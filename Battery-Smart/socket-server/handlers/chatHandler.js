/**
 * Chat Handler - Handles chat message WebSocket messages
 */

const sessionStore = require('../store/sessionStore');
const { sendToClient } = require('../utils/broadcaster');
const { forwardChatToPython } = require('../services/pythonBackend');
const { sendMockChatResponse } = require('../services/mockResponse');

/**
 * Handle CHAT_MESSAGE - Receive text message from frontend
 * @param {Object} message - Message payload
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Current session ID
 */
async function handleChatMessage(message, ws, sessionId) {
  const { text, messageId } = message;
  
  if (!sessionId || !sessionStore.hasSession(sessionId)) {
    console.warn('Chat message received for unknown session');
    sendToClient(ws, { type: 'ERROR', message: 'No active session' });
    return;
  }

  console.log(`Received chat message for session ${sessionId}: "${text.substring(0, 50)}..."`);
  
  // Track user message in session history for escalation
  sessionStore.addChatMessage(sessionId, {
    sender: 'user',
    text: text
  });
  
  // Acknowledge receipt
  sendToClient(ws, { 
    type: 'CHAT_ACK', 
    messageId,
    sessionId 
  });

  // Notify frontend that processing has started
  sendToClient(ws, { 
    type: 'CHAT_PROCESSING',
    sessionId,
    messageId
  });

  try {
    // Forward message to Python backend
    const response = await forwardChatToPython(sessionId, text, messageId);
    
    // Stream response back to frontend
    await streamChatResponse(ws, sessionId, response);
    
  } catch (error) {
    console.error('Error processing chat message:', error.message);
    
    // Send mock response since Python backend is not ready
    sendMockChatResponse(ws, sessionId, text);
  }
}

/**
 * Stream chat response from Python backend to frontend
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Session ID
 * @param {Response} response - Fetch response from Python
 */
async function streamChatResponse(ws, sessionId, response) {
  // TODO: Implement actual streaming when Python backend is ready
  /*
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  async function read() {
    const { done, value } = await reader.read();
    if (done) {
      sendToClient(ws, { type: 'CHAT_RESPONSE_END', sessionId });
      return;
    }
    
    const text = decoder.decode(value);
    sendToClient(ws, { 
      type: 'CHAT_RESPONSE', 
      sessionId,
      text,
      isPartial: true 
    });
    
    read();
  }
  
  read();
  */
}

module.exports = {
  handleChatMessage
};
