/**
 * Battery Smart WebSocket Server
 * 
 * Main entry point for the WebSocket server that handles:
 * - Voice session management
 * - Audio streaming from frontend
 * - Communication with Python backend (placeholder)
 * - Real-time message streaming to clients
 */

const { WebSocketServer } = require('ws');
const config = require('./config');
const sessionStore = require('./store/sessionStore');
const { setWSS, sendToClient } = require('./utils/broadcaster');
const {
  handleSessionStart,
  handleSessionEnd,
  cleanupSession,
  handleAudioData,
  handleAudioEnd,
  handleChatMessage,
  handleEscalation,
  handleEscalationResolve,
  handleEscalationTake,
  getPendingEscalations
} = require('./handlers');

// Create WebSocket server
const wss = new WebSocketServer({ port: config.WS_PORT });

// Set WSS instance for broadcaster
setWSS(wss);

// Handle new connections
wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Track which session this client belongs to
  let clientSessionId = null;

  // Send current active sessions and escalations to the new client (for Admin panel)
  sendToClient(ws, {
    type: 'SYNC',
    sessions: sessionStore.getAllSessions(),
    escalations: getPendingEscalations()
  });

  // Handle incoming messages
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);
      console.log('Received:', message.type);

      switch (message.type) {
        case 'SESSION_START':
          clientSessionId = handleSessionStart(message, ws);
          break;

        case 'SESSION_END':
          handleSessionEnd(message);
          if (message.id === clientSessionId) {
            clientSessionId = null;
          }
          break;

        case 'AUDIO_DATA':
          handleAudioData(message, ws, clientSessionId);
          break;

        case 'AUDIO_END':
          handleAudioEnd(message, ws, clientSessionId);
          break;

        case 'CHAT_MESSAGE':
          handleChatMessage(message, ws, clientSessionId);
          break;

        case 'ESCALATE':
          handleEscalation(message, ws, clientSessionId);
          break;

        case 'ESCALATION_RESOLVE':
          handleEscalationResolve(message, ws);
          break;

        case 'ESCALATION_TAKE':
          handleEscalationTake(message, ws);
          break;

        default:
          console.warn('Unknown message type:', message.type);
      }
    } catch (err) {
      console.error('Failed to parse message:', err);
    }
  });

  // Handle client disconnect
  ws.on('close', () => {
    console.log('Client disconnected');
    cleanupSession(clientSessionId);
  });

  // Handle errors
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

// Server startup logs
console.log('='.repeat(50));
console.log('Battery Smart WebSocket Server');
console.log('='.repeat(50));
console.log(`WebSocket server running on ws://localhost:${config.WS_PORT}`);
console.log(`Python backend URL: ${config.PYTHON_BACKEND_URL}`);
console.log('='.repeat(50));
