import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ALIASES = {
    "customer_id": ["customer_id", "customerid", "id"],
    "annual_income": ["annual_income", "annual income (k$)", "income"],
    "spending_score": ["spending_score", "spending score (1-100)", "spending score"],
    "purchase_frequency": ["purchase_frequency", "purchase_frequency_per_month"],
    "average_purchase_value": ["average_purchase_value", "average_order_value"],
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.columns.duplicated().any():
        raise ValueError("CSV contains duplicate column names.")
    reverse = {alias.casefold().strip(): canonical for canonical, values in ALIASES.items() for alias in values}
    out = df.copy()
    out.columns = [reverse.get(str(c).casefold().strip(), str(c).strip()) for c in df.columns]
    if out.columns.duplicated().any():
        raise ValueError("Multiple CSV columns map to the same supported field.")
    if not {"annual_income", "spending_score"}.issubset(out.columns):
        raise ValueError("Required columns: annual_income and spending_score (or documented aliases).")
    return out

def prepare(df: pd.DataFrame, features: list[str]):
    df = normalize_columns(df)
    if not features or any(f not in df for f in features):
        raise ValueError("Select supported numeric features that exist in this dataset.")
    if "customer_id" in features:
        raise ValueError("Customer ID cannot be a clustering feature.")
    if not all(pd.api.types.is_numeric_dtype(df[f]) for f in features):
        raise ValueError("Selected features must be numeric.")
    vals = df[features].replace([np.inf, -np.inf], np.nan)
    valid = vals.notna().all(axis=1)
    clean = df.loc[valid].copy()
    if len(clean) < 2:
        raise ValueError("At least two valid customer rows are required.")
    return df, clean, int((~valid).sum())

def choose_k(x, seed=42):
    if len(x) < 3:
        raise ValueError("Automatic selection needs at least three valid customers.")
    scores = []
    for k in range(2, min(10, len(x)-1)+1):
        model = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(x)
        score = float(silhouette_score(x, model.labels_)) if len(set(model.labels_)) > 1 else -1
        scores.append({"k": k, "inertia": float(model.inertia_), "silhouette": score})
    return max(scores, key=lambda row: row["silhouette"])["k"], scores

def fit(df, features, k, seed=42, automatic=False):
    original, clean, excluded = prepare(df, features)
    if automatic:
        k, curve = choose_k(clean[features].to_numpy(), seed)
    else:
        curve = []
    if not 2 <= k < len(clean):
        raise ValueError(f"K must be between 2 and valid customer count minus one ({len(clean)-1}).")
    scaler = StandardScaler()
    x = scaler.fit_transform(clean[features])
    model = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(x)
    silhouette = float(silhouette_score(x, model.labels_)) if 1 < len(set(model.labels_)) < len(x) else None
    clean["cluster"] = model.labels_.astype(int)
    return original, clean, scaler, model, excluded, silhouette, curve

def summary(clean, features):
    summaries = []
    median_income = float(clean["annual_income"].median()) if "annual_income" in clean else 0
    median_spend = float(clean["spending_score"].median()) if "spending_score" in clean else 0
    for cluster, group in clean.groupby("cluster"):
        income = float(group["annual_income"].mean()) if "annual_income" in group else median_income
        spend = float(group["spending_score"].mean()) if "spending_score" in group else median_spend
        summaries.append({"cluster": int(cluster), "count": len(group), "means": {f: float(group[f].mean()) for f in features},
          "label": f"{'High' if income >= median_income else 'Low'} Income, {'High' if spend >= median_spend else 'Low'} Spending",
          "recommendation": recommendation(income >= median_income, spend >= median_spend)})
    return summaries

def recommendation(high_income, high_spend):
    if high_income and high_spend: return "Consider premium offers and VIP loyalty programs."
    if high_income: return "Try personalized promotions and product discovery campaigns."
    if high_spend: return "Consider loyalty benefits and relevant value bundles."
    return "Consider affordable offers and budget-friendly products."
