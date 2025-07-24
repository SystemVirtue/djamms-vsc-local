import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_redis_connection():
    from backend.infrastructure.database import redis_client
    pong = await redis_client.ping()
    assert pong is True
