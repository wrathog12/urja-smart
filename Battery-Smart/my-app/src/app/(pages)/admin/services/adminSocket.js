export class AdminSocketService {
  constructor() {
    this.ws = null;
    this.onUpdate = null;
    this.onEscalationNew = null;
    this.onEscalationResolved = null;
    this.onEscalationUpdated = null;
  }

  connect(callback) {
    if (this.ws && this.ws.readyState <= 1) return;
    
    this.onUpdate = callback;
    this.ws = new WebSocket('ws://localhost:8080');

    this.ws.onopen = () => console.log('Admin Socket connected');

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Handle escalation-specific messages
      switch (data.type) {
        case 'ESCALATION_NEW':
          if (this.onEscalationNew) this.onEscalationNew(data.escalation);
          break;
        case 'ESCALATION_RESOLVED':
          if (this.onEscalationResolved) this.onEscalationResolved(data.escalationId);
          break;
        case 'ESCALATION_UPDATED':
          if (this.onEscalationUpdated) this.onEscalationUpdated(data.escalation);
          break;
        default:
          // Pass to general update handler
          if (this.onUpdate) this.onUpdate(data);
      }
    };

    this.ws.onclose = () => {
      console.log('Admin Socket disconnected, retrying in 3s...');
      setTimeout(() => this.connect(callback), 3000);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // Set callbacks for escalation events
  setEscalationCallbacks({ onNew, onResolved, onUpdated }) {
    this.onEscalationNew = onNew;
    this.onEscalationResolved = onResolved;
    this.onEscalationUpdated = onUpdated;
  }

  // Resolve an escalation
  resolveEscalation(escalationId, resolvedBy = 'admin') {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'ESCALATION_RESOLVE',
        escalationId,
        resolvedBy
      }));
    }
  }

  // Take over an escalation
  takeEscalation(escalationId, takenBy = 'admin') {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'ESCALATION_TAKE',
        escalationId,
        takenBy
      }));
    }
  }
}

export const adminSocket = new AdminSocketService();

