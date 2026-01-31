/**
 * Python Backend Service - Handles communication with Python backend
 */

const config = require('../config');

/**
 * Forward audio data to Python backend for processing
 * @param {string} sessionId - Session ID
 * @param {Array} audioChunks - Array of audio chunk objects
 * @returns {Promise<Response>} - Fetch response
 * @throws {Error} - When Python backend is not available
 */
async function forwardAudioToPython(sessionId, audioChunks) {
  console.log(`Forwarding ${audioChunks.length} audio chunks to Python backend`);
  
  // Combine audio chunks in order
  const combinedAudio = audioChunks
    .sort((a, b) => a.index - b.index)
    .map(chunk => chunk.data)
    .join('');

  // TODO: Uncomment and configure when Python backend is ready
  /*
  const response = await fetch(`${config.PYTHON_BACKEND_URL}/api/process-audio`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sessionId,
      audioData: combinedAudio,
      format: config.AUDIO_FORMAT,
      timestamp: Date.now()
    })
  });

  if (!response.ok) {
    throw new Error(`Python backend error: ${response.status}`);
  }

  return response;
  */

  // For now, throw to trigger mock response
  throw new Error('Python backend not configured');
}

/**
 * Transcribe a single audio chunk in real-time
 * @param {string} sessionId - Session ID
 * @param {string} audioData - Base64 encoded audio chunk
 * @param {number} chunkIndex - Chunk index
 * @returns {Promise<{transcript: string, isFinal: boolean}>}
 */
async function transcribeAudioChunk(sessionId, audioData, chunkIndex) {
  // TODO: Uncomment when Python backend is ready
  /*
  const response = await fetch(`${config.PYTHON_BACKEND_URL}/api/transcribe-chunk`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sessionId,
      audioData,
      chunkIndex,
      timestamp: Date.now()
    })
  });

  if (!response.ok) {
    throw new Error(`Python backend error: ${response.status}`);
  }

  return await response.json();
  */

  // For now, throw to trigger mock transcription
  throw new Error('Python backend not configured');
}

/**
 * Forward chat message to Python backend for processing
 * @param {string} sessionId - Session ID
 * @param {string} text - User message text
 * @param {string} messageId - Message ID
 * @returns {Promise<Response>} - Fetch response
 * @throws {Error} - When Python backend is not available
 */
async function forwardChatToPython(sessionId, text, messageId) {
  console.log(`Forwarding chat message to Python backend`);

  // TODO: Uncomment and configure when Python backend is ready
  /*
  const response = await fetch(`${config.PYTHON_BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sessionId,
      message: text,
      messageId,
      timestamp: Date.now()
    })
  });

  if (!response.ok) {
    throw new Error(`Python backend error: ${response.status}`);
  }

  return response;
  */

  // For now, throw to trigger mock response
  throw new Error('Python backend not configured');
}

/**
 * Stream response from Python backend to frontend client
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Session ID
 * @param {Response} response - Fetch response from Python
 */
async function streamResponseToClient(ws, sessionId, response) {
  // TODO: Implement actual streaming when Python backend is ready
  /*
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  async function read() {
    const { done, value } = await reader.read();
    if (done) {
      ws.send(JSON.stringify({ type: 'BOT_MESSAGE_END', sessionId }));
      return;
    }
    
    const text = decoder.decode(value);
    ws.send(JSON.stringify({ 
      type: 'BOT_MESSAGE', 
      sessionId,
      text,
      isPartial: true 
    }));
    
    read();
  }
  
  read();
  */
}

module.exports = {
  forwardAudioToPython,
  forwardChatToPython,
  streamResponseToClient,
  transcribeAudioChunk
};
