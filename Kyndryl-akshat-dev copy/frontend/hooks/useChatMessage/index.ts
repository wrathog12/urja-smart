import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/types/chat";
import { useChatService } from "@/services/useChatService";

function generateId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

function parseBackendResponse(rawResponse: string): string {
  try {
    const data = JSON.parse(rawResponse);
    const responseText = data.response || data.answer || data.content || JSON.stringify(data);
    return responseText.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  } catch {
    return rawResponse;
  }
}

export function useChatMessage(initialMessages: ChatMessage[] = []) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);
  const { sendMessage, uploadFile, sendVoiceChat, synthesizeSpeech } = useChatService();
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  const addMessage = (msg: ChatMessage) =>
    setMessages((prev) => [...prev, msg]);

  const sendUserMessage = async (
    text: string,
    file: File | null,
    ttsEnabled?: boolean,
    filenameOverride?: string,
    explicitDocId?: string
  ) => {
    const displayFilename = file ? file.name : filenameOverride;

    const userMsg: ChatMessage = {
      id: generateId(),
      text,
      isUser: true,
      timeStamp: Date.now(),
      ...(displayFilename ? { filename: displayFilename } : {}),
    };
    addMessage(userMsg);

    const botMsgId = generateId();
    addMessage({
      id: botMsgId,
      text: "",
      isUser: false,
      timeStamp: Date.now(),
      isLoading: true,
    });

    try {
      let docIdToUse = explicitDocId || activeDocumentId;

      if (file) {
        const uploadRes = await uploadFile(file);
        docIdToUse = uploadRes.document_id;
        setActiveDocumentId(docIdToUse);
      } else if (explicitDocId) {
        setActiveDocumentId(explicitDocId);
      }

      const finalDocId = docIdToUse || null;

      const rawResponse = await sendMessage(text, finalDocId);
      const botResponseText = parseBackendResponse(rawResponse);

      // Update message with text first
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botMsgId
            ? { ...m, text: botResponseText, isLoading: false }
            : m
        )
      );

      // Generate TTS if enabled
      if (ttsEnabled && botResponseText) {
        console.log("[TTS DEBUG] TTS enabled, synthesizing bot response");
        try {
          const ttsResult = await synthesizeSpeech(botResponseText);
          console.log("[TTS DEBUG] TTS synthesis complete, updating message with audio URL");

          // Update message with audio URL
          setMessages((prev) =>
            prev.map((m) =>
              m.id === botMsgId
                ? { ...m, audioUrl: ttsResult.audio_url }
                : m
            )
          );
        } catch (ttsErr) {
          console.error("[TTS DEBUG] TTS synthesis failed:", ttsErr);
          // Don't fail the whole message if TTS fails
        }
      }
    } catch (err) {
      console.error("Chat Error:", err);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botMsgId
            ? {
                ...m,
                text: "Error: Something went wrong. Please try again.",
                isLoading: false
              }
            : m
        )
      );
    }
  };

  const sendVoiceMessage = async (audioBlob: Blob, voiceResponseEnabled: boolean = true) => {
    const tempUserMsgId = generateId();
    addMessage({
      id: tempUserMsgId,
      text: "🎤 Sending audio...",
      isUser: true,
      timeStamp: Date.now(),
    });

    const botMsgId = generateId();
    addMessage({
      id: botMsgId,
      text: "",
      isUser: false,
      timeStamp: Date.now(),
      isLoading: true,
    });

    try {
      console.log("[Voice] Sending voice message with voiceResponseEnabled:", voiceResponseEnabled);
      const response = await sendVoiceChat(audioBlob, voiceResponseEnabled);

      setMessages((prev) =>
        prev.map((m) =>
            m.id === tempUserMsgId
            ? { ...m, text: response.transcribed_text || "🎤 [Audio Message]" }
            : m
        )
      );

      console.log("[TTS DEBUG] Setting bot message with audio URL:", {
        audio_url: response.audio_url,
        has_audio_url: !!response.audio_url,
        errors: response.errors
      });

      setMessages((prev) =>
        prev.map((m) =>
          m.id === botMsgId
            ? {
                ...m,
                text: response.chat_response,
                audioUrl: response.audio_url,
                isLoading: false
              }
            : m
        )
      );
    } catch (err) {
      console.error("Voice Chat Error:", err);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botMsgId 
          ? { ...m, text: "Error processing voice message.", isLoading: false } 
          : m
        )
      );
    }
  };

  const restoreSession = (userText: string, botText: string, audioUrl?: string) => {
    const userMsgId = generateId();
    const botMsgId = generateId();
    const now = Date.now();

    const restoredMessages: ChatMessage[] = [
      {
        id: userMsgId,
        text: userText,
        isUser: true,
        timeStamp: now,
      },
      {
        id: botMsgId,
        text: botText,
        isUser: false,
        timeStamp: now + 1,
        audioUrl: audioUrl,
        isLoading: false,
      },
    ];

    setMessages((prev) => [...prev, ...restoredMessages]);
  };

  const regenerateMessage = (msg: ChatMessage) => {
    if (!msg.isUser) {
      const idx = messages.findIndex((m) => m.id === msg.id);
      if (idx > 0) {
        const lastUserMsg = messages[idx - 1];
        if (lastUserMsg.isUser) {
          sendUserMessage(lastUserMsg.text, null);
        }
      }
    }
  };

  const setDocumentId = (id: string) => setActiveDocumentId(id);

  return { 
    messages, 
    sendUserMessage, 
    sendVoiceMessage, 
    containerRef, 
    regenerateMessage,
    setDocumentId,
    restoreSession
  };
}