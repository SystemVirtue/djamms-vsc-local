from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_public = Column(Boolean, default=True)
    artwork_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tracks = relationship("PlaylistTrack", back_populates="playlist")
    owner = relationship("User")

class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(String, ForeignKey('playlists.id'))
    track_id = Column(Integer, ForeignKey('tracks.id'))
    position = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    playlist = relationship("Playlist", back_populates="tracks")
    track = relationship("Track")

class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String)
    album = Column(String)
    duration = Column(Float)
    filepath = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DigitalSignageContent(Base):
    __tablename__ = "digital_signage_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    content_type = Column(String)  # video, image, html
    content_url = Column(String)
    duration = Column(Integer)  # duration in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DigitalSignageSchedule(Base):
    __tablename__ = "digital_signage_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey('digital_signage_contents.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    content = relationship("DigitalSignageContent")
