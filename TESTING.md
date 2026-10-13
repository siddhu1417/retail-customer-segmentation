# Testing

## Backend

From `backend`, activate the virtual environment, install `requirements.txt`, then run `python -m pytest`. The tests cover the health route, CSV format rejection, dashboard response shape, supported header aliases, clustering, and invalid K/required-column handling.

The API tests use the default local database configuration in this starter project. For a separate test database, set `DATABASE_URL` to a temporary SQLite file before starting pytest. Do not point tests at business data.

## Frontend

From `frontend`, run `npm install` followed by `npm test`. The smoke test checks that the main app shell renders. `npm run build` creates the production bundle in `dist`.

## Flow to verify manually

1. Start the backend and frontend as documented in `USER_MANUAL.md`.
2. Upload `data/sample_customers.csv`.
3. Run clustering with income and spending and K=5.
4. Review distribution, scatter plot, segment suggestions, and assigned customer table.
5. Use customer lookup with the run's two selected features.
6. Download both CSV exports.

Tests and production build were not executed while authoring these files; run the commands above in an environment with dependencies installed.
