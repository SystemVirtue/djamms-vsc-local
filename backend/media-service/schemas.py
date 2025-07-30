from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MediaMetadata(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: Optional[float] = None
    mime_type: str
    file_size: int
    tags: List[str] = []

class ChunkedUploadInit(BaseModel):
    filename: str
    total_size: int
    mime_type: str
    total_chunks: int

class ChunkedUploadStatus(BaseModel):
    upload_id: str
    filename: str
    chunks_received: List[int]
    total_chunks: int
    status: str  # 'pending', 'processing', 'completed', 'failed'

class MediaFile(BaseModel):
    id: int
    metadata: MediaMetadata
    file_path: str
    created_at: datetime
    updated_at: datetime
    status: str  # 'active', 'processing', 'error'
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
