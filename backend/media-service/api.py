from fastapi import APIRouter, Depends, UploadFile, WebSocket, HTTPException
from typing import List
from .media_manager import MediaManager
from .schemas import ChunkedUploadInit, ChunkedUploadStatus, MediaFile
from ..infrastructure.database import SessionLocal
from ..infrastructure.models import MediaTrack
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
media_manager = MediaManager(upload_dir="uploads")

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

@router.post("/media/upload/init")
async def initialize_upload(
    upload_init: ChunkedUploadInit,
    db: AsyncSession = Depends(get_db)
) -> ChunkedUploadStatus:
    return await media_manager.initialize_upload(upload_init)

@router.post("/media/upload/{upload_id}/chunk/{chunk_number}")
async def upload_chunk(
    upload_id: str,
    chunk_number: int,
    file: UploadFile,
    db: AsyncSession = Depends(get_db)
) -> ChunkedUploadStatus:
    try:
        return await media_manager.process_chunk(upload_id, chunk_number, file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/media/upload/{upload_id}/ws")
async def upload_websocket(upload_id: str, websocket: WebSocket):
    await websocket.accept()
    await media_manager.register_websocket(upload_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        pass  # Handle disconnection

@router.get("/media/search")
async def search_media(
    query: str = "",
    page: int = 1,
    limit: int = 50,
    sort_by: str = "created_at",
    filters: dict = None,
    db: AsyncSession = Depends(get_db)
) -> List[MediaFile]:
    # Implement search logic here
    pass

@router.delete("/media/{media_id}")
async def delete_media(
    media_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Implement delete logic here
    pass
