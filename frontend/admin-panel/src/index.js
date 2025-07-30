import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// Set up WebSocket connection for real-time updates
const socket = io('http://localhost:5001');

// Listen for status updates
socket.on('status_update', (status) => {
  console.log('Status update:', status);
});

// Handle WebSocket connection errors
socket.on('connect_error', (err) => {
  console.error('WebSocket connection error:', err);
});

// Handle disconnection
socket.on('disconnect', () => {
  console.log('WebSocket disconnected');
});

// Example: Listen for command responses
socket.on('command_response', (response) => {
  if (response.status === 'error') {
    alert(response.message);
  }
});