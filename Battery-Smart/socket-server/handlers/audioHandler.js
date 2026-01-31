/**
 * Audio Handler - Handles audio-related WebSocket messages
 */

const sessionStore = require('../store/sessionStore');
const { sendToClient } = require('../utils/broadcaster');
const { forwardAudioToPython, streamResponseToClient, transcribeAudioChunk } = require('../services/pythonBackend');
const { sendMockResponse, sendMockTranscriptUpdate } = require('../services/mockResponse');

/**
 * Handle AUDIO_DATA message - Receive audio chunk from frontend
 * Forwards to Python for real-time transcription
 * @param {Object} message - Message payload
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Current session ID
 */
async function handleAudioData(message, ws, sessionId) {
  const { audioData, chunkIndex } = message;
  
  if (!sessionId || !sessionStore.hasSession(sessionId)) {
    console.warn('Audio data received for unknown session');
    sendToClient(ws, { type: 'ERROR', message: 'No active session' });
    return;
  }

  sessionStore.addAudioChunk(sessionId, {
    data: audioData,
    index: chunkIndex,
    timestamp: Date.now()
  });

  console.log(`Received audio chunk ${chunkIndex} for session ${sessionId}`);
  
  // Acknowledge receipt
  sendToClient(ws, { 
    type: 'AUDIO_ACK', 
    chunkIndex,
    sessionId 
  });

  // Forward to Python for real-time transcription
  try {
    const transcriptResult = await transcribeAudioChunk(sessionId, audioData, chunkIndex);
    
    // Send real-time transcript update to frontend
    if (transcriptResult && transcriptResult.transcript) {
      sendToClient(ws, {
        type: 'TRANSCRIPT_UPDATE',
        sessionId,
        transcript: transcriptResult.transcript,
        isFinal: transcriptResult.isFinal || false
      });
    }
  } catch (error) {
    // Python backend not ready - use mock transcription
    sendMockTranscriptUpdate(ws, sessionId, chunkIndex);
  }
}

/**
 * Handle AUDIO_END message - Audio recording finished, process
 * @param {Object} message - Message payload
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Current session ID
 */
async function handleAudioEnd(message, ws, sessionId) {
  console.log(`Audio recording ended for session: ${sessionId}`);

  if (!sessionId || !sessionStore.hasSession(sessionId)) {
    console.warn('Audio end received for unknown session');
    return;
  }

  const audioChunks = sessionStore.getAndClearAudioChunks(sessionId);

  // Notify frontend that processing has started
  sendToClient(ws, { 
    type: 'PROCESSING_STARTED',
    sessionId 
  });

  try {
    // Forward audio to Python backend
    const response = await forwardAudioToPython(sessionId, audioChunks);
    
    // Stream response back to frontend
    await streamResponseToClient(ws, sessionId, response);
    
  } catch (error) {
    console.error('Error processing audio:', error.message);
    
    // Send mock response since Python backend is not ready
    sendMockResponse(ws, sessionId);
  }
}

module.exports = {
  handleAudioData,
  handleAudioEnd
};
