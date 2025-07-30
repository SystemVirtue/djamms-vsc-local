from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ServiceCredentials(BaseModel):
    client_id: str
    client_secret: str
    enabled: bool = True
    
class SystemSettings(BaseModel):
    spotify_credentials: Optional[ServiceCredentials]
    youtube_credentials: Optional[ServiceCredentials]
    musicbrainz_rate_limit: int = Field(default=1, description="Requests per second")
    default_player_mode: str = Field(default="spotify", pattern="^(spotify|youtube)$")

    class Config:
        from_attributes = True
