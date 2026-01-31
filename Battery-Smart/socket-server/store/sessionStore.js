/**
 * Session Store - Manages active sessions and their data
 */

// Store active sessions
const activeSessions = new Map();

// Store client connections mapped to session IDs
const sessionClients = new Map();

/**
 * Create a new session
 * @param {string} id - Session ID
 * @param {string} sessionType - Type of session ('voice' or 'chat')
 * @param {WebSocket} ws - WebSocket connection
 * @returns {Object} - Created session object
 */
function createSession(id, sessionType, ws) {
  const session = {
    id,
    type: sessionType,
    startTime: new Date().toISOString(),
    audioChunks: [],
    chatHistory: [], // Track conversation for escalation
  };

  activeSessions.set(id, session);
  sessionClients.set(id, ws);

  return session;
}

/**
 * Get a session by ID
 * @param {string} id - Session ID
 * @returns {Object|undefined} - Session object or undefined
 */
function getSession(id) {
  return activeSessions.get(id);
}

/**
 * Check if a session exists
 * @param {string} id - Session ID
 * @returns {boolean}
 */
function hasSession(id) {
  return activeSessions.has(id);
}

/**
 * Delete a session
 * @param {string} id - Session ID
 */
function deleteSession(id) {
  activeSessions.delete(id);
  sessionClients.delete(id);
}

/**
 * Get all active sessions
 * @returns {Array} - Array of session objects
 */
function getAllSessions() {
  return Array.from(activeSessions.values());
}

/**
 * Get client WebSocket for a session
 * @param {string} id - Session ID
 * @returns {WebSocket|undefined}
 */
function getSessionClient(id) {
  return sessionClients.get(id);
}

/**
 * Add audio chunk to session
 * @param {string} sessionId - Session ID
 * @param {Object} chunk - Audio chunk data
 */
function addAudioChunk(sessionId, chunk) {
  const session = activeSessions.get(sessionId);
  if (session) {
    session.audioChunks.push(chunk);
  }
}

/**
 * Get and clear audio chunks for a session
 * @param {string} sessionId - Session ID
 * @returns {Array} - Audio chunks
 */
function getAndClearAudioChunks(sessionId) {
  const session = activeSessions.get(sessionId);
  if (session) {
    const chunks = [...session.audioChunks];
    session.audioChunks = [];
    return chunks;
  }
  return [];
}

/**
 * Add a message to session's chat history
 * @param {string} sessionId - Session ID
 * @param {Object} message - Message object { sender, text, timestamp, confidence?, tool? }
 */
function addChatMessage(sessionId, message) {
  const session = activeSessions.get(sessionId);
  if (session) {
    session.chatHistory.push({
      ...message,
      timestamp: message.timestamp || new Date().toISOString(),
      confidence: message.confidence || null, // STT confidence score (0-1)
      tool: message.tool || null, // Tool used in this turn
    });
  }
}

/**
 * Get session's conversation history
 * @param {string} sessionId - Session ID
 * @returns {Array} - Chat history array
 */
function getSessionHistory(sessionId) {
  const session = activeSessions.get(sessionId);
  return session ? session.chatHistory : [];
}

module.exports = {
  createSession,
  getSession,
  hasSession,
  deleteSession,
  getAllSessions,
  getSessionClient,
  addAudioChunk,
  getAndClearAudioChunks,
  addChatMessage,
  getSessionHistory,
};
