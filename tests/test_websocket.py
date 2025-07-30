import pytest
from backend.player_control_service import app, socketio, status_monitor
from backend.models import Media
from datetime import datetime

@pytest.fixture
def socket_client():
    client = socketio.test_client(app)
    return client

@pytest.fixture
def mock_media():
    return Media(
        id=1,
        title="Test Track",
        artist="Test Artist",
        duration=180,
        file_path="test.mp3"
    )

def test_websocket_connection(socket_client):
    assert socket_client.is_connected()
    received = socket_client.get_received()
    assert len(received) == 1
    assert received[0]['name'] == 'status_update'
    assert received[0]['args'][0]['status'] == 'ready'

def test_play_command(socket_client, mock_media):
    socket_client.emit('play', {'track_id': 1})
    received = socket_client.get_received()
    assert len(received) > 0
    assert received[0]['name'] == 'command_response'
    assert received[0]['args'][0]['status'] == 'success'

def test_stop_command(socket_client):
    socket_client.emit('stop')
    received = socket_client.get_received()
    assert len(received) > 0
    assert received[0]['name'] == 'command_response'
    
def test_status_monitor():
    monitor = status_monitor
    monitor.start_monitoring(1)
    assert monitor.current_status is not None
    assert monitor.current_status.track_id == 1
    assert monitor.current_status.state == 'playing'
    monitor.stop_monitoring()
    assert monitor.current_status is None
