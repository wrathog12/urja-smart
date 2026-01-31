/**
 * Mock Response Service - Simulates responses when Python backend is unavailable
 */

const config = require('../config');
const sessionStore = require('../store/sessionStore');
const { sendToClient } = require('../utils/broadcaster');

// Mock responses for voice testing
const MOCK_VOICE_RESPONSES = [
  "I received your voice message and I'm processing it.",
  "This is a simulated response from the AI assistant.",
  "The Python backend integration is coming soon!",
  "Your voice has been captured successfully. Processing your request...",
  "I understand what you're saying. Let me help you with that."
];

// Mock responses for chat testing
const MOCK_CHAT_RESPONSES = [
  "I'm processing your message. The Python backend will provide real responses soon!",
  "Thanks for your question! This is a mock response while the AI backend is being set up.",
  "I received your message. Full AI capabilities coming soon!",
  "Interesting question! Once the Python backend is ready, I'll provide detailed answers.",
  "Got it! Currently running in demo mode - real AI responses coming soon."
];

/**
 * Send mock streaming response when Python backend is not available
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Session ID
 */
function sendMockResponse(ws, sessionId) {
  // Mock transcripts for testing
  const MOCK_TRANSCRIPTS = [
    "What is the battery status?",
    "Can you help me with the charging schedule?",
    "Tell me about the energy consumption today.",
    "How much power is available right now?",
    "Show me the usage statistics."
  ];
  
  const mockTranscript = MOCK_TRANSCRIPTS[Math.floor(Math.random() * MOCK_TRANSCRIPTS.length)];
  
  // Send user transcript first
  sendToClient(ws, {
    type: 'USER_TRANSCRIPT',
    sessionId,
    transcript: mockTranscript
  });
  
  // Small delay before bot starts responding
  setTimeout(() => {
    const fullResponse = MOCK_VOICE_RESPONSES[Math.floor(Math.random() * MOCK_VOICE_RESPONSES.length)];
    const words = fullResponse.split(' ');
    
    let currentIndex = 0;
    let currentText = '';

    const streamInterval = setInterval(() => {
      if (currentIndex >= words.length) {
        clearInterval(streamInterval);
        
        // Track bot response in session history for escalation
        sessionStore.addChatMessage(sessionId, {
          sender: 'bot',
          text: fullResponse
        });
        
        sendToClient(ws, { 
          type: 'BOT_MESSAGE_END', 
          sessionId,
          fullText: fullResponse
        });
        return;
      }

      currentText += (currentIndex > 0 ? ' ' : '') + words[currentIndex];
      
      sendToClient(ws, { 
        type: 'BOT_MESSAGE', 
        sessionId,
        text: currentText,
        isPartial: currentIndex < words.length - 1
      });

      currentIndex++;
    }, config.STREAM_WORD_DELAY_MS);
  }, 500);
}

/**
 * Send mock streaming chat response when Python backend is not available
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Session ID
 * @param {string} userMessage - Original user message (for context)
 */
function sendMockChatResponse(ws, sessionId, userMessage) {
  const lowerMessage = userMessage.toLowerCase();
  
  // Keywords for maps/stations redirect
  const mapsKeywords = ['nearest station', 'swap station', 'find station', 'locate station', 'map', 'nearby station', 'closest station'];
  // Keywords for invoices redirect
  const invoiceKeywords = ['invoice', 'bill', 'payment', 'last invoice', 'billing', 'receipt'];
  
  // Check for redirect triggers
  const isMapsRequest = mapsKeywords.some(keyword => lowerMessage.includes(keyword));
  const isInvoiceRequest = invoiceKeywords.some(keyword => lowerMessage.includes(keyword));
  
  // Custom responses for redirect scenarios
  let fullResponse;
  if (isMapsRequest) {
    fullResponse = "I found nearby swap stations for you! Let me show you the map with the closest options.";
  } else if (isInvoiceRequest) {
    fullResponse = "I've pulled up your recent invoice details. Here's a quick look at your billing information.";
  } else {
    fullResponse = MOCK_CHAT_RESPONSES[Math.floor(Math.random() * MOCK_CHAT_RESPONSES.length)];
  }
  
  const words = fullResponse.split(' ');
  
  let currentIndex = 0;
  let currentText = '';

  const streamInterval = setInterval(() => {
    if (currentIndex >= words.length) {
      clearInterval(streamInterval);
      
      // Track bot response in session history for escalation
      sessionStore.addChatMessage(sessionId, {
        sender: 'bot',
        text: fullResponse
      });
      
      sendToClient(ws, { 
        type: 'CHAT_RESPONSE_END', 
        sessionId,
        fullText: fullResponse
      });
      
      // Send redirect popup after response completes
      if (isMapsRequest) {
        setTimeout(() => {
          sendToClient(ws, {
            type: 'REDIRECT_POPUP',
            redirectType: 'maps',
            sessionId
          });
        }, 300);
      } else if (isInvoiceRequest) {
        setTimeout(() => {
          sendToClient(ws, {
            type: 'REDIRECT_POPUP',
            redirectType: 'invoices',
            sessionId
          });
        }, 300);
      }
      
      return;
    }

    currentText += (currentIndex > 0 ? ' ' : '') + words[currentIndex];
    
    sendToClient(ws, { 
      type: 'CHAT_RESPONSE', 
      sessionId,
      text: currentText,
      isPartial: currentIndex < words.length - 1
    });

    currentIndex++;
  }, config.STREAM_WORD_DELAY_MS);
}

// Store for building up mock transcripts per session
const sessionTranscripts = new Map();

// Mock transcript words that build up over time
const MOCK_TRANSCRIPT_WORDS = [
  "What", "is", "the", "battery", "status", "and", "how", "much", "power", "is", "available", "right", "now"
];

/**
 * Send mock real-time transcript update as audio chunks arrive
 * @param {WebSocket} ws - WebSocket client
 * @param {string} sessionId - Session ID
 * @param {number} chunkIndex - Current chunk index
 */
function sendMockTranscriptUpdate(ws, sessionId, chunkIndex) {
  // Build transcript progressively based on chunk index
  const wordCount = Math.min(chunkIndex + 1, MOCK_TRANSCRIPT_WORDS.length);
  const transcript = MOCK_TRANSCRIPT_WORDS.slice(0, wordCount).join(' ');
  
  // Store current transcript for this session
  sessionTranscripts.set(sessionId, transcript);
  
  sendToClient(ws, {
    type: 'TRANSCRIPT_UPDATE',
    sessionId,
    transcript: transcript,
    isFinal: wordCount >= MOCK_TRANSCRIPT_WORDS.length
  });
}

/**
 * Clear transcript for a session
 * @param {string} sessionId - Session ID
 */
function clearSessionTranscript(sessionId) {
  sessionTranscripts.delete(sessionId);
}

module.exports = {
  sendMockResponse,
  sendMockChatResponse,
  sendMockTranscriptUpdate,
  clearSessionTranscript,
  MOCK_VOICE_RESPONSES,
  MOCK_CHAT_RESPONSES
};
