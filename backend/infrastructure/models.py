from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Interval, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from ..infrastructure.database import Base

class DigitalSignageContent(Base):
    __tablename__ = "digital_signage_content"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(32), nullable=False)  # image, video, text, etc.
    url = Column(Text, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class DigitalSignageSchedule(Base):
    __tablename__ = "digital_signage_schedule"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("digital_signage_content.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    repeat_pattern = Column(String(32))  # e.g., daily, weekly, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Interval, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from ..infrastructure.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(32), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    display_name = Column(String(64))
    avatar_url = Column(Text)
    role = Column(String(16), nullable=False, default="user")
    spotify_id = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    playlists = relationship("Playlist", back_populates="owner")

class Track(Base):
    __tablename__ = "tracks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    artist = Column(String(255))
    album = Column(String(255))
    duration = Column(Interval)
    bpm = Column(Integer)
    genre = Column(String(64))
    storage_url = Column(Text, nullable=False)
    artwork_url = Column(Text)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)
    artwork_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", back_populates="playlists")

class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"
    playlist_id = Column(UUID(as_uuid=True), ForeignKey("playlists.id"), primary_key=True)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), primary_key=True)
    position = Column(Integer, nullable=False)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    device = Column(String(64))
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    current_track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"))
    playback_position = Column(Interval)
    is_active = Column(Boolean, default=True)

class PlaybackHistory(Base):
    __tablename__ = "playback_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"))
    played_at = Column(DateTime, default=datetime.utcnow)
    device = Column(String(64))

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    provider = Column(String(32), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
