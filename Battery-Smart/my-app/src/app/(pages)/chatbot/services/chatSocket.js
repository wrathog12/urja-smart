export class ChatSocketService {
  constructor() {
    this.ws = null;
    this.sessionId = null;
    this.messageQueue = [];

    // Callbacks for handling events
    this.onChatResponseCallback = null;
    this.onChatResponseEndCallback = null;
    this.onChatProcessingCallback = null;
    this.onChatAckCallback = null;
    this.onErrorCallback = null;
    this.onEscalationCallback = null;
    this.onRedirectPopupCallback = null;
  }

  connect() {
    if (this.ws && this.ws.readyState <= 1) return;

    this.ws = new WebSocket("ws://localhost:4001");

    this.ws.onopen = () => {
      console.log("Chat Socket connected");
      while (this.messageQueue.length > 0) {
        const msg = this.messageQueue.shift();
        this.ws.send(JSON.stringify(msg));
      }
    };

    this.ws.onmessage = (event) => {
      this.handleMessage(event.data);
    };

    this.ws.onerror = (err) => {
      console.error("Chat Socket error:", err);
      if (this.onErrorCallback) {
        this.onErrorCallback(err);
      }
    };

    this.ws.onclose = () => {
      console.log("Chat Socket disconnected");
    };
  }

  handleMessage(data) {
    try {
      const message = JSON.parse(data);
      console.log("Chat received from server:", message.type);

      switch (message.type) {
        case "CHAT_RESPONSE":
          if (this.onChatResponseCallback) {
            this.onChatResponseCallback(message.text, message.isPartial);
          }
          break;

        case "CHAT_RESPONSE_END":
          if (this.onChatResponseEndCallback) {
            this.onChatResponseEndCallback(message.fullText);
          }
          break;

        case "CHAT_PROCESSING":
          console.log("Server started processing chat message");
          if (this.onChatProcessingCallback) {
            this.onChatProcessingCallback();
          }
          break;

        case "CHAT_ACK":
          console.log(`Chat message ${message.messageId} acknowledged`);
          if (this.onChatAckCallback) {
            this.onChatAckCallback(message.messageId);
          }
          break;

        case "ERROR":
          console.error("Server error:", message.message);
          if (this.onErrorCallback) {
            this.onErrorCallback(new Error(message.message));
          }
          break;

        case "SYNC":
        case "SESSION_STARTED":
        case "SESSION_ENDED":
          // Admin/tracking messages
          break;

        case "ESCALATION_TRIGGERED":
          console.log("Call escalated to agent");
          if (this.onEscalationCallback) {
            this.onEscalationCallback(message);
          }
          break;

        case "REDIRECT_POPUP":
          console.log("Redirect popup triggered:", message.redirectType);
          if (this.onRedirectPopupCallback) {
            this.onRedirectPopupCallback(message.redirectType);
          }
          break;

        default:
          console.log("Unhandled chat message type:", message.type);
      }
    } catch (err) {
      console.error("Failed to parse chat message:", err);
    }
  }

  startSession(id) {
    this.sessionId = id;
    const payload = {
      type: "SESSION_START",
      id: this.sessionId,
      sessionType: "chat",
    };

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    } else {
      this.messageQueue.push(payload);
    }
  }

  endSession() {
    if (!this.sessionId) return;

    const payload = {
      type: "SESSION_END",
      id: this.sessionId,
    };

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    } else {
      this.messageQueue.push(payload);
    }
    this.sessionId = null;
  }

  /**
   * Send a chat message to the server
   * @param {string} text - Message text
   * @param {string} messageId - Unique message ID
   */
  sendMessage(text, messageId) {
    if (!this.sessionId) {
      console.warn("Cannot send message: no active session");
      return;
    }

    const payload = {
      type: "CHAT_MESSAGE",
      text,
      messageId,
      sessionId: this.sessionId,
    };

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
      console.log(`Sent chat message: ${messageId}`);
    } else {
      console.warn("WebSocket not ready, queueing message");
      this.messageQueue.push(payload);
    }
  }

  /**
   * Register callback for chat response events (streaming)
   * @param {function} callback - Called with (text, isPartial)
   */
  onChatResponse(callback) {
    this.onChatResponseCallback = callback;
  }

  /**
   * Register callback for chat response completion
   * @param {function} callback - Called with (fullText)
   */
  onChatResponseEnd(callback) {
    this.onChatResponseEndCallback = callback;
  }

  /**
   * Register callback for processing started event
   * @param {function} callback - Called when server starts processing
   */
  onChatProcessing(callback) {
    this.onChatProcessingCallback = callback;
  }

  /**
   * Register callback for errors
   * @param {function} callback - Called with error object
   */
  onError(callback) {
    this.onErrorCallback = callback;
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.sessionId = null;
  }

  /**
   * Register callback for escalation events
   * @param {function} callback - Called when call is escalated
   */
  onEscalation(callback) {
    this.onEscalationCallback = callback;
  }

  /**
   * Trigger escalation to agent
   * @param {string} reason - Optional reason for escalation
   */
  triggerEscalation(reason = "User requested agent assistance") {
    if (!this.sessionId) {
      console.warn("Cannot escalate: no active session");
      return;
    }

    const payload = {
      type: "ESCALATE",
      sessionId: this.sessionId,
      reason,
    };

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
      console.log("Escalation triggered");
    }
  }

  /**
   * Register callback for redirect popup events
   * @param {function} callback - Called with (redirectType) 'maps' | 'invoices'
   */
  onRedirectPopup(callback) {
    this.onRedirectPopupCallback = callback;
  }
}

export const chatSocket = new ChatSocketService();
