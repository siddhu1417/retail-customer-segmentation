<<<<<<< HEAD
# Retail Customer Segmentation

A local full-stack application for uploading retail customer CSVs, exploring and clustering customers with K-Means, inspecting deterministic marketing suggestions, predicting a new customer's segment, and exporting run results. The included dataset is synthetic and intended only for demonstration.

## Features

- FastAPI backend with SQLite persistence for datasets, clustering runs, and customer results.
- React/Vite dashboard with dataset upload, feature selection, clustering, segment results, recommendations, customer lookup, and exports.
- StandardScaler + scikit-learn KMeans; optional silhouette-based K selection.
- CSV template and synthetic sample data.
- Isolated backend and frontend tests.

## Architecture

`frontend` communicates with `backend` over JSON/CSV HTTP APIs. The backend owns column normalization, validation, ML, recommendation rules, persistence, and exports. SQLite is created locally at `backend/data/retail.db`; uploaded files and serialized models are stored under `backend/storage`.

## Quick start

Requirements: Python 3.11+ and Node.js 20+.

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally http://localhost:5173). API docs are at http://localhost:8000/docs. For detailed setup, see [USER_MANUAL.md](USER_MANUAL.md).

## Screenshots

Screenshots can be added here after running the application.

## Tests

```powershell
cd backend
python -m pytest
cd ..\frontend
npm test
npm run build
```

See [TESTING.md](TESTING.md) for coverage and limitations.
=======
# retail-customer-segmentation
>>>>>>> origin/main
