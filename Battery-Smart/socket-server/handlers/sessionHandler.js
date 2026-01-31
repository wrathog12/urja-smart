/**
 * Session Handler - Handles session-related WebSocket messages
 */

const { v4: uuidv4 } = require("uuid");
const sessionStore = require("../store/sessionStore");
const { broadcast } = require("../utils/broadcaster");

/**
 * Handle SESSION_START message
 * @param {Object} message - Message payload
 * @param {WebSocket} ws - WebSocket client
 * @returns {string} - Created session ID
 */
function handleSessionStart(message, ws) {
  const sessionId = message.id || uuidv4();
  console.log(
    "📥 SESSION_START received, creating session:",
    sessionId,
    "type:",
    message.sessionType,
  );

  const session = sessionStore.createSession(
    sessionId,
    message.sessionType,
    ws,
  );

  console.log("✅ Session created:", session);
  broadcast({ type: "SESSION_STARTED", session });
  console.log(`📢 Broadcast SESSION_STARTED for session: ${sessionId}`);

  return sessionId;
}

/**
 * Handle SESSION_END message
 * @param {Object} message - Message payload
 */
function handleSessionEnd(message) {
  if (sessionStore.hasSession(message.id)) {
    sessionStore.deleteSession(message.id);
    broadcast({ type: "SESSION_ENDED", id: message.id });
    console.log(`Session ended: ${message.id}`);
  }
}

/**
 * Cleanup session on disconnect
 * @param {string} sessionId - Session ID to cleanup
 */
function cleanupSession(sessionId) {
  if (sessionId && sessionStore.hasSession(sessionId)) {
    sessionStore.deleteSession(sessionId);
    broadcast({ type: "SESSION_ENDED", id: sessionId });
    console.log(`Session cleaned up: ${sessionId}`);
  }
}

module.exports = {
  handleSessionStart,
  handleSessionEnd,
  cleanupSession,
};
