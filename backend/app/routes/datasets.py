import logging

from fastapi import APIRouter, Depends, File, UploadFile

from app.schemas import QuestionRequest
from app.services.csv_service import get_dataset, register_sample, save_upload
from app.services.ai_service import mock_suggest_questions, suggest_questions
from app.services.profile_service import profile_dataset
from app.services.rag_service import index_dataset_context
from app.services.security import current_user

router = APIRouter(prefix="/datasets", tags=["datasets"])
logger = logging.getLogger(__name__)


def safe_suggest_questions(profile: dict) -> list[str]:
    try:
        return suggest_questions(profile)
    except Exception as exc:
        logger.warning("Question suggestion generation failed; returning fallback suggestions: %s", exc)
        return mock_suggest_questions(profile)


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), user=Depends(current_user)):
    dataset_id, df, metadata = await save_upload(file)
    profile = profile_dataset(df, metadata)
    index_dataset_context(dataset_id, profile)
    return {"dataset_id": dataset_id, "metadata": metadata, "profile": profile, "suggested_questions": safe_suggest_questions(profile)}


@router.post("/sample/{name}")
def use_sample_dataset(name: str, user=Depends(current_user)):
    dataset_id, df, metadata = register_sample(name)
    profile = profile_dataset(df, metadata)
    index_dataset_context(dataset_id, profile)
    return {"dataset_id": dataset_id, "metadata": metadata, "profile": profile, "suggested_questions": safe_suggest_questions(profile)}


@router.post("/profile")
def profile_existing_dataset(payload: QuestionRequest, user=Depends(current_user)):
    df = get_dataset(payload.dataset_id)
    return {"dataset_id": payload.dataset_id, "profile": profile_dataset(df)}
