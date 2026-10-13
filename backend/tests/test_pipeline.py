import pandas as pd
import pytest
from app.pipeline import fit, normalize_columns

def test_aliases_and_valid_clustering():
    df = pd.DataFrame({'CustomerID': range(1, 13), 'Annual Income (k$)': [20,22,25,27,40,42,45,47,70,72,75,77], 'Spending Score (1-100)': [20,22,25,27,40,42,45,47,70,72,75,77]})
    original, clean, scaler, model, excluded, score, curve = fit(df, ['annual_income', 'spending_score'], 3)
    assert len(clean) == 12 and model.n_clusters == 3 and excluded == 0
    assert score is not None

def test_invalid_k_and_missing_fields():
    df = pd.DataFrame({'income': [1,2,3], 'spending score': [2,3,4]})
    with pytest.raises(ValueError): fit(df, ['annual_income', 'spending_score'], 4)
    with pytest.raises(ValueError): normalize_columns(pd.DataFrame({'other': [1]}))
