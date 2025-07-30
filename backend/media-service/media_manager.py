import asyncio
from fastapi import UploadFile, WebSocket
from typing import Dict, List
import aiofiles
import os
import uuid
from .schemas import ChunkedUploadInit, ChunkedUploadStatus, MediaFile, MediaMetadata

class MediaManager:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        self.active_uploads: Dict[str, ChunkedUploadStatus] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}

    async def initialize_upload(self, upload_init: ChunkedUploadInit) -> ChunkedUploadStatus:
        upload_id = str(uuid.uuid4())
        status = ChunkedUploadStatus(
            upload_id=upload_id,
            filename=upload_init.filename,
            chunks_received=[],
            total_chunks=upload_init.total_chunks,
            status='pending'
        )
        self.active_uploads[upload_id] = status
        return status

    async def process_chunk(self, upload_id: str, chunk_number: int, chunk_data: UploadFile) -> ChunkedUploadStatus:
        if upload_id not in self.active_uploads:
            raise ValueError("Upload ID not found")

        status = self.active_uploads[upload_id]
        chunk_dir = os.path.join(self.upload_dir, upload_id)
        os.makedirs(chunk_dir, exist_ok=True)

        chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_number}")
        async with aiofiles.open(chunk_path, 'wb') as f:
            content = await chunk_data.read()
            await f.write(content)

        status.chunks_received.append(chunk_number)
        await self._notify_progress(upload_id)

        if len(status.chunks_received) == status.total_chunks:
            await self._combine_chunks(upload_id)

        return status

    async def _combine_chunks(self, upload_id: str):
        status = self.active_uploads[upload_id]
        status.status = 'processing'
        await self._notify_progress(upload_id)

        chunk_dir = os.path.join(self.upload_dir, upload_id)
        output_path = os.path.join(self.upload_dir, status.filename)

        async with aiofiles.open(output_path, 'wb') as outfile:
            for i in range(status.total_chunks):
                chunk_path = os.path.join(chunk_dir, f"chunk_{i}")
                async with aiofiles.open(chunk_path, 'rb') as infile:
                    await outfile.write(await infile.read())

        # Cleanup chunks
        for i in range(status.total_chunks):
            os.remove(os.path.join(chunk_dir, f"chunk_{i}"))
        os.rmdir(chunk_dir)

        status.status = 'completed'
        await self._notify_progress(upload_id)

    async def _notify_progress(self, upload_id: str):
        if upload_id in self.websocket_connections:
            status = self.active_uploads[upload_id]
            ws = self.websocket_connections[upload_id]
            try:
                await ws.send_json({
                    'type': 'upload_progress',
                    'data': {
                        'upload_id': upload_id,
                        'progress': len(status.chunks_received) / status.total_chunks * 100,
                        'status': status.status
                    }
                })
            except:
                pass  # Handle WebSocket errors

    async def register_websocket(self, upload_id: str, websocket: WebSocket):
        self.websocket_connections[upload_id] = websocket
