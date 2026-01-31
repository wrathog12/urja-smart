/**
 * Escalation Handler - Handles escalation-related WebSocket messages
 */

const sessionStore = require("../store/sessionStore");
const escalationStore = require("../store/escalationStore");
const { broadcast, sendToClient } = require("../utils/broadcaster");

/**
 * Handle ESCALATE message - Trigger escalation to agent
 * @param {Object} message - Message payload
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Current session ID
 */
function handleEscalation(message, ws, sessionId) {
  console.log("📥 ESCALATE received, sessionId:", sessionId);
  console.log("📥 Message contents:", JSON.stringify(message, null, 2));

  const {
    reason,
    metrics,
    avgConfidence,
    summary,
    fullHistory,
    customerPhone,
    customerName,
  } = message;

  if (!sessionId || !sessionStore.hasSession(sessionId)) {
    console.warn("❌ Escalation received for unknown session:", sessionId);
    console.warn(
      "   Available sessions:",
      sessionStore.getAllSessions().map((s) => s.id),
    );
    sendToClient(ws, { type: "ERROR", message: "No active session" });
    return;
  }

  // Check if already escalated
  const existingEscalation =
    escalationStore.getEscalationBySessionId(sessionId);
  if (existingEscalation) {
    console.log(`⚠️ Session ${sessionId} already escalated`);
    sendToClient(ws, {
      type: "ESCALATION_EXISTS",
      escalationId: existingEscalation.id,
    });
    return;
  }

  const session = sessionStore.getSession(sessionId);
  console.log("📋 Session found:", session);

  // Use fullHistory from voice backend if provided, otherwise use session store history
  const history = fullHistory || sessionStore.getSessionHistory(sessionId);
  console.log("📋 History to use:", history?.length || 0, "messages");

  // If fullHistory is provided, also update the session store for consistency
  if (fullHistory && fullHistory.length > 0) {
    fullHistory.forEach((msg) => {
      sessionStore.addChatMessage(sessionId, msg);
    });
  }

  // Create escalation with full context including customer info
  const escalation = escalationStore.createEscalation({
    sessionId,
    type: session.type,
    reason: reason || "User requested agent assistance",
    history,
    metrics: metrics || {}, // STT/LLM/TTS latencies
    avgConfidence: avgConfidence, // Average confidence score
    summary: summary, // AI-generated summary
    customerPhone: customerPhone, // Customer phone for callback
    customerName: customerName, // Customer name
  });

  console.log(
    `✅ Created escalation ${escalation.id} for session ${sessionId}`,
  );

  // Notify the client that escalation was triggered
  sendToClient(ws, {
    type: "ESCALATION_TRIGGERED",
    escalationId: escalation.id,
    message: "Connecting you to an agent...",
  });

  // Broadcast to all clients (admins) about new escalation
  broadcast({
    type: "ESCALATION_NEW",
    escalation,
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
    "resolved",
    resolvedBy || "admin",
  );

  if (!escalation) {
    sendToClient(ws, {
      type: "ERROR",
      message: "Escalation not found",
    });
    return;
  }

  console.log(
    `Escalation ${escalationId} resolved by ${resolvedBy || "admin"}`,
  );

  // Broadcast to all clients about resolved escalation
  broadcast({
    type: "ESCALATION_RESOLVED",
    escalationId,
    resolvedBy: resolvedBy || "admin",
  });

  // Notify the original session client if still connected
  const sessionClient = sessionStore.getSessionClient(escalation.sessionId);
  if (sessionClient && sessionClient.readyState === 1) {
    // WebSocket.OPEN
    sendToClient(sessionClient, {
      type: "ESCALATION_RESOLVED",
      escalationId,
      message: "An agent has resolved your request.",
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
    "in-progress",
  );

  if (!escalation) {
    sendToClient(ws, {
      type: "ERROR",
      message: "Escalation not found",
    });
    return;
  }

  console.log(`Escalation ${escalationId} taken by ${takenBy || "admin"}`);

  // Broadcast update
  broadcast({
    type: "ESCALATION_UPDATED",
    escalation,
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
  getPendingEscalations,
};
