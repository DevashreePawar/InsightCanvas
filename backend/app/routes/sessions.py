from fastapi import APIRouter, Depends

from app.schemas import SaveSessionRequest
from app.services.security import current_user
from app.services.session_service import delete_session, get_session, get_shared_session, list_sessions, save_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("")
def index(user=Depends(current_user)):
    return list_sessions(user["id"])


@router.post("")
def create(payload: SaveSessionRequest, user=Depends(current_user)):
    return save_session(user["id"], payload.model_dump())


@router.get("/shared/{share_id}/public")
def shared(share_id: str):
    return get_shared_session(share_id)


@router.get("/{session_id}")
def show(session_id: str, user=Depends(current_user)):
    return get_session(user["id"], session_id)


@router.delete("/{session_id}")
def destroy(session_id: str, user=Depends(current_user)):
    return delete_session(user["id"], session_id)
