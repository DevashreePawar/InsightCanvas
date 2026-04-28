from fastapi import APIRouter, Depends

from app.schemas import ChartRequest, QuestionRequest
from app.services.agent_service import analyze_dataset_question, interpret_dataset_question
from app.services.rag_service import retrieve_dataset_context
from app.services.security import current_user
from app.services.session_service import save_session

router = APIRouter(tags=["analysis"])


@router.post("/interpret")
def interpret(payload: QuestionRequest, user=Depends(current_user)):
    return interpret_dataset_question(payload.dataset_id, payload.question)


@router.post("/recommend")
def recommend(payload: QuestionRequest, user=Depends(current_user)):
    return interpret_dataset_question(payload.dataset_id, payload.question)


@router.post("/rag/search")
def rag_search(payload: QuestionRequest, user=Depends(current_user)):
    return {"context": retrieve_dataset_context(payload.dataset_id, payload.question)}


@router.post("/charts/generate")
def generate(payload: ChartRequest, user=Depends(current_user)):
    result = analyze_dataset_question(payload.dataset_id, payload.question)
    if payload.save_session:
        saved = save_session(
            user["id"],
            {
                "title": payload.title or payload.question[:80],
                "dataset_metadata": result["profile"],
                "question": payload.question,
                "chart_type": result["chart_type"],
                "chart_config": result["chart_json"],
                "insight": result["insight"],
            },
        )
        result["saved_session"] = saved
    return result
