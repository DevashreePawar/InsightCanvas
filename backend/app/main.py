import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGIN
from app.database import init_db
from app.routes import analysis, analytics, auth, charts, datasets, reports, sessions

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Auto Visualization AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api")
app.include_router(datasets.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(charts.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
