import { VoiceChatResponse } from "@/types/chat";

export function useChatService() {
  const uploadFile = async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);

    const res = await fetch("/api/upload", {
      method: "POST",
      body: fd,
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || "Upload failed");
    }
    
    return await res.json();
  };

  const sendMessage = async (message: string, documentId: string | null) => {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: message,
        document_id: documentId,
      }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || "Chat failed");
    }

    return await res.text();
  };

  const sendVoiceChat = async (audioBlob: Blob, voiceResponseEnabled: boolean = true): Promise<VoiceChatResponse> => {
    const fd = new FormData();
    fd.append("file", audioBlob);
    fd.append("include_audio_response", voiceResponseEnabled.toString());

    console.log("[Voice] Sending to backend with include_audio_response:", voiceResponseEnabled);

    const res = await fetch("/api/voice-chat", {
      method: "POST",
      body: fd,
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || "Voice chat failed");
    }

    const response = await res.json();
    console.log("[TTS DEBUG] Voice chat response:", {
      audio_url: response.audio_url,
      has_audio: !!response.audio_url,
      errors: response.errors,
      chat_response_length: response.chat_response?.length
    });

    return response;
  };

  const synthesizeSpeech = async (text: string, language: string = "en"): Promise<{ audio_url: string }> => {
    const res = await fetch("/api/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language })
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || "TTS synthesis failed");
    }

    const data = await res.json();
    console.log("[TTS DEBUG] synthesizeSpeech result:", {
      audio_url: data.audio_url,
      has_audio: !!data.audio_url
    });

    return data;
  };

  return { sendMessage, uploadFile, sendVoiceChat, synthesizeSpeech };
}