import uuid
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile

from app.config import MAX_UPLOAD_BYTES, UPLOAD_DIR

DATASET_REGISTRY = {}
CSV_CONTENT_TYPES = {
    "",
    "text/csv",
    "text/plain",
    "application/csv",
    "application/vnd.ms-excel",
    "application/octet-stream",
}

SAMPLE_DATASETS = {
    "sales": pd.DataFrame(
        [
            {"month": "2026-01-01", "region": "North", "revenue": 42000, "orders": 720, "profit": 12000},
            {"month": "2026-02-01", "region": "South", "revenue": 46000, "orders": 760, "profit": 13500},
            {"month": "2026-03-01", "region": "West", "revenue": 51000, "orders": 840, "profit": 15100},
            {"month": "2026-04-01", "region": "East", "revenue": 56000, "orders": 900, "profit": 16800},
            {"month": "2026-05-01", "region": "North", "revenue": 61000, "orders": 980, "profit": 18500},
            {"month": "2026-06-01", "region": "West", "revenue": 69000, "orders": 1080, "profit": 21300},
        ]
    ),
    "customer-churn": pd.DataFrame(
        [
            {"segment": "Starter", "churn_rate": 18, "retention": 82, "age": 24, "spending": 120},
            {"segment": "Growth", "churn_rate": 12, "retention": 88, "age": 31, "spending": 260},
            {"segment": "Pro", "churn_rate": 8, "retention": 92, "age": 38, "spending": 410},
            {"segment": "Enterprise", "churn_rate": 5, "retention": 95, "age": 46, "spending": 680},
            {"segment": "Legacy", "churn_rate": 21, "retention": 79, "age": 52, "spending": 230},
        ]
    ),
    "marketing-campaigns": pd.DataFrame(
        [
            {"channel": "Email", "leads": 1240, "conversion_rate": 7.8, "spend": 9400, "revenue": 42000},
            {"channel": "Search", "leads": 1680, "conversion_rate": 9.4, "spend": 15300, "revenue": 69000},
            {"channel": "Social", "leads": 1420, "conversion_rate": 6.9, "spend": 12600, "revenue": 51000},
            {"channel": "Events", "leads": 620, "conversion_rate": 12.5, "spend": 18100, "revenue": 76000},
            {"channel": "Partners", "leads": 820, "conversion_rate": 10.2, "spend": 7800, "revenue": 58000},
        ]
    ),
}


def _safe_dataset_id() -> str:
    return str(uuid.uuid4())


def read_csv_robust(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(path, sep=None, engine="python", encoding=encoding)
        except UnicodeDecodeError:
            continue
        except pd.errors.ParserError as exc:
            raise HTTPException(status_code=400, detail=f"CSV parsing failed: {exc}") from exc
    raise HTTPException(status_code=400, detail="Unable to decode CSV. Try UTF-8 or Latin-1 encoding.")


async def save_upload(file: UploadFile) -> tuple[str, pd.DataFrame, dict]:
    original_name = Path(file.filename or "").name
    if not original_name.lower().endswith(".csv") or (file.content_type or "") not in CSV_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    dataset_id = _safe_dataset_id()
    target_path = UPLOAD_DIR / f"{dataset_id}.csv"
    size = 0
    with target_path.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                target_path.unlink(missing_ok=True)
                max_mb = round(MAX_UPLOAD_BYTES / (1024 * 1024))
                raise HTTPException(status_code=413, detail=f"CSV is too large. Maximum upload size is {max_mb} MB.")
            output.write(chunk)

    df = read_csv_robust(target_path)
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV contains no rows.")

    DATASET_REGISTRY[dataset_id] = {"path": str(target_path), "filename": original_name, "source": "upload"}
    return dataset_id, df, {"filename": original_name, "source": "upload"}


def register_sample(name: str) -> tuple[str, pd.DataFrame, dict]:
    key = name.lower()
    if key not in SAMPLE_DATASETS:
        raise HTTPException(status_code=404, detail="Sample dataset not found.")
    dataset_id = _safe_dataset_id()
    DATASET_REGISTRY[dataset_id] = {"sample": key, "filename": f"{key}.csv", "source": "sample"}
    return dataset_id, SAMPLE_DATASETS[key].copy(), {"filename": f"{key}.csv", "source": "sample"}


def get_dataset(dataset_id: str) -> pd.DataFrame:
    entry = DATASET_REGISTRY.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found. Upload or load a sample dataset again.")
    if entry.get("source") == "sample":
        return SAMPLE_DATASETS[entry["sample"]].copy()
    return read_csv_robust(Path(entry["path"]))


def get_dataset_metadata(dataset_id: str) -> dict:
    entry = DATASET_REGISTRY.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found. Upload or load a sample dataset again.")
    return {"filename": entry.get("filename", "dataset.csv"), "source": entry.get("source", "upload")}
