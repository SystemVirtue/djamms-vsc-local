from flask import jsonify
from flask_socketio import emit
import subprocess
import json
import os
import signal
import time
import logging
from backend.infrastructure.database import db
from backend.models import Media

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to track playback state
current_processes = {
    'ffmpeg': None,
    'mpg123': None
}
current_track = None

def get_process_status(process):
    """Get the status of the current media playback process."""
    if process:
        return {
            'status': 'playing' if process.poll() is None else 'stopped',
            'pid': process.pid if process else None
        }
    return {'status': 'stopped', 'pid': None}

@socketio.on('connect')
def on_connect():
    """Handle client connection event."""
    print('Client connected')
    emit('status_update', {'status': 'ready'})

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection event."""
    global current_processes, current_track
    print('Client disconnected')
    if current_processes['ffmpeg'] or current_processes['mpg123']:
        try:
            # Stop both FFmpeg and mpg123 processes
            if current_processes['ffmpeg']:
                os.kill(current_processes['ffmpeg'].pid, signal.SIGTERM)
            if current_processes['mpg123']:
                os.kill(current_processes['mpg123'].pid, signal.SIGTERM)
            current_processes = {
                'ffmpeg': None,
                'mpg123': None
            }
            current_track = None
        except Exception as e:
            logger.error(f"Error stopping process: {e}")

@socketio.on('play')
def play_command(data):
    """Handle play command from client."""
    global current_processes, current_track
    try:
        if not current_processes['ffmpeg'] or current_processes['ffmpeg'].poll() is not None:
            if 'track_id' not in data:
                raise ValueError("track_id is required")
                
            # Get the track from the database
            track = Media.query.get(data['track_id'])
            if not track:
                raise ValueError("Track not found")
                
            # Set up the track path
            track_path = os.path.join('uploads', track.file_path)
            
            # Start FFmpeg process to pipe audio to mpg123
            ffmpeg_process = subprocess.Popen(
                ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', track_path, '-f', 'wav', '-'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Start mpg123 process to play the audio
            mpg_process = subprocess.Popen(
                ['mpg123', '-'],
                stdin=ffmpeg_process.stdout
            )
            
            # Store the processes and current track
            current_processes = {
                'ffmpeg': ffmpeg_process,
                'mpg123': mpg_process
            }
            current_track = {
                'id': track.id,
                'title': track.title,
                'artist': track.artist,
                'duration': track.duration,
                'file_path': track.file_path
            }
            
            # Emit immediate confirmation
            emit('command_response', {'status': 'success', 'message': 'Playback started'})
            
            # Start background status monitoring
            def monitor_processes():
                while True:
                    ffmpeg_status = get_process_status(current_processes['ffmpeg'])
                    mpg_status = get_process_status(current_processes['mpg123'])
                    status = {
                        'ffmpeg': ffmpeg_status,
                        'mpg123': mpg_status
                    }
                    emit('status_update', status)
                    if ffmpeg_status['status'] == 'stopped' and mpg_status['status'] == 'stopped':
                        break
                    time.sleep(0.5)
            
            thread = threading.Thread(target=monitor_processes)
            thread.start()
            
            return jsonify({'status': 'success', 'message': 'Track is now playing', 'track': current_track})
        else:
            return jsonify({'status': 'error', 'message': 'Already playing'})
    except Exception as e:
        logger.error(f"Error handling play command: {e}")
        emit('command_response', {'status': 'error', 'message': str(e)})
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('pause')
def pause_command():
    """Handle pause command from client."""
    global current_processes
    try:
        if current_processes['ffmpeg'] and current_processes['ffmpeg'].poll() is None:
            # Send SIGSTOP to pause
            os.kill(current_processes['ffmpeg'].pid, signal.SIGSTOP)
            if current_processes['mpg123']:
                os.kill(current_processes['mpg123'].pid, signal.SIGSTOP)
            emit('command_response', {'status': 'success', 'message': 'Playback paused'})
            return jsonify({'status': 'success', 'message': 'Playback paused'})
        else:
            return jsonify({'status': 'error', 'message': 'Not currently playing'})
    except Exception as e:
        logger.error(f"Error handling pause command: {e}")
        emit('command_response', {'status': 'error', 'message': str(e)})
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('resume')
def resume_command():
    """Handle resume command from client."""
    global current_processes
    try:
        if current_processes['ffmpeg'] and current_processes['ffmpeg'].poll() is None:
            # Send SIGCONT to resume
            os.kill(current_processes['ffmpeg'].pid, signal.SIGCONT)
            if current_processes['mpg123']:
                os.kill(current_processes['mpg123'].pid, signal.SIGCONT)
            emit('command_response', {'status': 'success', 'message': 'Playback resumed'})
            return jsonify({'status': 'success', 'message': 'Playback resumed'})
        else:
            return jsonify({'status': 'error', 'message': 'Not currently playing'})
    except Exception as e:
        logger.error(f"Error handling resume command: {e}")
        emit('command_response', {'status': 'error', 'message': str(e)})
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('stop')
def stop_command():
    """Handle stop command from client."""
    global current_processes, current_track
    try:
        if current_processes['ffmpeg'] or current_processes['mpg123']:
            # Terminate both processes
            if current_processes['ffmpeg']:
                os.kill(current_processes['ffmpeg'].pid, signal.SIGTERM)
            if current_processes['mpg123']:
                os.kill(current_processes['mpg123'].pid, signal.SIGTERM)
            current_processes = {
                'ffmpeg': None,
                'mpg123': None
            }
            current_track = None
            emit('command_response', {'status': 'success', 'message': 'Playback stopped'})
            return jsonify({'status': 'success', 'message': 'Playback stopped'})
        else:
            return jsonify({'status': 'error', 'message': 'No track is currently playing'})
    except Exception as e:
        logger.error(f"Error handling stop command: {e}")
        emit('command_response', {'status': 'error', 'message': str(e)})
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('skip')
def skip_command():
    """Handle skip command from client."""
    global current_processes, current_track
    try:
        if current_processes['ffmpeg'] and current_processes['ffmpeg'].poll() is None:
            # Stop the current track
            if current_processes['ffmpeg']:
                os.kill(current_processes['ffmpeg'].pid, signal.SIGTERM)
            if current_processes['mpg123']:
                os.kill(current_processes['mpg123'].pid, signal.SIGTERM)
            current_processes = {
                'ffmpeg': None,
                'mpg123': None
            }
            current_track = None
            
            # Request the next track from the media service
            next_track = get_next_track()
            
            if next_track:
                # Start playing the next track
                play_command({'track_id': next_track.id})
                return jsonify({'status': 'success', 'message': 'Skipped to next track', 'track': next_track})
            else:
                emit('command_response', {'status': 'success', 'message': 'No more tracks in playlist'})
                return jsonify({'status': 'success', 'message': 'No more tracks in playlist'})
        else:
            return jsonify({'status': 'error', 'message': 'No track is currently playing'})
    except Exception as e:
        logger.error(f"Error handling skip command: {e}")
        emit('command_response', {'status': 'error', 'message': str(e)})
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_next_track():
    """Get the next track in the playlist."""
    # This function would typically call your media service to get the next track
    # For this example, we'll return a mock track
    return Media.query.offset(current_track.id + 1).first() if current_track else None

if __name__ == '__main__':
    socketio.run(app, debug=True)