/**
 * Broadcaster - Handles WebSocket message broadcasting
 */

let wssInstance = null;

/**
 * Set the WebSocket server instance
 * @param {WebSocketServer} wss
 */
function setWSS(wss) {
  wssInstance = wss;
}

/**
 * Broadcast message to all connected clients
 * @param {Object} data - Data to broadcast
 */
function broadcast(data) {
  if (!wssInstance) {
    console.warn('WSS not initialized for broadcast');
    return;
  }
  
  const payload = JSON.stringify(data);
  wssInstance.clients.forEach((client) => {
    if (client.readyState === 1) { // WebSocket.OPEN
      client.send(payload);
    }
  });
}

/**
 * Send message to a specific WebSocket client
 * @param {WebSocket} ws - WebSocket client
 * @param {Object} data - Data to send
 */
function sendToClient(ws, data) {
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify(data));
  }
}

module.exports = {
  setWSS,
  broadcast,
  sendToClient
};
