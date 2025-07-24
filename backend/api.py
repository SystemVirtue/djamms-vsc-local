from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.infrastructure.database import SessionLocal
from backend.infrastructure.models import Track, DigitalSignageContent, DigitalSignageSchedule
from pydantic import BaseModel

router = APIRouter()

# --- Video Output State, Schemas, and Endpoints (after all dependencies) ---

class VideoOutputSettings(BaseModel):
    resolution: str = "1920x1080"
    quality: str = "high"
    frame_rate: int = 30
    bitrate: int = 5000
    format: str = "mp4"
    brightness: int = 100
    contrast: int = 100
    saturation: int = 100
    hue: int = 0
    zoom: int = 100
    rotation: int = 0
    audio_enabled: bool = True
    show_overlay: bool = True
    overlay_text: str = "DJAMMS Live Stream"

class VideoOutputState(BaseModel):
    is_live: bool = False
    is_recording: bool = False
    recording_time: int = 0
    settings: VideoOutputSettings = VideoOutputSettings()

video_output_state = VideoOutputState()

# --- Pydantic Schemas for Video Output ---
# class VideoOutputSettings(BaseModel):
#     resolution: str = "1920x1080"
#     quality: str = "high"
#     frame_rate: int = 30
#     bitrate: int = 5000
#     format: str = "mp4"
#     brightness: int = 100
#     contrast: int = 100
#     saturation: int = 100
#     hue: int = 0
#     zoom: int = 100
#     rotation: int = 0
#     audio_enabled: bool = True
#     show_overlay: bool = True
#     overlay_text: str = "DJAMMS Live Stream"

# class VideoOutputState(BaseModel):
#     is_live: bool = False
#     is_recording: bool = False
#     recording_time: int = 0
#     settings: VideoOutputSettings = VideoOutputSettings()

# --- In-memory state for demonstration (replace with DB/Redis for production) ---
# video_output_state = VideoOutputState()

# --- Video Output Endpoints ---
# (Moved below router/require_role definitions)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.infrastructure.database import SessionLocal
from backend.infrastructure.models import Track, DigitalSignageContent, DigitalSignageSchedule
from pydantic import BaseModel

def get_current_user_role(request: Request):
    # Placeholder: Extract user role from JWT or session (to be replaced with real JWT logic)
    # Example: return request.state.user_role
    # For now, default to 'admin' for demonstration
    return "admin"

def require_role(required_roles):
    def dependency(role=Depends(get_current_user_role)):
        if role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    return dependency

router = APIRouter()

# --- Pydantic Schemas ---
class TrackOut(BaseModel):
    id: str
    title: str
    artist: Optional[str]
    album: Optional[str]
    duration: Optional[int]
    bpm: Optional[int]
    genre: Optional[str]
    storage_url: str
    artwork_url: Optional[str]
    uploaded_by: Optional[str]
    is_public: bool
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

class TrackCreate(BaseModel):
    title: str
    artist: Optional[str]
    album: Optional[str]
    duration: Optional[int]
    bpm: Optional[int]
    genre: Optional[str]
    storage_url: str
    artwork_url: Optional[str]
    uploaded_by: Optional[str]
    is_public: Optional[bool] = True


# --- Pydantic Schemas for Digital Signage ---
class DigitalSignageContentOut(BaseModel):
    id: str
    filename: str
    content_type: str
    url: str
    uploaded_by: Optional[str]
    uploaded_at: Optional[str]
    is_active: bool
    class Config:
        orm_mode = True

class DigitalSignageContentCreate(BaseModel):
    filename: str
    content_type: str
    url: str
    uploaded_by: Optional[str]
    is_active: Optional[bool] = True

class DigitalSignageScheduleOut(BaseModel):
    id: str
    content_id: str
    start_time: str
    end_time: str
    repeat_pattern: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    class Config:
        orm_mode = True

class DigitalSignageScheduleCreate(BaseModel):
    content_id: str
    start_time: str
    end_time: str
    repeat_pattern: Optional[str]

