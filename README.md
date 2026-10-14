# Pocket Money Management System — Backend

A Python-based backend that processes UPI transaction statements and provides financial summaries through REST APIs.

## Features

- Upload and validate CSV transaction statements.
- Clean and normalize transaction data using Pandas.
- Classify transactions into spending categories.
- Return structured JSON responses for frontend integration.
- Generate weekly, monthly, and yearly transaction summaries.
- Handle invalid files with appropriate error responses.

## Tech Stack

- **Python** — Backend development
- **FastAPI** — REST API development
- **Pandas** — Data cleaning and analytics
- **Uvicorn** — ASGI server

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/hitmanp007/pocket_money_management_backend.git

```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn pandas python-multipart
```

### 4. Run the backend

```bash
python -m uvicorn app.main:app --app-dir backend --reload
```

The API will be available at:

`http://127.0.0.1:8000`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Check backend status |
| POST | `/api/v1/upload/csv` | Upload and process a CSV |
| GET | `/api/v1/transactions/cleaned` | Retrieve cleaned transactions |
| GET | `/api/v1/analytics/weekly` | Weekly summary |
| GET | `/api/v1/analytics/monthly` | Monthly summary |
| GET | `/api/v1/analytics/yearly` | Yearly summary |

Explore and test the APIs using FastAPI Swagger UI:

`http://127.0.0.1:8000/docs`

## Project Status

Hackathon prototype completed. The backend provides CSV processing, transaction normalization, and financial analytics APIs.

## Contributors

Developed as part of a hackathon project.
