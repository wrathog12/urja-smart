"use client";

import React, { useRef, useState, useEffect } from "react";
import TextareaAutosize from "react-textarea-autosize";
import { FiPlus, FiArrowUp, FiX, FiFileText, FiMic, FiSquare } from "react-icons/fi";
import { HiSpeakerWave, HiSpeakerXMark } from "react-icons/hi2";

type ChatInputProps = {
  sendUserMessage: (text: string, file: File | null, ttsEnabled?: boolean) => void;
  sendVoiceMessage?: (audioBlob: Blob, voiceResponseEnabled?: boolean) => void;
  variant?: "dark" | "light";
};

const ChatInput: React.FC<ChatInputProps> = ({ sendUserMessage, sendVoiceMessage, variant = "dark" }) => {
  const [value, setValue] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const attachmentRef = useRef<File | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const hasText = value.trim().length > 0;

  // Load TTS preference from localStorage (for all messages)
  useEffect(() => {
    const saved = localStorage.getItem("ttsEnabled");
    if (saved !== null) {
      setTtsEnabled(saved === "true");
    }
  }, []);

  // Toggle TTS for all messages
  const toggleTts = () => {
    const newValue = !ttsEnabled;
    setTtsEnabled(newValue);
    localStorage.setItem("ttsEnabled", newValue.toString());
  };

  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(event.target.value);
  };

  const handleSubmit = () => {
    if (!value.trim() && !attachmentRef.current) return;
    sendUserMessage(value, attachmentRef.current, ttsEnabled);
    setValue("");
    attachmentRef.current = null;
    setFileName(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  };

  const startRecording = async () => {
    if (!sendVoiceMessage) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 48000,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      // Try different mimeTypes in order of preference
      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/webm';
      }
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/mp4';
      }
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = ''; // Use browser default
      }

      console.log('[Recording] Using mimeType:', mimeType);

      const options = mimeType ? { mimeType } : {};
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          console.log('[Recording] Audio chunk received:', event.data.size, 'bytes');
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        console.log('[Recording] Stopped. Total chunks:', audioChunksRef.current.length);

        if (audioChunksRef.current.length === 0) {
          console.error('[Recording] No audio data captured!');
          alert('No audio was recorded. Please try again.');
          stream.getTracks().forEach(track => track.stop());
          return;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType || 'audio/webm' });
        console.log('[Recording] Created blob:', audioBlob.size, 'bytes, type:', audioBlob.type);

        if (audioBlob.size === 0) {
          console.error('[Recording] Audio blob is empty!');
          alert('Recording failed. Please try again.');
          stream.getTracks().forEach(track => track.stop());
          return;
        }

        sendVoiceMessage(audioBlob, ttsEnabled);
        stream.getTracks().forEach(track => track.stop());
      };

      // Start recording with timeslice to ensure data is captured
      mediaRecorder.start(1000); // Capture data every 1 second
      setIsRecording(true);
      console.log('[Recording] Started with TTS enabled:', ttsEnabled);
    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Could not access microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleAddAttachment = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    attachmentRef.current = file;
    setFileName(file.name);
  };

  const handleRemoveFile = () => {
    attachmentRef.current = null;
    setFileName(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const isLight = variant === "light";

  return (
    <div className="w-full max-w-3xl mx-auto px-4">
      <div className={`rounded-2xl border flex flex-col justify-between px-4 py-3 min-h-18 transition-colors ${
        isLight 
          ? `bg-white shadow-sm ${isRecording ? "border-red-400" : "border-blue-400"}`
          : `bg-neutral-800 ${isRecording ? "border-red-500/50 bg-neutral-800/80" : "border-neutral-700"}`
      }`}>
        {fileName && (
          <div className={`relative inline-flex items-center gap-2 text-sm mb-2 px-2 py-2 rounded-full shadow max-w-48 ${
            isLight ? "bg-gray-100 text-gray-700" : "bg-neutral-700 text-neutral-200"
          }`}>
            <FiFileText size={16} className={isLight ? "text-gray-500" : "text-neutral-300"} />
            <span className="truncate flex-1 pr-6">{fileName}</span>
            <button
              onClick={handleRemoveFile}
              className={`absolute right-2 cursor-pointer ${isLight ? "text-gray-400 hover:text-red-500" : "text-neutral-400 hover:text-red-400"}`}
            >
              <FiX size={18} />
            </button>
          </div>
        )}

        <TextareaAutosize
          minRows={1}
          maxRows={6}
          placeholder={isRecording ? "Listening..." : "Ask me anything..."}
          className={`w-full resize-none bg-transparent outline-none text-base leading-relaxed py-1 ${
            isLight 
              ? "text-gray-700 placeholder-blue-400" 
              : "text-white placeholder-neutral-400"
          }`}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={isRecording}
        />

        <div className="mt-2 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <button
              className={`flex items-center justify-center h-8 w-8 rounded-full transition-colors duration-200 cursor-pointer ${
                isLight 
                  ? "text-gray-400 hover:text-gray-600 hover:bg-gray-100" 
                  : "text-neutral-400 hover:text-neutral-300 hover:bg-neutral-700"
              }`}
              title="Add attachment"
              type="button"
              onClick={handleAddAttachment}
              disabled={isRecording}
            >
              <FiPlus size={18} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf, .png, .jpg, .jpeg"
              style={{ display: "none" }}
              onChange={handleFileChange}
            />

            {sendVoiceMessage && (
              <button
                className={`flex items-center justify-center h-8 w-8 rounded-full transition-all duration-200 cursor-pointer ${
                  isRecording
                    ? "bg-red-500 text-white animate-pulse"
                    : isLight 
                      ? "text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                      : "text-neutral-400 hover:text-neutral-300 hover:bg-neutral-700"
                }`}
                title={isRecording ? "Stop Recording" : "Voice Chat"}
                type="button"
                onClick={isRecording ? stopRecording : startRecording}
              >
                {isRecording ? <FiSquare size={14} fill="currentColor" /> : <FiMic size={18} />}
              </button>
            )}

            <button
              className={`flex items-center justify-center h-8 w-8 rounded-full transition-all duration-200 cursor-pointer ${
                ttsEnabled
                  ? "bg-blue-500/20 text-blue-500 hover:bg-blue-500/30"
                  : isLight 
                    ? "text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                    : "text-neutral-400 hover:text-neutral-300 hover:bg-neutral-700"
              }`}
              title={ttsEnabled ? "Audio Response ON (get voice replies)" : "Audio Response OFF (text only)"}
              type="button"
              onClick={toggleTts}
              disabled={isRecording}
            >
              {ttsEnabled ? <HiSpeakerWave size={18} /> : <HiSpeakerXMark size={18} />}
            </button>
          </div>

          <div>
            <button
              className={`flex h-8 w-8 items-center justify-center rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 cursor-pointer ${
                hasText || attachmentRef.current
                  ? isLight 
                    ? "bg-blue-500 text-white hover:bg-blue-600" 
                    : "bg-white text-black hover:bg-gray-200"
                  : isLight 
                    ? "bg-gray-200 text-gray-400 hover:bg-gray-300"
                    : "bg-neutral-700 text-neutral-400 hover:bg-neutral-600"
              }`}
              title="Send message"
              onClick={handleSubmit}
              type="button"
              disabled={isRecording}
            >
              <FiArrowUp size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;