# --- Digital Signage Endpoints ---
@router.post("/signage/upload", response_model=DigitalSignageContentOut, dependencies=[Depends(require_role(["admin", "moderator"]))])
async def signage_upload(payload: DigitalSignageContentCreate, db: AsyncSession = Depends(SessionLocal)):
    signage = DigitalSignageContent(
        filename=payload.filename,
        content_type=payload.content_type,
        url=payload.url,
        uploaded_by=payload.uploaded_by,
        is_active=payload.is_active if payload.is_active is not None else True
    )
    db.add(signage)
    await db.commit()
    await db.refresh(signage)
    return signage


@router.delete("/signage/content/{content_id}", dependencies=[Depends(require_role(["admin"]))])
async def signage_delete_content(content_id: str, db: AsyncSession = Depends(SessionLocal)):
    signage = await db.get(DigitalSignageContent, content_id)
    if not signage:
        raise HTTPException(status_code=404, detail="Signage content not found")
    await db.delete(signage)
    await db.commit()
    return {"message": "Signage content deleted"}

@router.post("/signage/schedule", response_model=DigitalSignageScheduleOut, dependencies=[Depends(require_role(["admin", "moderator"]))])
async def signage_schedule(payload: DigitalSignageScheduleCreate, db: AsyncSession = Depends(SessionLocal)):
    schedule = DigitalSignageSchedule(
        content_id=payload.content_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        repeat_pattern=payload.repeat_pattern
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule



# --- Digital Signage ---
# (Moved below router/require_role definitions)

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.infrastructure.database import SessionLocal
from backend.infrastructure.models import Track
from pydantic import BaseModel


def get_current_user_role(request: Request):
    # Placeholder: Extract user role from JWT or session (to be replaced with real JWT logic)
    # Example: return request.state.user_role
    # For now, default to 'admin' for demonstration
    return "admin"

def require_role(required_roles):
    def dependency(role=Depends(get_current_user_role)):
        if role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    return dependency

router = APIRouter()

# --- Pydantic Schemas ---
class TrackOut(BaseModel):
    id: str
    title: str
    artist: Optional[str]
    album: Optional[str]
    duration: Optional[int]
    bpm: Optional[int]
    genre: Optional[str]
    storage_url: str
    artwork_url: Optional[str]
    uploaded_by: Optional[str]
    is_public: bool
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

class TrackCreate(BaseModel):
    title: str
    artist: Optional[str]
    album: Optional[str]
    duration: Optional[int]
    bpm: Optional[int]
    genre: Optional[str]
    storage_url: str
    artwork_url: Optional[str]
    uploaded_by: Optional[str]
    is_public: Optional[bool] = True

# --- Tracks ---
@router.get("/tracks", response_model=List[TrackOut])
async def list_tracks(db: AsyncSession = Depends(SessionLocal)):
    result = await db.execute(select(Track))
    tracks = result.scalars().all()
    return tracks

@router.post("/tracks", response_model=TrackOut, dependencies=[Depends(require_role(["admin", "moderator"]))])
async def upload_track(track: TrackCreate, db: AsyncSession = Depends(SessionLocal)):
    db_track = Track(**track.dict())
    db.add(db_track)
    await db.commit()
    await db.refresh(db_track)
    return db_track

@router.get("/tracks/{id}", response_model=TrackOut)
async def get_track(id: str, db: AsyncSession = Depends(SessionLocal)):
    result = await db.execute(select(Track).where(Track.id == id))
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


# --- Pydantic Schemas for Queue ---
from sqlalchemy import select as sa_select
from sqlalchemy import desc as sa_desc
from backend.infrastructure.models import Track
from pydantic import BaseModel
from typing import Optional

class QueueItem(BaseModel):
    track_id: str
    position: int

class QueueAdd(BaseModel):
    track_id: str

# For demonstration, use a simple in-memory queue (replace with DB-backed model for production)
queue: list[QueueItem] = []

@router.get("/queue", response_model=list[QueueItem])
async def get_queue():
    return queue

@router.post("/queue", dependencies=[Depends(require_role(["admin", "moderator", "user"]))])
async def add_to_queue(item: QueueAdd):
    position = len(queue) + 1
    queue.append(QueueItem(track_id=item.track_id, position=position))
    return {"message": "Track added to queue"}

@router.delete("/queue/{track_id}", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def remove_from_queue(track_id: str):
    global queue
    queue = [item for item in queue if item.track_id != track_id]
    return {"message": "Track removed from queue"}

# --- Voting & Favorites ---
@router.post("/queue/{track_id}/vote")
async def vote_track(track_id: str, up: bool = True):
    # TODO: Register vote
    return {"message": "Vote registered"}

@router.post("/tracks/{track_id}/favorite")
async def favorite_track(track_id: str):
    # TODO: Add to favorites
    return {"message": "Track favorited"}


# --- Playback State (in-memory for demonstration) ---
from pydantic import BaseModel
from typing import Optional

class PlaybackState(BaseModel):
    state: str = "stopped"  # playing, paused, stopped
    current_track_id: Optional[str] = None
    position: float = 0.0
    repeat_mode: str = "off"  # off, one, all
    shuffle: bool = False

playback_state = PlaybackState()

@router.get("/playback", response_model=PlaybackState)
async def get_playback_state():
    return playback_state

@router.post("/playback/play")
async def play():
    playback_state.state = "playing"
    return {"message": "Playback started"}

@router.post("/playback/pause")
async def pause():
    playback_state.state = "paused"
    return {"message": "Playback paused"}

@router.post("/playback/seek")
async def seek(position: float):
    playback_state.position = position
    return {"message": f"Seeked to {position}"}

@router.post("/playback/shuffle")
async def shuffle():
    playback_state.shuffle = not playback_state.shuffle
    return {"message": f"Shuffle set to {playback_state.shuffle}"}

@router.post("/playback/repeat")
async def repeat(mode: str):
    playback_state.repeat_mode = mode
    return {"message": f"Repeat mode set to {mode}"}

# --- WebSocket for Real-Time Player Sync ---
@router.websocket("/ws/player")
async def player_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # TODO: Handle real-time player events
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass


# --- Pydantic Schemas for Playlists ---
from backend.infrastructure.models import Playlist, PlaylistTrack

class PlaylistOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: Optional[str]
    is_public: bool
    artwork_url: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str]
    owner_id: Optional[str]
    is_public: Optional[bool] = True
    artwork_url: Optional[str]

class PlaylistUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_public: Optional[bool]
    artwork_url: Optional[str]

class PlaylistTrackAdd(BaseModel):
    track_id: str
    position: int

@router.get("/playlists", response_model=List[PlaylistOut])
async def list_playlists(db: AsyncSession = Depends(SessionLocal)):
    result = await db.execute(select(Playlist))
    playlists = result.scalars().all()
    return playlists

@router.post("/playlists", response_model=PlaylistOut, dependencies=[Depends(require_role(["admin", "moderator"]))])
async def create_playlist(playlist: PlaylistCreate, db: AsyncSession = Depends(SessionLocal)):
    db_playlist = Playlist(**playlist.dict())
    db.add(db_playlist)
    await db.commit()
    await db.refresh(db_playlist)
    return db_playlist

@router.get("/playlists/{id}", response_model=PlaylistOut)
async def get_playlist(id: str, db: AsyncSession = Depends(SessionLocal)):
    result = await db.execute(select(Playlist).where(Playlist.id == id))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist

@router.patch("/playlists/{id}", response_model=PlaylistOut, dependencies=[Depends(require_role(["admin", "moderator"]))])
async def update_playlist(id: str, update: PlaylistUpdate, db: AsyncSession = Depends(SessionLocal)):
    result = await db.execute(select(Playlist).where(Playlist.id == id))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(playlist, key, value)
    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)
    return playlist

