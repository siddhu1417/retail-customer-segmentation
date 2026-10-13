# User Manual

## 1. Introduction and objective

Retail Customer Segmentation groups customers with similar numerical purchase behavior using K-means. It helps explore customer patterns and suggests rule-based campaign ideas. These suggestions are not predictions of intent or guaranteed business outcomes.

## 2. Features and limitations

Upload and validate CSV data, choose numeric features, fit K-means, review cluster statistics and charts, get median-based marketing suggestions, assign a new customer to a saved cluster, and export customer/summary CSVs. SQLite stores local runs. K-means depends on selected features, outliers, scaling, and K; labels and cluster numbers are descriptive only. No PDF report or authentication is included.

## 3. Technology stack

React, Vite, React Router, Recharts, Axios; FastAPI, Pydantic, Pandas, NumPy, scikit-learn; SQLAlchemy and SQLite.

## 4. Hardware and software requirements

A modern Windows/macOS/Linux computer, Python 3.11 or later, Node.js 20 or later, and a current browser. Network access is needed for first-time package installation.

## 5. Project folder structure

```text
retail-customer-segmentation/
├── backend/app/          # API, persistence, ML pipeline
├── backend/tests/        # pytest tests
├── frontend/src/         # React application and UI styles
├── data/                 # synthetic example CSV
├── README.md
├── USER_MANUAL.md
└── TESTING.md
```

## 6–7. Install prerequisites and open in VS Code

Install Python from python.org and Node.js LTS from nodejs.org. In VS Code choose **File → Open Folder** and select `retail-customer-segmentation`. Use two integrated terminals, one for backend and one for frontend.

## 8. Create and activate a virtual environment

Windows PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

## 9. Install backend dependencies

```bash
python -m pip install -r requirements.txt
```

## 10. Install frontend dependencies

In another terminal from the project root:

```bash
cd frontend
npm install
```

## 11. Configure environment variables

Optional examples are in `backend/.env.example` and `frontend/.env.example`. The backend reads `DATABASE_URL`, `STORAGE_DIR`, and `CORS_ORIGINS` from the process environment. The frontend reads `VITE_API_URL` at build/start time. Defaults work for local development; set variables in your shell before starting processes.

## 12. Initialize the database

SQLAlchemy creates the SQLite tables automatically when the API starts. The default database is `backend/data/retail.db`; no separate database service is required.

## 13. Start the backend server

From `backend` with the virtual environment active:

```bash
uvicorn app.main:app --reload
```

## 14. Start the frontend server

From `frontend`:

```bash
npm run dev
```

## 15. Verify the connection

Open `http://localhost:5173`. The Overview page loads live dashboard data. Check backend health directly at `http://localhost:8000/api/health` and API documentation at `http://localhost:8000/docs`.

## 16. Upload a CSV

Open **Datasets**, choose a `.csv`, and select **Upload and validate**. Review the preview, columns, row count, and missing-value counts. The file must include required income and spending fields.

## 17. Supported column names and CSV format

Canonical headers are `customer_id`, `annual_income`, `spending_score`, `purchase_frequency`, and `average_purchase_value`. Recognized aliases include `CustomerID`, `ID`, `Annual Income (k$)`, `income`, `Spending Score (1-100)`, `spending score`, `purchase_frequency_per_month`, and `average_order_value`. The bundled `data/sample_customers.csv` contains 110 synthetic records. IDs are retained for reports but cannot be a feature. Unsupported headers are not guessed.

## 18. Choose features and K

Select at least two existing numeric features; income and spending score are required by the dataset validator. Choose K from 2 through valid row count minus one, or choose automatic selection. Automatic mode compares silhouette scores across candidate K and returns the highest score; inertia is included for context. Neither metric guarantees an optimal business segmentation.

## 19. Run clustering and understand results

Press **Start clustering**. The backend excludes rows with missing/non-finite selected features, reports the count, standardizes selected features, fits K-means, and saves results/model metadata. The results page shows cluster sizes, feature means, metrics, and customer assignments.

## 20. Interpret charts and labels

Cluster IDs are arbitrary and may change when the data or seed changes. Relative High/Low income and spending labels compare cluster averages to the uploaded dataset medians. Scatter plot axes use original values. Silhouette ranges from -1 to 1 when defined; larger values generally indicate better separation under the selected features. Inertia measures within-cluster squared distances and usually declines as K grows.

## 21. Marketing recommendations

Suggestions use the combination of income and spending relative to their dataset medians: high/high premium or VIP ideas; high/low product discovery; low/high relevant value bundles; low/low affordable offers. Validate ideas with business context and experiments; the app does not establish causation or promise sales growth.

## 22. Predict a new customer's cluster

Open **Customer lookup** after a successful run. Enter all selected feature values in their original units. The saved StandardScaler and fitted K-means model assign the closest existing cluster. The API requires a saved run.

## 23. Export results

Use the buttons on the Segments page to download assigned customers or a cluster summary as CSV. The exports are generated from persisted run results.

## 24. Inspect the database

The SQLite file is `backend/data/retail.db`. Open it read-only with a SQLite viewer such as the VS Code SQLite extension. Tables are `datasets`, `runs`, and `results`.

## 25. Troubleshooting

- **API unavailable:** confirm Uvicorn is running on port 8000.
- **CORS error:** include the frontend origin in `CORS_ORIGINS` and restart backend.
- **CSV rejected:** check UTF-8 CSV format, headers, and duplicate columns.
- **K rejected:** use K between 2 and valid customer count minus one.
- **Automatic K unavailable:** datasets need enough usable rows to compare at least two K values.
- **PowerShell activation blocked:** run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate the venv.

## 26. Run automated tests

Backend: from `backend`, activate the environment, then `python -m pytest`. Frontend: from `frontend`, run `npm test`; production bundle: `npm run build`. See `TESTING.md` for scope. Tests/build were not run during project generation.

## 27. Reset demo data safely

Stop both servers first. Back up any data you need. To reset the local demo, remove `backend/data/retail.db` and files inside `backend/storage`, then restart the API. This permanently removes local uploads and runs. Do not remove these when they contain records you need.

## 28. Privacy and data handling

This starter runs locally and does not implement user accounts or access control. Uploaded CSVs and models remain in backend storage. Upload only data you are authorized to process; avoid unnecessary direct identifiers and protect the project folder and backups.

## 29. Limitations and future improvements

Current limits include local single-user deployment, CSV-only input, no PDF report, and minimal automated coverage. Future work could add authentication, role-based access, stronger isolated test fixtures, model/run comparison, robust outlier review, pagination on the server, and PDF reporting.
