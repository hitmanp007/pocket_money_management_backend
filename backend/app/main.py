
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import transactions, analytics, upload
from .api.routes import health

app = FastAPI(
    title="Pocket Money Management API",
    description="Backend API for UPI transaction tracking and analytics",
    version="1.0.0",
)

# Change this to Prem's actual frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Pocket Money Management API",
        "docs": "/docs",
    }


app.include_router(health.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
# app.include_router(analytics.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")