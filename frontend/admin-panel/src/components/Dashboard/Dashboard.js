import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import socketIOClient from 'socket.io-client';

const Dashboard = () => {
  const [media, setMedia] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch media list
    axios.get('http://localhost:5000/media')
      .then(response => {
        setMedia(response.data);
      })
      .catch(error => {
        setError('Failed to fetch media');
        console.error('Media fetch error:', error);
      });

    // Set up socket.io client
    const socket = socketIOClient('http://localhost:5001');
    socket.on('status_update', (status) => {
      setIsPlaying(status.status === 'playing');
      setCurrentTrack(status.currentTrack);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const handlePlay = (trackId) => {
    socketIOClient('http://localhost:5001').emit('play', { track_id: trackId });
  };

  const handlePause = () => {
    socketIOClient('http://localhost:5001').emit('pause');
  };

  const handleStop = () => {
    socketIOClient('http://localhost:5001').emit('stop');
  };

  const handleSkip = () => {
    if (currentTrack) {
      socketIOClient('http://localhost:5001').emit('skip');
    }
  };

  return (
    <div className="container">
      <h2>Dashboard</h2>
      {error && <p className="error">{error}</p>}
      
      <div className="media-list">
        <h3>Media Library</h3>
        <ul>
          {media.map(track => (
            <li key={track.id} className={`track-item ${isPlaying && currentTrack?.id === track.id ? 'playing' : ''}`}>
              <div className="track-info">
                <h4>{track.title}</h4>
                <p>{track.artist}</p>
                <p>Duration: {track.duration}</p>
              </div>
              <div className="track-controls">
                <button onClick={() => handlePlay(track.id)}>Play</button>
                <button onClick={handlePause}>Pause</button>
                <button onClick={handleStop}>Stop</button>
                <button onClick={handleSkip}>Skip</button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="player-controls">
        <h3>Current Track</h3>
        {currentTrack ? (
          <div>
            <p>{currentTrack.title} by {currentTrack.artist}</p>
            <p>Duration: {currentTrack.duration}</p>
            <div className="playback-status">
              {isPlaying ? (
                <span>Playing</span>
              ) : (
                <span>Stopped</span>
              )}
            </div>
          </div>
        ) : (
          <p>No track is currently playing</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;