from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import SessionLocal
from backend.infrastructure.security import get_current_user
import json
import httpx

# Models for media API
class Track(BaseModel):
    id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration: int
    thumbnail_url: str
    source_url: str
    source_type: str

class Playlist(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    tracks: List[Track]
    source_type: str
    
class PlaylistConversion(BaseModel):
    source_type: str
    target_type: str
    playlist_id: str

class SearchQuery(BaseModel):
    query: str

# Router
router = APIRouter(prefix="/api", tags=["media"])

# Get database session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

# Spotify API client
async def spotify_client(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(headers=headers, base_url="https://api.spotify.com/v1") as client:
        return client

# YouTube Data API client (mock)
class YouTubeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def get_playlist(self, playlist_id: str):
        # In a real implementation, this would call the YouTube API
        # For now, return mock data
        return {
            "id": playlist_id,
            "title": f"YouTube Playlist {playlist_id}",
            "description": "Mock YouTube playlist",
            "items": [
                {
                    "id": "video1",
                    "title": "Song One",
                    "artist": "Artist One",
                    "duration": 180,
                    "thumbnail": "https://i.ytimg.com/vi/video1/default.jpg",
                    "url": f"https://youtube.com/watch?v=video1"
                },
                {
                    "id": "video2",
                    "title": "Song Two",
                    "artist": "Artist Two",
                    "duration": 240,
                    "thumbnail": "https://i.ytimg.com/vi/video2/default.jpg",
                    "url": f"https://youtube.com/watch?v=video2"
                }
            ]
        }
    
    async def search(self, query: str, limit: int = 10):
        # Mock search results
        return {
            "items": [
                {
                    "id": {"videoId": f"video{i}"},
                    "snippet": {
                        "title": f"Result {i} for {query}",
                        "channelTitle": f"Channel {i}",
                        "thumbnails": {"default": {"url": f"https://i.ytimg.com/vi/video{i}/default.jpg"}}
                    }
                }
                for i in range(1, limit + 1)
            ]
        }

# Endpoints
@router.get("/playlists/spotify/{playlist_id}", response_model=Playlist)
async def get_spotify_playlist(
    playlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # This would normally get a Spotify access token from the user's account
    # For now, we'll return mock data
    
    # Mock Spotify playlist data
    playlist_data = {
        "id": playlist_id,
        "name": f"Spotify Playlist {playlist_id}",
        "description": "Mock Spotify playlist",
        "source_type": "spotify",
        "tracks": [
            {
                "id": "track1",
                "title": "Spotify Song One",
                "artist": "Spotify Artist One",
                "album": "Album One",
                "duration": 210,
                "thumbnail_url": "https://i.scdn.co/image/ab67616d0000b273f22549b6e5efc1e3d3ef9f93",
                "source_url": "https://open.spotify.com/track/track1",
                "source_type": "spotify"
            },
            {
                "id": "track2",
                "title": "Spotify Song Two",
                "artist": "Spotify Artist Two",
                "album": "Album Two",
                "duration": 195,
                "thumbnail_url": "https://i.scdn.co/image/ab67616d0000b273f72e8d83ba55bbf71e962b9e",
                "source_url": "https://open.spotify.com/track/track2",
                "source_type": "spotify"
            }
        ]
    }
    
    return playlist_data

@router.get("/playlists/youtube/{playlist_id}", response_model=Playlist)
async def get_youtube_playlist(
    playlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Mock YouTube API client
    youtube = YouTubeClient("mock_api_key")
    playlist = await youtube.get_playlist(playlist_id)
    
    # Convert to our format
    tracks = [
        Track(
            id=item["id"],
            title=item["title"],
            artist=item["artist"],
            duration=item["duration"],
            thumbnail_url=item["thumbnail"],
            source_url=item["url"],
            source_type="youtube"
        )
        for item in playlist["items"]
    ]
    
    return Playlist(
        id=playlist["id"],
        name=playlist["title"],
        description=playlist["description"],
        tracks=tracks,
        source_type="youtube"
    )

@router.get("/search/spotify", response_model=List[Track])
async def search_spotify(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Mock Spotify search results
    search_results = [
        {
            "id": f"track{i}",
            "title": f"Spotify Result {i} for {q}",
            "artist": f"Artist {i}",
            "album": f"Album {i}",
            "duration": 180 + i * 10,
            "thumbnail_url": f"https://i.scdn.co/image/ab67616d0000b273{i}",
            "source_url": f"https://open.spotify.com/track/track{i}",
            "source_type": "spotify"
        }
        for i in range(1, 6)
    ]
    
    return search_results

@router.get("/search/youtube", response_model=List[Track])
async def search_youtube(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Mock YouTube API client
    youtube = YouTubeClient("mock_api_key")
    search_results = await youtube.search(q)
    
    # Convert to our format
    tracks = [
        Track(
            id=item["id"]["videoId"],
            title=item["snippet"]["title"],
            artist=item["snippet"]["channelTitle"],
            duration=240,  # Mock duration
            thumbnail_url=item["snippet"]["thumbnails"]["default"]["url"],
            source_url=f"https://youtube.com/watch?v={item['id']['videoId']}",
            source_type="youtube"
        )
        for item in search_results["items"][:5]
    ]
    
    return tracks

@router.post("/playlists/convert", response_model=Playlist)
async def convert_playlist(
    conversion: PlaylistConversion,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if conversion.source_type == conversion.target_type:
        raise HTTPException(status_code=400, detail="Source and target types must be different")
    
    if conversion.source_type not in ["spotify", "youtube"] or conversion.target_type not in ["spotify", "youtube"]:
        raise HTTPException(status_code=400, detail="Source and target types must be 'spotify' or 'youtube'")
    
    # Get the source playlist
    source_playlist = None
    if conversion.source_type == "spotify":
        source_playlist = await get_spotify_playlist(conversion.playlist_id, db, current_user)
    else:
        source_playlist = await get_youtube_playlist(conversion.playlist_id, db, current_user)
    
    # Convert tracks (in a real implementation, this would search for matches)
    converted_tracks = []
    for track in source_playlist.tracks:
        # Mock conversion by changing IDs and URLs
        converted_tracks.append(Track(
            id=f"{conversion.target_type}_{track.id}",
            title=track.title,
            artist=track.artist,
            album=track.album,
            duration=track.duration,
            thumbnail_url=track.thumbnail_url,
            source_url=f"https://{'open.spotify.com/track' if conversion.target_type == 'spotify' else 'youtube.com/watch?v='}/{conversion.target_type}_{track.id}",
            source_type=conversion.target_type
        ))
    
    # Return the converted playlist
    return Playlist(
        id=f"{conversion.target_type}_{source_playlist.id}",
        name=f"{source_playlist.name} (Converted to {conversion.target_type.title()})",
        description=source_playlist.description,
        tracks=converted_tracks,
        source_type=conversion.target_type
    )

@router.get("/user/playlists", response_model=List[Playlist])
async def get_user_playlists(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Mock user playlists
    playlists = [
        {
            "id": "user_playlist1",
            "name": "My Favorites",
            "description": "My favorite songs",
            "tracks": [
                {
                    "id": "track1",
                    "title": "My Favorite Song",
                    "artist": "Favorite Artist",
                    "album": "Greatest Hits",
                    "duration": 240,
                    "thumbnail_url": "https://i.scdn.co/image/ab67616d0000b273f22549b6e5efc1e3d3ef9f93",
                    "source_url": "https://open.spotify.com/track/track1",
                    "source_type": "spotify"
                }
            ],
            "source_type": "spotify"
        }
    ]
    
    return playlists
