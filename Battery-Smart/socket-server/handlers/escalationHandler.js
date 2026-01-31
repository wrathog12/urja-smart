/**
 * Escalation Handler - Handles escalation-related WebSocket messages
 */

const sessionStore = require('../store/sessionStore');
const escalationStore = require('../store/escalationStore');
const { broadcast, sendToClient } = require('../utils/broadcaster');

/**
 * Handle ESCALATE message - Trigger escalation to agent
 * @param {Object} message - Message payload
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Current session ID
 */
function handleEscalation(message, ws, sessionId) {
  const { reason } = message;
  
  if (!sessionId || !sessionStore.hasSession(sessionId)) {
    console.warn('Escalation received for unknown session');
    sendToClient(ws, { type: 'ERROR', message: 'No active session' });
    return;
  }

  // Check if already escalated
  const existingEscalation = escalationStore.getEscalationBySessionId(sessionId);
  if (existingEscalation) {
    console.log(`Session ${sessionId} already escalated`);
    sendToClient(ws, { 
      type: 'ESCALATION_EXISTS', 
      escalationId: existingEscalation.id 
    });
    return;
  }

  const session = sessionStore.getSession(sessionId);
  const history = sessionStore.getSessionHistory(sessionId);
  
  // Create escalation
  const escalation = escalationStore.createEscalation({
    sessionId,
    type: session.type,
    reason: reason || 'User requested agent assistance',
    history
  });

  console.log(`Created escalation ${escalation.id} for session ${sessionId}`);

  // Notify the client that escalation was triggered
  sendToClient(ws, {
    type: 'ESCALATION_TRIGGERED',
    escalationId: escalation.id,
    message: 'Connecting you to an agent...'
  });

  // Broadcast to all clients (admins) about new escalation
  broadcast({
    type: 'ESCALATION_NEW',
    escalation
  });

  return escalation;
}

/**
 * Handle ESCALATION_RESOLVE message - Admin resolves an escalation
 * @param {Object} message - Message payload
 * @param {WebSocket} ws - WebSocket client (admin)
 */
function handleEscalationResolve(message, ws) {
  const { escalationId, resolvedBy } = message;
  
  const escalation = escalationStore.updateEscalationStatus(
    escalationId, 
    'resolved', 
    resolvedBy || 'admin'
  );
  
  if (!escalation) {
    sendToClient(ws, { 
      type: 'ERROR', 
      message: 'Escalation not found' 
    });
    return;
  }

  console.log(`Escalation ${escalationId} resolved by ${resolvedBy || 'admin'}`);

  // Broadcast to all clients about resolved escalation
  broadcast({
    type: 'ESCALATION_RESOLVED',
    escalationId,
    resolvedBy: resolvedBy || 'admin'
  });

  // Notify the original session client if still connected
  const sessionClient = sessionStore.getSessionClient(escalation.sessionId);
  if (sessionClient && sessionClient.readyState === 1) { // WebSocket.OPEN
    sendToClient(sessionClient, {
      type: 'ESCALATION_RESOLVED',
      escalationId,
      message: 'An agent has resolved your request.'
    });
  }
}

/**
 * Handle ESCALATION_TAKE message - Admin takes over escalation
 * @param {Object} message - Message payload
 * @param {WebSocket} ws - WebSocket client (admin)
 */
function handleEscalationTake(message, ws) {
  const { escalationId, takenBy } = message;
  
  const escalation = escalationStore.updateEscalationStatus(
    escalationId,
    'in-progress'
  );
  
  if (!escalation) {
    sendToClient(ws, { 
      type: 'ERROR', 
      message: 'Escalation not found' 
    });
    return;
  }

  console.log(`Escalation ${escalationId} taken by ${takenBy || 'admin'}`);

  // Broadcast update
  broadcast({
    type: 'ESCALATION_UPDATED',
    escalation
  });
}

/**
 * Get all pending escalations (for admin sync)
 * @returns {Array} - Array of pending escalation objects
 */
function getPendingEscalations() {
  return escalationStore.getPendingEscalations();
}

module.exports = {
  handleEscalation,
  handleEscalationResolve,
  handleEscalationTake,
  getPendingEscalations
};
