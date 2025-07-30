import asyncio
from typing import Dict, List, Optional
import yt_dlp
import spotipy
import musicbrainzngs
from spotipy.oauth2 import SpotifyOAuth
from redis import Redis
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class MusicServiceManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self._setup_musicbrainz()
        
    def _setup_musicbrainz(self):
        musicbrainzngs.set_useragent(
            "DJAMMS",
            "3.0",
            "http://github.com/systemvirtue/djamms"
        )
        
    async def match_track(self, title: str, artist: str) -> Dict:
        """Use MusicBrainz to get detailed track info"""
        try:
            result = musicbrainzngs.search_recordings(
                query=f"recording:{title} AND artist:{artist}",
                limit=1
            )
            if result and result.get('recording-list'):
                recording = result['recording-list'][0]
                return {
                    'title': recording['title'],
                    'artist': recording['artist-credit'][0]['artist']['name'],
                    'release': recording.get('release-list', [{}])[0].get('title'),
                    'year': recording.get('release-list', [{}])[0].get('date', '').split('-')[0],
                    'mbid': recording['id']
                }
        except Exception as e:
            logger.error(f"MusicBrainz error: {e}")
        return None

class PlaylistConverter:
    def __init__(self, music_manager: MusicServiceManager):
        self.music_manager = music_manager
        
    async def convert_playlist(
        self,
        source_type: str,
        target_type: str,
        playlist_id: str,
        progress_callback: Optional[callable] = None
    ) -> List[Dict]:
        """Convert playlist between services using MusicBrainz for matching"""
        if source_type == "spotify" and target_type == "youtube":
            return await self._spotify_to_youtube(playlist_id, progress_callback)
        elif source_type == "youtube" and target_type == "spotify":
            return await self._youtube_to_spotify(playlist_id, progress_callback)
        else:
            raise ValueError(f"Unsupported conversion: {source_type} to {target_type}")

    async def _spotify_to_youtube(self, playlist_id: str, progress_callback=None) -> List[Dict]:
        # Implementation using MusicBrainz for better matching
        pass

    async def _youtube_to_spotify(self, playlist_id: str, progress_callback=None) -> List[Dict]:
        # Implementation using MusicBrainz for better matching
        pass

class UnifiedMediaPlayer:
    def __init__(
        self,
        music_manager: MusicServiceManager,
        redis_client: Redis
    ):
        self.music_manager = music_manager
        self.redis = redis_client
        self.current_mode = "spotify"
        self.active_connections: List[WebSocket] = []
        self.current_track: Optional[Dict] = None
        
    async def switch_mode(self, mode: str):
        """Switch between Spotify and YouTube modes"""
        if mode not in ["spotify", "youtube"]:
            raise ValueError("Invalid mode")
        self.current_mode = mode
        await self._broadcast_status({"type": "mode_changed", "mode": mode})
        
    async def play(self, track_id: str):
        """Play track from current service"""
        try:
            if self.current_mode == "spotify":
                await self._play_spotify(track_id)
            else:
                await self._play_youtube(track_id)
        except Exception as e:
            logger.error(f"Playback error: {e}")
            await self._broadcast_status({"type": "error", "message": str(e)})
            
    async def _broadcast_status(self, message: Dict):
        """Send status update to all connected clients"""
        dead_connections = []
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except:
                dead_connections.append(ws)
        
        # Cleanup dead connections
        for ws in dead_connections:
            self.active_connections.remove(ws)