@router.delete("/playlists/{id}", dependencies=[Depends(require_role(["admin"]))])
async def delete_playlist(id: str, db: AsyncSession = Depends(SessionLocal)):
    result = await db.execute(select(Playlist).where(Playlist.id == id))
    playlist = result.scalar_one_or_none()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    await db.delete(playlist)
    await db.commit()
    return {"message": "Playlist deleted"}

@router.post("/playlists/{id}/tracks", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def add_track_to_playlist(id: str, item: PlaylistTrackAdd, db: AsyncSession = Depends(SessionLocal)):
    playlist_track = PlaylistTrack(playlist_id=id, track_id=item.track_id, position=item.position)
    db.add(playlist_track)
    await db.commit()
    return {"message": "Track added to playlist"}

@router.delete("/playlists/{id}/tracks/{track_id}", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def remove_track_from_playlist(id: str, track_id: str, db: AsyncSession = Depends(SessionLocal)):
    result = await db.execute(select(PlaylistTrack).where(PlaylistTrack.playlist_id == id, PlaylistTrack.track_id == track_id))
    playlist_track = result.scalar_one_or_none()
    if not playlist_track:
        raise HTTPException(status_code=404, detail="Track not found in playlist")
    await db.delete(playlist_track)
    await db.commit()
    return {"message": "Track removed from playlist"}

# --- Spotify Integration ---
@router.get("/spotify/playlists")
async def get_spotify_playlists():
    # TODO: Fetch playlists from Spotify
    return []

@router.post("/spotify/sync")
async def sync_spotify():
    # TODO: Sync playlists/tracks with Spotify
    return {"message": "Spotify sync started"}

# --- Advanced Search ---
@router.get("/search/tracks")
async def search_tracks(query: str = "", genre: str = None, bpm_min: int = None, bpm_max: int = None):
    # TODO: Advanced search for tracks
    return []

@router.get("/search/playlists")
async def search_playlists(query: str = ""): 
    # TODO: Advanced search for playlists
    return []


# --- Pydantic Schemas for Scheduler ---
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

class ScheduleEntry(BaseModel):
    id: Optional[str]
    playlist_id: str
    start_time: datetime
    end_time: datetime
    description: Optional[str]

class ScheduleEntryCreate(BaseModel):
    playlist_id: str
    start_time: datetime
    end_time: datetime
    description: Optional[str]

# For demonstration, use a simple in-memory schedule (replace with DB-backed model for production)
schedule_entries: list[ScheduleEntry] = []

@router.get("/scheduler/entries", response_model=list[ScheduleEntry])
async def list_schedule_entries():
    return schedule_entries

@router.post("/scheduler/entries", response_model=ScheduleEntry, dependencies=[Depends(require_role(["admin", "moderator"]))])
async def create_schedule_entry(entry: ScheduleEntryCreate):
    new_entry = ScheduleEntry(id=str(len(schedule_entries)+1), **entry.dict())
    schedule_entries.append(new_entry)
    return new_entry

@router.patch("/scheduler/entries/{id}", response_model=ScheduleEntry, dependencies=[Depends(require_role(["admin", "moderator"]))])
async def update_schedule_entry(id: str, update: ScheduleEntryCreate):
    for entry in schedule_entries:
        if entry.id == id:
            entry.playlist_id = update.playlist_id
            entry.start_time = update.start_time
            entry.end_time = update.end_time
            entry.description = update.description
            return entry
    raise HTTPException(status_code=404, detail="Schedule entry not found")

@router.delete("/scheduler/entries/{id}", dependencies=[Depends(require_role(["admin"]))])
async def delete_schedule_entry(id: str):
    global schedule_entries
    schedule_entries = [entry for entry in schedule_entries if entry.id != id]
    return {"message": "Schedule entry deleted"}

@router.get("/scheduler/history")
async def get_schedule_history():
    # TODO: Implement undo/redo history (stub)
    return []

# --- Theme Management ---
@router.post("/themes/save")
async def save_theme():
    # TODO: Save user theme
    return {"message": "Theme saved"}

@router.get("/themes/load")
async def load_theme():
    # TODO: Load user theme
    return {"theme": {}}

# --- Logging ---
@router.get("/logs/{log_type}")
async def get_logs(log_type: str):
    # TODO: Return logs by type (player, request, system, network, error)
    return []

@router.get("/logs/{log_type}/download")
async def download_log(log_type: str):
    # TODO: Download log file
    return {"message": f"Download for {log_type} log"}

@router.get("/logs/{log_type}/search")
async def search_logs(log_type: str, query: str):
    # TODO: Search logs
    return []

# --- Network & Devices ---
@router.get("/system/status", dependencies=[Depends(require_role(["admin", "moderator", "user"]))])
async def get_system_status():
    # Example: Check DB, Redis, and storage health (stub)
    return {
        "database": "ok",
        "redis": "ok",
        "storage": "ok",
        "uptime": 123456,
        "version": "1.0.0"
    }

@router.get("/system/monitoring", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def get_system_monitoring():
    # Example: Return system metrics (stub)
    return {
        "cpu": 12.5,
        "memory": 65.2,
        "disk": 80.1,
        "network": {"in": 12345, "out": 67890}
    }

@router.get("/system/devices", dependencies=[Depends(require_role(["admin", "moderator", "user"]))])
async def get_connected_devices():
    # Example: Return list of connected devices (stub)
    return [
        {"id": "dev-1", "name": "Main Player", "type": "audio", "status": "online"},
        {"id": "dev-2", "name": "Signage Display", "type": "video", "status": "offline"}
    ]

@router.put("/system/devices/{device_id}", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def update_device(device_id: str, updates: dict):
    # Example: Update device properties (stub)
    return {"id": device_id, "updated": updates}

@router.post("/system/devices/{device_id}/config", dependencies=[Depends(require_role(["admin"]))])
async def configure_device(device_id: str, config: dict):
    # Example: Apply configuration to device (stub)
    return {"id": device_id, "config": config, "status": "applied"}

# --- Video Output Endpoints (after require_role and router) ---
@router.get("/video-output/state", response_model=VideoOutputState, dependencies=[Depends(require_role(["admin", "moderator", "user"]))])
async def get_video_output_state():
    return video_output_state

@router.post("/video-output/start", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def start_video_output():
    video_output_state.is_live = True
    return {"message": "Video output started"}

@router.post("/video-output/stop", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def stop_video_output():
    video_output_state.is_live = False
    video_output_state.is_recording = False
    video_output_state.recording_time = 0
    return {"message": "Video output stopped"}

@router.post("/video-output/record/start", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def start_video_recording():
    if not video_output_state.is_live:
        video_output_state.is_live = True
    video_output_state.is_recording = True
    video_output_state.recording_time = 0
    return {"message": "Recording started"}

@router.post("/video-output/record/stop", dependencies=[Depends(require_role(["admin", "moderator"]))])
async def stop_video_recording():
    video_output_state.is_recording = False
    return {"message": "Recording stopped"}

@router.get("/video-output/settings", response_model=VideoOutputSettings, dependencies=[Depends(require_role(["admin", "moderator", "user"]))])
async def get_video_output_settings():
    return video_output_state.settings

@router.put("/video-output/settings", response_model=VideoOutputSettings, dependencies=[Depends(require_role(["admin", "moderator"]))])
async def set_video_output_settings(settings: VideoOutputSettings):
    video_output_state.settings = settings
    return settings

@router.get("/video-output/preview", dependencies=[Depends(require_role(["admin", "moderator", "user"]))])
async def video_output_preview():
    # For now, just return a message (future: return preview image/stream URL)
    return {"message": "Video output preview not implemented (stub)"}
