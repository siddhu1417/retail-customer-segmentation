import json, os, uuid
from pathlib import Path
from io import BytesIO, StringIO
import joblib
import pandas as pd
from fastapi import FastAPI, Depends, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Dataset, Run, Result
from .pipeline import normalize_columns, fit, summary

Base.metadata.create_all(bind=engine)
ROOT = Path(__file__).resolve().parents[1]
STORAGE = Path(os.getenv("STORAGE_DIR", ROOT / "storage")); STORAGE.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="Retail Customer Segmentation API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","), allow_methods=["*"], allow_headers=["*"])

class ClusterRequest(BaseModel):
    dataset_id: int
    features: list[str] = Field(min_length=2)
    k: int = 5
    seed: int = 42
    automatic: bool = False

class PredictRequest(BaseModel):
    values: dict[str, float]

@app.get("/api/health")
def health(): return {"status": "ok"}

@app.post("/api/datasets")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"): raise HTTPException(400, "Upload a .csv file.")
    try:
        raw = await file.read()
        if not raw: raise ValueError("CSV is empty.")
        frame = normalize_columns(pd.read_csv(BytesIO(raw)))
    except Exception as exc: raise HTTPException(400, str(exc)) from exc
    path = STORAGE / f"dataset-{uuid.uuid4().hex}.csv"; path.write_bytes(raw)
    item = Dataset(name=file.filename, path=str(path), row_count=len(frame), columns=json.dumps(list(frame.columns)))
    db.add(item); db.commit(); db.refresh(item)
    preview = frame.head(10).astype(object).where(pd.notna(frame.head(10)), None)
    return {"id": item.id, "name": item.name, "row_count": item.row_count, "columns": json.loads(item.columns), "preview": preview.to_dict("records"), "missing": frame.isna().sum().to_dict()}

@app.get("/api/datasets")
def datasets(db: Session = Depends(get_db)):
    return [{"id": d.id, "name": d.name, "row_count": d.row_count, "columns": json.loads(d.columns), "created_at": d.created_at.isoformat()} for d in db.query(Dataset).order_by(Dataset.id.desc()).all()]

@app.get("/api/template.csv")
def template():
    data = "customer_id,annual_income,spending_score,purchase_frequency,average_purchase_value\nC001,55,72,8,48\nC002,28,31,3,22\n"
    return StreamingResponse(iter([data]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=customer_template.csv"})

@app.post("/api/runs")
def cluster(req: ClusterRequest, db: Session = Depends(get_db)):
    dataset = db.get(Dataset, req.dataset_id)
    if not dataset: raise HTTPException(404, "Dataset not found.")
    try:
        df = pd.read_csv(dataset.path)
        original, clean, scaler, model, excluded, score, curve = fit(df, req.features, req.k, req.seed, req.automatic)
    except Exception as exc: raise HTTPException(400, str(exc)) from exc
    model_path = STORAGE / f"model-{uuid.uuid4().hex}.joblib"; joblib.dump({"scaler": scaler, "model": model, "features": req.features}, model_path)
    run = Run(dataset_id=dataset.id, k=model.n_clusters, features=json.dumps(req.features), seed=req.seed, inertia=float(model.inertia_), silhouette=score, model_path=str(model_path))
    db.add(run); db.flush()
    for index, row in clean.iterrows():
        data = row.drop(labels=["cluster"]).to_dict()
        for key, value in data.items():
            if pd.isna(value): data[key] = None
            elif hasattr(value, "item"): data[key] = value.item()
        cid = str(data.get("customer_id", index))
        db.add(Result(run_id=run.id, customer_id=cid, record=json.dumps(data), cluster=int(row["cluster"])))
    db.commit(); db.refresh(run)
    return {"run_id": run.id, "k": run.k, "features": req.features, "inertia": run.inertia, "silhouette": score, "excluded_rows": excluded, "curve": curve, "summary": summary(clean, req.features), "customers": [{**json.loads(r.record), "cluster": r.cluster} for r in db.query(Result).filter_by(run_id=run.id).all()]}

@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    runs = db.query(Run).order_by(Run.id.desc()).limit(5).all()
    if not runs: return {"customers": 0, "clusters": 0, "average_income": None, "average_spending": None, "distribution": [], "recent_runs": []}
    latest = runs[0]; rows = db.query(Result).filter_by(run_id=latest.id).all()
    records = [json.loads(r.record) for r in rows]
    return {"customers": len(rows), "clusters": latest.k, "average_income": round(sum(r["annual_income"] for r in records if r.get("annual_income") is not None)/max(1, sum(r.get("annual_income") is not None for r in records)), 2), "average_spending": round(sum(r["spending_score"] for r in records if r.get("spending_score") is not None)/max(1, sum(r.get("spending_score") is not None for r in records)), 2), "distribution": [{"cluster": c, "count": sum(r.cluster == c for r in rows)} for c in sorted(set(r.cluster for r in rows))], "recent_runs": [{"id": r.id, "k": r.k, "created_at": r.created_at.isoformat()} for r in runs]}

@app.get("/api/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run: raise HTTPException(404, "Run not found.")
    rows = db.query(Result).filter_by(run_id=run.id).all(); frame = pd.DataFrame([{**json.loads(r.record), "cluster": r.cluster} for r in rows])
    return {"run_id": run.id, "k": run.k, "features": json.loads(run.features), "inertia": run.inertia, "silhouette": run.silhouette, "customers": frame.where(pd.notna(frame), None).to_dict("records"), "summary": summary(frame, json.loads(run.features))}

@app.post("/api/runs/{run_id}/predict")
def predict(run_id: int, req: PredictRequest, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run: raise HTTPException(404, "Run not found. Run clustering first.")
    saved = joblib.load(run.model_path); features = saved["features"]
    if set(features) - req.values.keys(): raise HTTPException(400, f"Provide values for: {', '.join(features)}")
    try: cluster_id = int(saved["model"].predict(saved["scaler"].transform([[req.values[f] for f in features]]))[0])
    except Exception as exc: raise HTTPException(400, str(exc)) from exc
    return {"cluster": cluster_id, "features": features}

@app.get("/api/runs/{run_id}/customers.csv")
def export_customers(run_id: int, db: Session = Depends(get_db)):
    rows = db.query(Result).filter_by(run_id=run_id).all()
    if not rows: raise HTTPException(404, "Run has no saved customers.")
    frame = pd.DataFrame([{**json.loads(r.record), "cluster": r.cluster} for r in rows]); return StreamingResponse(iter([frame.to_csv(index=False)]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=run-{run_id}-customers.csv"})

@app.get("/api/runs/{run_id}/summary.csv")
def export_summary(run_id: int, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run: raise HTTPException(404, "Run not found.")
    rows = db.query(Result).filter_by(run_id=run_id).all(); frame = pd.DataFrame([{**json.loads(r.record), "cluster": r.cluster} for r in rows])
    data = pd.DataFrame(summary(frame, json.loads(run.features))).to_csv(index=False)
    return StreamingResponse(iter([data]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=run-{run_id}-summary.csv"})
