"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import VoiceAgent from "./components/voice-agent";
import { useRedirectPopup } from "@/context/RedirectPopupContext";
import { voiceSocket } from "./services/voiceSocket";
import {
  initializeStationData,
  resetStationDataCache,
} from "./services/stationService";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function HomePage() {
  // Bot states: 'idle' | 'connecting' | 'listening' | 'processing' | 'speaking'
  const [botState, setBotState] = useState("idle");
  const [speakingIntensity, setSpeakingIntensity] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [userTranscript, setUserTranscript] = useState("");
  const [botResponse, setBotResponse] = useState("");
  const [isEscalated, setIsEscalated] = useState(false);
  const [voicePersona, setVoicePersona] = useState("female");
  const [sentiment, setSentiment] = useState(0.7);
  const [connectionError, setConnectionError] = useState(null);

  const voiceAgentRef = useRef(null);
  const speakingIntervalRef = useRef(null);
  const { showPopup } = useRedirectPopup();
  const router = useRouter();

  // Cleanup function
  const cleanup = useCallback(async () => {
    console.log("🧹 Running cleanup...");

    // Disconnect socket (this stops its internal polling too)
    voiceSocket.disconnect();

    // Reset backend session
    try {
      await fetch(`${BACKEND_URL}/api/session/reset`, { method: "POST" });
    } catch (e) {
      console.warn("Failed to reset backend session:", e);
    }

    // Reset frontend state
    setIsConnected(false);
    setBotState("idle");
    setUserTranscript("");
    setBotResponse("");
    setIsEscalated(false);
    setSentiment(0.7);
    setConnectionError(null);
  }, []);

  // Initialize voiceSocket callbacks
  useEffect(() => {
    // State change handler
    voiceSocket.onStateChange((state) => {
      console.log("📡 Voice socket state:", state);
      if (state === "connected") {
        setIsConnected(true);
        setBotState("listening");
        setConnectionError(null);
      } else if (state === "disconnected") {
        setIsConnected(false);
        // Don't auto-set to idle here - let cleanup handle it
      } else if (state === "listening") {
        setBotState("listening");
      } else if (state === "processing") {
        setBotState("processing");
      } else if (state === "speaking") {
        setBotState("speaking");
      }
    });

    // Transcript handler
    voiceSocket.onTranscript((transcript) => {
      console.log("📝 Transcript:", transcript);
      setUserTranscript(transcript);
      setBotState("processing");
    });

    // Bot response handler
    voiceSocket.onBotResponse((response) => {
      console.log("🤖 Bot response:", response);
      setBotResponse(response);
      setBotState("speaking");

      // Return to listening after speaking
      setTimeout(() => {
        setBotState("listening");
      }, 3000);
    });

    // Tool activation handler
    voiceSocket.onToolActivation((tool) => {
      console.log("🔧 Tool activated in page.jsx:", tool);
      console.log("🔧 Tool name:", tool?.name);
      if (tool?.name === "escalate_to_agent") {
        console.log("🚨 ESCALATION TOOL DETECTED in page.jsx!");
        setIsEscalated(true);
        setBotState("idle"); // Stop the bot immediately

        // Send escalation to socket server with full conversation history
        const reason = tool.args?.reason || "Agent requested by voice bot";
        console.log("🚨 Triggering escalation with reason:", reason);
        voiceSocket.triggerEscalation(reason);

        // Disconnect after a short delay to allow escalation message to send
        setTimeout(() => {
          console.log("🔌 Disconnecting after escalation...");
          voiceSocket.disconnect();
        }, 2000);
      }

      // Handle show_directions tool - redirect to maps page
      if (tool?.name === "show_directions") {
        console.log("🗺️ SHOW DIRECTIONS TOOL DETECTED - redirecting to maps");
        // Redirect to maps page after a short delay (let audio play first)
        setTimeout(() => {
          console.log("🗺️ Redirecting to /maps");
          router.push("/maps");
        }, 2500);
      }
    });

    // Call end handler
    voiceSocket.onCallEnd((reason) => {
      console.log("📞 Call ended:", reason);
      if (reason === "issue_resolved") {
        if (showPopupRef.current) {
          showPopupRef.current("feedback");
        }
      }
      // Delay cleanup to let final audio play
      setTimeout(() => {
        cleanup();
      }, 2000);
    });

    // Error handler
    voiceSocket.onError((error) => {
      console.error("❌ Voice socket error:", error);
      setConnectionError(error.message || "Connection failed");
      setBotState("idle");
    });

    // Cleanup on unmount
    return () => {
      cleanup();
    };
  }, [cleanup]);

  // Initialize station data on page load (single call, cached)
  useEffect(() => {
    console.log("🗺️ Initializing station data...");
    initializeStationData()
      .then((result) => {
        if (result.success) {
          console.log(`✅ Station data ready: ${result.stationCount} stations`);
        } else {
          console.warn("⚠️ Station data init failed:", result.error);
        }
      })
      .catch((error) => {
        console.error("❌ Station data init error:", error);
      });

    // Reset cache when leaving the page
    return () => {
      resetStationDataCache();
    };
  }, []);

  // Simulate speaking intensity when bot is speaking
  useEffect(() => {
    if (botState === "speaking") {
      speakingIntervalRef.current = setInterval(() => {
        const intensity = 0.3 + Math.random() * 0.5;
        setSpeakingIntensity(intensity);
      }, 100);
    } else {
      setSpeakingIntensity(0);
      if (speakingIntervalRef.current) {
        clearInterval(speakingIntervalRef.current);
        speakingIntervalRef.current = null;
      }
    }

    return () => {
      if (speakingIntervalRef.current) {
        clearInterval(speakingIntervalRef.current);
      }
    };
  }, [botState]);

  // Connect and start session
  const handleStartBot = async () => {
    console.log("🎯 handleStartBot called, current state:", botState);

    if (botState !== "idle") {
      // If already active, stop the session
      console.log("⏹️ Stopping session...");
      try {
        await fetch(`${BACKEND_URL}/api/session/end`, { method: "POST" });
      } catch (e) {
        console.warn("Failed to end session:", e);
      }
      cleanup();
      return;
    }

    setBotState("connecting");
    setConnectionError(null);

    // Reset backend session first
    console.log("🔄 Resetting backend session...");
    try {
      await fetch(`${BACKEND_URL}/api/session/reset`, { method: "POST" });
    } catch (e) {
      console.warn("Failed to reset backend session:", e);
      setConnectionError("Backend not available");
      setBotState("idle");
      return;
    }

    // Small delay to ensure reset is complete
    await new Promise((r) => setTimeout(r, 500));

    // Connect to WebRTC
    console.log("🔌 Connecting to WebRTC...");
    const connected = await voiceSocket.connect();
    console.log("🔌 Connection result:", connected);

    if (!connected) {
      console.error("❌ WebRTC connection failed");
      setConnectionError(
        "WebRTC connection failed. Check microphone permissions.",
      );
      setBotState("idle");
      return;
    }

    // Start the session
    console.log("▶️ Starting voice session...");
    voiceSocket.startSession();
    setBotState("listening");
    setIsConnected(true);
  };

  // Handle voice persona switch
  const handlePersonaSwitch = async () => {
    const newPersona = voicePersona === "male" ? "female" : "male";
    try {
      await voiceSocket.setVoicePersona(newPersona);
      setVoicePersona(newPersona);
    } catch (error) {
      console.error("Failed to switch persona:", error);
    }
  };

  // Handle escalation
  const handleEscalate = async () => {
    setIsEscalated(true);
    try {
      await fetch(`${BACKEND_URL}/api/session/end`, { method: "POST" });
    } catch (e) {
      console.warn("Failed to end session:", e);
    }
    setTimeout(() => {
      cleanup();
    }, 2000);
  };

  // Map 'processing' to 'thinking' for VoiceAgent component
  const voiceAgentState = botState === "processing" ? "thinking" : botState;

  // Sentiment indicator color
  const getSentimentColor = () => {
    if (sentiment >= 0.7) return "bg-green-500";
    if (sentiment >= 0.5) return "bg-yellow-500";
    if (sentiment >= 0.3) return "bg-orange-500";
    return "bg-red-500";
  };

  return (
    <div className="min-h-full bg-white flex flex-col items-center justify-center">
      {/* Main content */}
      <div className="flex flex-col items-center">
        {/* Title */}
        <h1 className="text-5xl font-semibold text-gray-800">Urja Bot</h1>
        <p className="text-gray-500 mt-1">Battery Smart Voice Assistant</p>

        {/* Connection Error Display */}
        {connectionError && (
          <div className="mt-4 px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm">
            ❌ {connectionError}
          </div>
        )}

        {/* Voice Persona Toggle */}
        <div className="mt-4 flex items-center gap-2">
          <span className="text-sm text-gray-500">Voice:</span>
          <button
            onClick={handlePersonaSwitch}
            disabled={botState !== "idle"}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
              voicePersona === "male"
                ? "bg-blue-100 text-blue-700"
                : "bg-pink-100 text-pink-700"
            } ${botState !== "idle" ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            {voicePersona === "male" ? "👨 Male" : "👩 Female"}
          </button>
        </div>

        {/* Voice Agent Orb */}
        <div className="">
          <VoiceAgent
            ref={voiceAgentRef}
            state={voiceAgentState}
            speakingIntensity={speakingIntensity}
          />
        </div>

        {/* Sentiment Indicator (only show during call) */}
        {botState !== "idle" && botState !== "connecting" && (
          <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-gray-500">User Mood:</span>
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${getSentimentColor()}`}
              ></div>
              <span className="text-sm font-medium">
                {sentiment >= 0.7
                  ? "😊 Happy"
                  : sentiment >= 0.5
                    ? "😐 Neutral"
                    : sentiment >= 0.3
                      ? "😟 Frustrated"
                      : "😠 Angry"}
              </span>
            </div>
          </div>
        )}

        {/* User Transcript Display */}
        {userTranscript && (
          <div className="mt-4 max-w-md text-center">
            <p className="text-sm text-gray-500 mb-1">You said:</p>
            <p className="text-gray-700 font-medium">"{userTranscript}"</p>
          </div>
        )}

        {/* Bot Response Display */}
        {botResponse && (
          <div className="mt-2 max-w-md text-center">
            <p className="text-sm text-gray-500 mb-1">Urja:</p>
            <p className="text-green-700 font-medium">"{botResponse}"</p>
          </div>
        )}

        {/* Escalation Banner */}
        {isEscalated && (
          <div className="mt-4 px-6 py-3 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">
            Connecting you to an agent... Please wait.
          </div>
        )}

        {/* Start/Stop Button & ChatBot Button */}
        <div className="flex items-center gap-4 mt-6">
          {/* Start/Stop Talking Button */}
          <button
            onClick={handleStartBot}
            disabled={botState === "connecting"}
            className={`
              px-4 py-2 rounded-full font-medium text-white text-lg
              transition-all duration-200
              ${
                botState === "connecting"
                  ? "bg-yellow-400 cursor-wait"
                  : botState === "idle"
                    ? "bg-green-500 hover:bg-green-600 active:scale-95"
                    : "bg-red-500 hover:bg-red-600 active:scale-95"
              }
            `}
          >
            <span className="flex items-center gap-3">
              {botState === "connecting" ? (
                <>
                  <svg
                    className="animate-spin h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Connecting...
                </>
              ) : botState === "idle" ? (
                <>
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  </svg>
                  Start Talking
                </>
              ) : (
                <>
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
                    />
                  </svg>
                  Stop
                </>
              )}
            </span>
          </button>

          {/* ChatBot Button */}
          <a href="http://localhost:4002">
            <button className="px-4 py-2 rounded-full font-medium text-white text-lg bg-blue-500 hover:bg-blue-600 active:scale-95 transition-all duration-200">
              <span className="flex items-center gap-3">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
                ChatBot
              </span>
            </button>
          </a>
        </div>

        {/* Status Indicator */}
        {botState !== "idle" && botState !== "connecting" && (
          <div className="mt-4">
            <div className="px-4 py-2 rounded-full bg-gray-50 border border-gray-200">
              <span className="flex items-center gap-3 text-gray-600 font-medium">
                {botState === "listening" && (
                  <>
                    <span className="relative flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-300 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-400"></span>
                    </span>
                    Listening...
                  </>
                )}
                {botState === "processing" && (
                  <>
                    <svg
                      className="animate-spin h-5 w-5 text-green-500"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Processing...
                  </>
                )}
                {botState === "speaking" && (
                  <>
                    <span className="flex gap-1">
                      <span className="w-1 h-4 bg-green-500 rounded animate-pulse"></span>
                      <span
                        className="w-1 h-4 bg-emerald-400 rounded animate-pulse"
                        style={{ animationDelay: "0.1s" }}
                      ></span>
                      <span
                        className="w-1 h-4 bg-green-500 rounded animate-pulse"
                        style={{ animationDelay: "0.2s" }}
                      ></span>
                    </span>
                    Urja is speaking...
                  </>
                )}
              </span>
            </div>
          </div>
        )}

        {/* Escalate Button */}
        <div className="mt-4">
          <button
            onClick={handleEscalate}
            disabled={isEscalated || botState === "idle"}
            className={`px-4 py-2 rounded-full font-medium text-sm transition-all duration-200 ${
              isEscalated
                ? "bg-orange-100 text-orange-600 cursor-not-allowed"
                : botState === "idle"
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                  : "bg-red-50 text-red-600 hover:bg-red-100"
            }`}
          >
            {isEscalated ? "Escalated to Agent" : "Talk to Agent"}
          </button>
        </div>
      </div>
    </div>
  );
}
