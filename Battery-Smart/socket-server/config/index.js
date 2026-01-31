module.exports = {
  // Python backend URL (placeholder - update when Python backend is ready)
  PYTHON_BACKEND_URL: process.env.PYTHON_BACKEND_URL || 'http://localhost:5000',
  
  // WebSocket server port
  WS_PORT: process.env.WS_PORT || 8080,
  
  // Audio settings
  AUDIO_FORMAT: 'webm',
  
  // Streaming settings
  STREAM_WORD_DELAY_MS: 150, // Delay between words for streaming effect
};
