/**
 * Voice Socket Service - WebRTC connection to FastRTC backend
 * 
 * This connects to FastRTC via WebRTC for real-time audio streaming.
 * Connects to FastAPI backend at port 8000 with FastRTC endpoints.
 */

const BACKEND_URL = 'http://localhost:8000';

// Generate unique WebRTC ID
function generateWebRTCId() {
  return `webrtc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export class VoiceSocketService {
  constructor() {
    this.peerConnection = null;
    this.localStream = null;
    this.remoteStream = null;
    this.dataChannel = null;
    this.webrtcId = null;
    this.isConnected = false;
    this.sessionActive = false;

    // Audio playback elements
    this.audioElement = null;

    // Callbacks for handling events
    this.onStateChangeCallback = null;
    this.onTranscriptCallback = null;
    this.onBotResponseCallback = null;
    this.onToolActivationCallback = null;
    this.onCallEndCallback = null;
    this.onErrorCallback = null;
    this.onLogCallback = null;

    // Polling interval for session state
    this.statePollingInterval = null;
  }

  /**
   * Initialize WebRTC connection to FastRTC backend
   */
  async connect() {
    if (this.isConnected) {
      console.log('Already connected');
      return true;
    }

    try {
      // Generate unique webrtc_id for this connection
      this.webrtcId = generateWebRTCId();
      console.log('🔌 WebRTC ID:', this.webrtcId);

      // 1. Get user's microphone
      this.localStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 24000
        }
      });
      console.log('🎤 Microphone access granted');

      // 2. Create RTCPeerConnection
      this.peerConnection = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });

      // 3. Add local audio track
      this.localStream.getTracks().forEach(track => {
        this.peerConnection.addTrack(track, this.localStream);
      });

      // 4. Handle incoming audio from bot
      this.peerConnection.ontrack = (event) => {
        console.log('🔊 Received remote audio track');
        this.remoteStream = event.streams[0];

        // Create audio element for playback if not exists
        if (!this.audioElement) {
          this.audioElement = new Audio();
          this.audioElement.autoplay = true;
        }
        this.audioElement.srcObject = this.remoteStream;
      };

      // 5. Collect ICE candidates to send to server
      const iceCandidates = [];
      this.peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          iceCandidates.push(event.candidate);
        }
      };

      // 6. Handle connection state changes
      this.peerConnection.onconnectionstatechange = () => {
        console.log('Connection state:', this.peerConnection.connectionState);
        if (this.peerConnection.connectionState === 'connected') {
          this.isConnected = true;
          if (this.onStateChangeCallback) {
            this.onStateChangeCallback('connected');
          }
        } else if (this.peerConnection.connectionState === 'disconnected' ||
          this.peerConnection.connectionState === 'failed') {
          this.isConnected = false;
          if (this.onStateChangeCallback) {
            this.onStateChangeCallback('disconnected');
          }
        }
      };

      // 7. Create data channel for messages (FastRTC uses this)
      this.dataChannel = this.peerConnection.createDataChannel('data');

      this.dataChannel.onopen = () => {
        console.log('📡 Data channel opened');
      };

      this.dataChannel.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleDataChannelMessage(message);
        } catch (e) {
          console.log('Data channel message:', event.data);
        }
      };

      // 8. Create and send offer to FastRTC
      const offer = await this.peerConnection.createOffer();
      await this.peerConnection.setLocalDescription(offer);

      // Wait for ICE gathering to complete (or timeout)
      await new Promise((resolve) => {
        if (this.peerConnection.iceGatheringState === 'complete') {
          resolve();
        } else {
          const checkState = () => {
            if (this.peerConnection.iceGatheringState === 'complete') {
              this.peerConnection.removeEventListener('icegatheringstatechange', checkState);
              resolve();
            }
          };
          this.peerConnection.addEventListener('icegatheringstatechange', checkState);
          // Timeout after 3 seconds
          setTimeout(resolve, 3000);
        }
      });

      // 9. Send offer to FastRTC backend with webrtc_id
      const response = await fetch(`${BACKEND_URL}/webrtc/offer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sdp: this.peerConnection.localDescription.sdp,
          type: this.peerConnection.localDescription.type,
          webrtc_id: this.webrtcId
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to connect: ${response.status} - ${errorText}`);
      }

      const answer = await response.json();

      // Check for FastRTC error response
      if (answer.status === 'failed') {
        throw new Error(`FastRTC error: ${answer.meta?.error || 'Unknown error'}`);
      }

      // 10. Set remote description from FastRTC
      await this.peerConnection.setRemoteDescription(
        new RTCSessionDescription({ sdp: answer.sdp, type: answer.type })
      );

      // 11. Send collected ICE candidates
      for (const candidate of iceCandidates) {
        await this.sendIceCandidate(candidate);
      }

      this.isConnected = true;
      this.sessionActive = true;
      console.log('✅ WebRTC connected to FastRTC');

      // Start polling session state
      this.startStatePolling();

      return true;

    } catch (error) {
      console.error('❌ WebRTC connection failed:', error);
      if (this.onErrorCallback) {
        this.onErrorCallback(error);
      }
      return false;
    }
  }

  /**
   * Send ICE candidate to FastRTC server
   */
  async sendIceCandidate(candidate) {
    try {
      await fetch(`${BACKEND_URL}/webrtc/offer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'ice-candidate',
          candidate: {
            candidate: candidate.candidate,
            sdpMid: candidate.sdpMid,
            sdpMLineIndex: candidate.sdpMLineIndex
          },
          webrtc_id: this.webrtcId
        })
      });
    } catch (error) {
      console.warn('Failed to send ICE candidate:', error);
    }
  }

  /**
   * Handle messages from FastRTC data channel
   */
  handleDataChannelMessage(message) {
    console.log('📨 Data channel message:', message);

    switch (message.type) {
      case 'log':
        if (this.onLogCallback) {
          this.onLogCallback(message.data);
        }
        // Handle specific log events
        if (message.data === 'pause_detected') {
          if (this.onStateChangeCallback) {
            this.onStateChangeCallback('processing');
          }
        } else if (message.data === 'response_starting') {
          if (this.onStateChangeCallback) {
            this.onStateChangeCallback('speaking');
          }
        } else if (message.data === 'started_talking') {
          if (this.onStateChangeCallback) {
            this.onStateChangeCallback('listening');
          }
        }
        break;

      case 'fetch_output':
        // AdditionalOutputs from FastRTC
        this.handleAdditionalOutputs(message.data);
        break;

      case 'error':
        console.error('FastRTC error:', message.data);
        if (this.onErrorCallback) {
          this.onErrorCallback(new Error(message.data));
        }
        break;

      case 'warning':
        console.warn('FastRTC warning:', message.data);
        break;
    }
  }

  /**
   * Handle AdditionalOutputs from FastRTC (transcript, bot response, tool, latency)
   */
  handleAdditionalOutputs(data) {
    // data is an array: [userText, botResponse, toolData, latency]
    if (Array.isArray(data) && data.length >= 4) {
      const [userText, botResponse, toolData, latency] = data;

      if (userText && this.onTranscriptCallback) {
        this.onTranscriptCallback(userText.replace(/^🗣️\s*/, ''));
      }

      if (botResponse && this.onBotResponseCallback) {
        this.onBotResponseCallback(botResponse.replace(/^🤖\s*/, ''));
      }

      if (toolData && toolData !== 'None' && this.onToolActivationCallback) {
        try {
          const tool = typeof toolData === 'string' ? JSON.parse(toolData) : toolData;
          this.onToolActivationCallback(tool);

          // Check for end_call tool
          if (tool?.name === 'end_call') {
            if (this.onCallEndCallback) {
              this.onCallEndCallback(tool.args?.reason || 'user_requested');
            }
          }
        } catch (e) {
          // Not valid JSON
        }
      }
    }
  }

  /**
   * Poll backend for session state updates (fallback if data channel not working)
   */
  startStatePolling() {
    if (this.statePollingInterval) return;

    // Add a delay before starting to poll to ensure session reset completes
    setTimeout(() => {
      this.statePollingInterval = setInterval(async () => {
        try {
          const response = await fetch(`${BACKEND_URL}/api/session/state`);
          if (!response.ok) return;

          const state = await response.json();

          // Handle call end from backend - ONLY if session is active
          // This prevents false triggers from stale state
          if (state.is_active && state.should_end && this.onCallEndCallback) {
            this.onCallEndCallback(state.end_reason);
            this.stopStatePolling();
            this.disconnect();
          }

        } catch (error) {
          // Silently ignore polling errors
        }
      }, 1000); // Poll every 1 second
    }, 1500); // Wait 1.5 seconds before polling
  }

  stopStatePolling() {
    if (this.statePollingInterval) {
      clearInterval(this.statePollingInterval);
      this.statePollingInterval = null;
    }
  }

  /**
   * Start a voice session (unmute microphone)
   */
  startSession() {
    if (!this.localStream) {
      console.warn('No local stream - call connect() first');
      return false;
    }

    // Unmute microphone tracks
    this.localStream.getAudioTracks().forEach(track => {
      track.enabled = true;
    });

    this.sessionActive = true;
    console.log('🎙️ Session started - microphone active');

    if (this.onStateChangeCallback) {
      this.onStateChangeCallback('listening');
    }

    return true;
  }

  /**
   * End voice session (mute microphone)
   */
  endSession() {
    if (!this.localStream) return;

    // Mute microphone tracks
    this.localStream.getAudioTracks().forEach(track => {
      track.enabled = false;
    });

    this.sessionActive = false;
    console.log('🔇 Session ended - microphone muted');

    if (this.onStateChangeCallback) {
      this.onStateChangeCallback('idle');
    }
  }

  /**
   * Toggle voice session (for button press)
   */
  toggleSession() {
    if (this.sessionActive) {
      this.endSession();
      return false;
    } else {
      this.startSession();
      return true;
    }
  }

  /**
   * Switch voice persona (male/female)
   */
  async setVoicePersona(persona) {
    try {
      const response = await fetch(`${BACKEND_URL}/api/voice/persona`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona })
      });

      if (!response.ok) {
        throw new Error(`Failed to set persona: ${response.status}`);
      }

      const result = await response.json();
      console.log(`🔄 Voice persona changed to: ${persona}`);
      return result;

    } catch (error) {
      console.error('Failed to change voice persona:', error);
      throw error;
    }
  }

  /**
   * Get current voice persona
   */
  async getVoicePersona() {
    try {
      const response = await fetch(`${BACKEND_URL}/api/voice/persona`);
      if (!response.ok) throw new Error('Failed to get persona');
      return await response.json();
    } catch (error) {
      console.error('Failed to get voice persona:', error);
      throw error;
    }
  }

  /**
   * Register callback for state changes
   * @param {function} callback - Called with state ('connected', 'disconnected', 'listening', 'idle', 'processing', 'speaking')
   */
  onStateChange(callback) {
    this.onStateChangeCallback = callback;
  }

  /**
   * Register callback for transcript updates
   */
  onTranscript(callback) {
    this.onTranscriptCallback = callback;
  }

  /**
   * Register callback for bot responses
   */
  onBotResponse(callback) {
    this.onBotResponseCallback = callback;
  }

  /**
   * Register callback for tool activations
   */
  onToolActivation(callback) {
    this.onToolActivationCallback = callback;
  }

  /**
   * Register callback for call end events
   */
  onCallEnd(callback) {
    this.onCallEndCallback = callback;
  }

  /**
   * Register callback for log messages from FastRTC
   */
  onLog(callback) {
    this.onLogCallback = callback;
  }

  /**
   * Register callback for errors
   */
  onError(callback) {
    this.onErrorCallback = callback;
  }

  /**
   * Disconnect from FastRTC
   */
  disconnect() {
    this.stopStatePolling();

    if (this.dataChannel) {
      this.dataChannel.close();
      this.dataChannel = null;
    }

    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop());
      this.localStream = null;
    }

    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }

    if (this.audioElement) {
      this.audioElement.srcObject = null;
    }

    this.isConnected = false;
    this.sessionActive = false;
    this.webrtcId = null;
    console.log('🔌 Disconnected from FastRTC');

    if (this.onStateChangeCallback) {
      this.onStateChangeCallback('disconnected');
    }
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      isConnected: this.isConnected,
      sessionActive: this.sessionActive,
      webrtcId: this.webrtcId,
      connectionState: this.peerConnection?.connectionState || 'closed'
    };
  }
}

// Singleton instance
export const voiceSocket = new VoiceSocketService();
