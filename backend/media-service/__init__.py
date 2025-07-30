from flask import jsonify
import subprocess
import json
import os
import logging
from backend.infrastructure.database import db
from backend.models import Media

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_metadata(file_path):
    """Extract metadata from media file using FFmpeg."""
    try:
        # Extract metadata
        result = subprocess.run(
            [
                'ffmpeg', '-i', file_path, '-hide_banner', '-loglevel', 'error',
                '-f', 'json', '-'
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse JSON metadata
        metadata = json.loads(result.stdout)
        
        # Additional processing for audio-specific metadata
        if metadata.get('streams', [{}])[0].get('codec_type') == 'audio':
            # Extract audio-specific metadata
            audio_stream = next(
                stream for stream in metadata['streams'] 
                if stream.get('codec_type') == 'audio'
            )
            
            if audio_stream:
                metadata['audio'] = {
                    'bit_rate': audio_stream.get('bit_rate'),
                    'sample_rate': audio_stream.get('sample_rate'),
                    'channels': audio_stream.get('channels'),
                    'codec': audio_stream.get('codec_name'),
                }
        
        return metadata
    
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error extracting metadata: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse FFmpeg metadata: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error processing media file: {e}")
        return {}

def transcode_file(input_path, output_path, format='mp3'):
    """Transcode media file to specified format using FFmpeg."""
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # FFmpeg command for transcoding
        format_dict = {
            'mp3': '-f mp3 -ab 128k',
            'mp4': '-f mp4 -preset medium',
            'wav': '-f wav'
        }
        
        if format not in format_dict:
            raise ValueError(f"Unsupported format: {format}")
            
        cmd = [
            'ffmpeg', '-i', input_path, '-y',  # Overwrite output file
            format_dict[format],
            output_path
        ]
        
        # Run the transcoding process
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return output_path
    
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error transcoding file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error transcoding file: {e}")
        raise

def process_uploaded_file(file, upload_folder='uploads'):
    """
    Process an uploaded media file, extracting metadata and transcoding if necessary.
    """
    try:
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Extract metadata
        metadata = extract_metadata(file_path)
        if not metadata:
            raise ValueError("Failed to extract metadata from the file")
            
        # Transcode if necessary (e.g., for audio files)
        if metadata.get('streams', [{}])[0].get('codec_type') == 'audio':
            output_path = os.path.join(
                upload_folder,
                f"{os.path.splitext(filename)[0]}_converted.mp3"
            )
            transcode_file(file_path, output_path, format='mp3')
            # Use the converted file for playback
            file_path = output_path
            filename = os.path.basename(output_path)
            
        # Save to database
        media = Media(
            title=metadata.get('title', filename),
            artist=metadata.get('artist', ''),
            duration=metadata.get('duration', 0),
            file_path=filename,
            metadata=metadata,
            bit_rate=metadata.get('audio', {}).get('bit_rate'),
            sample_rate=metadata.get('audio', {}).get('sample_rate'),
            channels=metadata.get('audio', {}).get('channels'),
            codec=metadata.get('audio', {}).get('codec'),
            file_format=metadata.get('format', {}).get('format_name'),
        )
        db.session.add(media)
        db.session.commit()
        
        return media
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing file {file.filename}: {e}")
        raise