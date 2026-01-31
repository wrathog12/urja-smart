"use client";

import ChatInput from "@/components/ChatInput";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { useChatService } from "@/services/useChatService";
import { LuSparkles } from "react-icons/lu";

export default function Home() {
  const router = useRouter();
  const [isPreparing, setIsPreparing] = useState(false);
  
  // Destructure the services we need
  const { uploadFile, sendVoiceChat } = useChatService();

  // --- Scenario 1: TEXT Input (Deferred to Chat Page) ---
  const handleSend = async (text: string, file: File | null) => {
    if (!text.trim() && !file) return;
    setIsPreparing(true);

    const sessionId = crypto.randomUUID();
    let documentId: string | null = null;
    let filename: string | null = null;

    try {
      // If there is a PDF, upload it NOW to get the ID
      if (file) {
        if (file.type !== "application/pdf") {
          console.warn("Only PDF files are expected.");
        }
        filename = file.name;
        const uploadRes = await uploadFile(file);
        documentId = uploadRes.document_id;
      }

      // Save intent to session storage (Text flow triggers API on next page)
      window.sessionStorage.setItem(
        `first-message-${sessionId}`,
        JSON.stringify({
          type: "text_intent", // Marker
          text,
          documentId,
          filename,
        })
      );

      router.push(`/chat/${sessionId}/`);
    } catch (err) {
      console.error("Failed to initialize chat:", err);
      setIsPreparing(false);
    }
  };

  // --- Scenario 2: VOICE Input (Executed Immediately) ---
  const handleVoice = async (audioBlob: Blob) => {
    setIsPreparing(true);
    const sessionId = crypto.randomUUID();

    try {
      // 1. Send Audio to /voice-chat immediately
      const data = await sendVoiceChat(audioBlob);

      // 2. Store the COMPLETED result in session storage
      // We pass the response data so the Chat Page just has to render it
      window.sessionStorage.setItem(
        `first-message-${sessionId}`,
        JSON.stringify({
          type: "voice_result", // Marker
          userText: data.transcribed_text,
          botText: data.chat_response,
          audioUrl: data.audio_url
        })
      );

      // 3. Redirect
      router.push(`/chat/${sessionId}/`);

    } catch (err) {
      console.error("Failed to process voice on home:", err);
      setIsPreparing(false);
      alert("Voice processing failed. Please try again.");
    }
  };

  return (
    <div className="h-screen w-screen bg-gray-50">
      <main className="h-full">
        <div className="h-full flex flex-col items-center justify-center px-4">
          {/* Logo/Icon */}
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white mx-auto mb-4 shadow-lg">
            <LuSparkles size={32} />
          </div>
          
          {/* Title */}
          <h1 className="text-2xl font-semibold text-gray-800 mb-2">
            How can I help you today?
          </h1>
          <p className="text-gray-500 mb-8">
            Ask me anything about our services
          </p>

          {/* Loading State */}
          {isPreparing && (
            <p className="text-sm text-blue-500 mb-4 animate-pulse">
              Setting up your workspace...
            </p>
          )}

          {/* Chat Input */}
          <div className="w-full max-w-2xl">
            <ChatInput 
              sendUserMessage={handleSend} 
              sendVoiceMessage={handleVoice}
              variant="light"
            />
          </div>
        </div>
      </main>
    </div>
  );
}