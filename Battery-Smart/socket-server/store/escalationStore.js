/**
 * Escalation Store - Manages escalated calls for agent intervention
 */

// Store escalated calls
const escalatedCalls = new Map();

/**
 * Create a new escalation
 * @param {Object} params - Escalation parameters
 * @param {string} params.sessionId - Original session ID
 * @param {string} params.type - Type of session ('voice' or 'chat')
 * @param {string} params.reason - Reason for escalation
 * @param {Array} params.history - Conversation history (transcripts or messages)
 * @returns {Object} - Created escalation object
 */
function createEscalation({ sessionId, type, reason, history }) {
  const escalationId = `esc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  const escalation = {
    id: escalationId,
    sessionId,
    type,
    reason,
    history: history || [],
    status: 'pending', // 'pending' | 'in-progress' | 'resolved'
    createdAt: new Date().toISOString(),
    resolvedAt: null,
    resolvedBy: null
  };
  
  escalatedCalls.set(escalationId, escalation);
  console.log(`Created escalation ${escalationId} for session ${sessionId}`);
  
  return escalation;
}

/**
 * Get an escalation by ID
 * @param {string} id - Escalation ID
 * @returns {Object|undefined} - Escalation object or undefined
 */
function getEscalation(id) {
  return escalatedCalls.get(id);
}

/**
 * Get all escalations (optionally filtered by status)
 * @param {string} [status] - Filter by status
 * @returns {Array} - Array of escalation objects
 */
function getAllEscalations(status = null) {
  const all = Array.from(escalatedCalls.values());
  if (status) {
    return all.filter(e => e.status === status);
  }
  return all;
}

/**
 * Get pending escalations (not resolved)
 * @returns {Array} - Array of pending escalation objects
 */
function getPendingEscalations() {
  return Array.from(escalatedCalls.values()).filter(e => e.status !== 'resolved');
}

/**
 * Add a message to an escalation's history
 * @param {string} escalationId - Escalation ID
 * @param {Object} message - Message to add
 */
function addMessageToEscalation(escalationId, message) {
  const escalation = escalatedCalls.get(escalationId);
  if (escalation) {
    escalation.history.push({
      ...message,
      timestamp: new Date().toISOString()
    });
  }
}

/**
 * Update escalation status
 * @param {string} id - Escalation ID
 * @param {string} status - New status
 * @param {string} [resolvedBy] - Who resolved it (for resolved status)
 * @returns {Object|null} - Updated escalation or null if not found
 */
function updateEscalationStatus(id, status, resolvedBy = null) {
  const escalation = escalatedCalls.get(id);
  if (escalation) {
    escalation.status = status;
    if (status === 'resolved') {
      escalation.resolvedAt = new Date().toISOString();
      escalation.resolvedBy = resolvedBy;
    }
    console.log(`Updated escalation ${id} status to ${status}`);
    return escalation;
  }
  return null;
}

/**
 * Delete an escalation
 * @param {string} id - Escalation ID
 */
function deleteEscalation(id) {
  escalatedCalls.delete(id);
}

/**
 * Check if an escalation exists for a session
 * @param {string} sessionId - Session ID
 * @returns {Object|undefined} - Escalation object or undefined
 */
function getEscalationBySessionId(sessionId) {
  return Array.from(escalatedCalls.values()).find(e => e.sessionId === sessionId);
}

module.exports = {
  createEscalation,
  getEscalation,
  getAllEscalations,
  getPendingEscalations,
  addMessageToEscalation,
  updateEscalationStatus,
  deleteEscalation,
  getEscalationBySessionId
};
