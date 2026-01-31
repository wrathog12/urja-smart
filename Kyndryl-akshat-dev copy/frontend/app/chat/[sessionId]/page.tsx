"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useChatMessage } from "@/hooks/useChatMessage"; 
import { ChatMessage } from "@/types/chat";
import ChatInput from "@/components/ChatInput";
import { FiFileText, FiUser, FiMoreHorizontal } from "react-icons/fi";
import { MdReplay } from "react-icons/md";
import { FaRegCopy, FaRobot } from "react-icons/fa";
import { LuCheck, LuSparkles, LuRotateCcw } from "react-icons/lu";

export default function ChatPage() {
  const { sessionId } = useParams();
   
  const { 
    messages, 
    sendUserMessage, 
    sendVoiceMessage, 
    containerRef, 
    regenerateMessage, 
    setDocumentId,
    restoreSession
  } = useChatMessage();

  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});
  const hasMessages = messages.length > 0;

  useEffect(() => {
    const key = `first-message-${sessionId}`;
    const raw = sessionStorage.getItem(key);
    if (!raw) return;

    try {
      const parsed = JSON.parse(raw);
      if (parsed.type === "voice_result") {
        restoreSession(parsed.userText, parsed.botText, parsed.audioUrl);
      } else if (parsed.text || parsed.type === "text_intent") {
        sendUserMessage(parsed.text, null, undefined, parsed.filename, parsed.documentId);
      } else if (parsed.documentId) {
        setDocumentId(parsed.documentId);
      }
    } catch (err) {
      console.error("Failed to restore initial message:", err);
    } finally {
      sessionStorage.removeItem(key);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]); 

  const copyMessage = (text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedStates((s) => ({ ...s, [id]: true }));
      setTimeout(() => {
        setCopiedStates((s) => ({ ...s, [id]: false }));
      }, 1500);
    });
  };

  const handleReset = () => {
    window.location.reload();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header - only show when there are messages */}
      {hasMessages && (
        <div className="px-6 py-3 border-b border-gray-200 bg-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white shadow-lg">
              <FaRobot size={18} />
            </div>
            <div>
              <h2 className="font-semibold text-gray-800 text-sm">Urja AI Assistant</h2>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
                <span className="text-[10px] text-gray-500 font-medium uppercase tracking-wider">Online</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={handleReset}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500" 
              title="Reset chat"
            >
              <LuRotateCcw size={16} />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500">
              <FiMoreHorizontal size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      {!hasMessages ? (
        /* Empty State - Centered Welcome */
        <div className="flex-1 flex flex-col items-center justify-center px-6">
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white mx-auto mb-4 shadow-lg">
              <LuSparkles size={32} />
            </div>
            <h1 className="text-2xl font-semibold text-gray-800 mb-2">
              How can I help you today?
            </h1>
            <p className="text-gray-500">
              Ask me anything about our services
            </p>
          </div>

          {/* Centered Input */}
          <div className="w-full max-w-2xl mx-auto">
            <ChatInput 
              sendUserMessage={(text, file) => sendUserMessage(text, file)} 
              sendVoiceMessage={sendVoiceMessage} 
              variant="light"
            />
          </div>
        </div>
      ) : (
        /* Chat State - Messages + Bottom Input */
        <>
          {/* Messages Area */}
          <div
            ref={containerRef}
            className="flex-1 overflow-y-auto p-6 space-y-4 scroll-smooth"
          >
            {messages.map((msg: ChatMessage) => (
              <div
                key={msg.id}
                className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${msg.isUser ? "flex-row-reverse" : ""}`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white shadow-md
                    ${msg.isUser ? "bg-gray-600" : "bg-gradient-to-br from-blue-500 to-blue-600"}`}
                  >
                    {msg.isUser ? <FiUser size={14} /> : <FaRobot size={14} />}
                  </div>

                  <div className="space-y-2">
                    {msg.isLoading ? (
                      <div className="px-4 py-3 bg-white border border-gray-200 rounded-2xl rounded-tl-none shadow-sm">
                        <div className="flex items-center gap-1">
                          <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '-0.3s' }}></div>
                          <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '-0.15s' }}></div>
                          <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce"></div>
                        </div>
                      </div>
                    ) : (
                      <div
                        className={`px-4 py-3 rounded-2xl shadow-sm break-words ${
                          msg.isUser
                            ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-tr-none"
                            : "bg-white text-gray-700 border border-gray-200 rounded-tl-none"
                        }`}
                      >
                        <p
                          className="text-[0.95rem] leading-relaxed whitespace-pre-wrap break-words"
                          dangerouslySetInnerHTML={{ __html: msg.text }}
                        ></p>
                        {msg.audioUrl && (
                          <div className="mt-3 bg-gray-100 p-2 rounded-lg">
                            <audio
                              autoPlay
                              controls
                              src={msg.audioUrl}
                              className="w-full h-8 max-w-[250px]"
                              onError={(e) => {
                                const target = e.currentTarget as HTMLAudioElement;
                                const error = target.error;
                                console.error("[TTS DEBUG] Audio playback failed:");
                                console.error("[TTS DEBUG] Error code:", error?.code);
                                console.error("[TTS DEBUG] Error message:", error?.message);
                              }}
                            />
                          </div>
                        )}
                        {msg.filename && msg.isUser && (
                          <div className="inline-flex items-center gap-2 text-sm text-white/90 mt-2 bg-white/20 px-2 py-1.5 rounded-full max-w-48">
                            <FiFileText size={14} />
                            <span className="truncate flex-1">{msg.filename}</span>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Action buttons for bot messages */}
                    {!msg.isUser && !msg.isLoading && (
                      <div className="flex gap-1 pl-1">
                        <button
                          className="bg-transparent hover:bg-gray-100 text-gray-400 hover:text-gray-600 p-1.5 rounded-lg transition-all cursor-pointer"
                          onClick={() => regenerateMessage(msg)}
                          title="Regenerate message"
                        >
                          <MdReplay size={14} />
                        </button>

                        <button
                          className="bg-transparent hover:bg-gray-100 text-gray-400 hover:text-gray-600 p-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1"
                          onClick={() => copyMessage(msg.text, msg.id)}
                          title="Copy message"
                        >
                          {copiedStates[msg.id] ? (
                            <>
                              <LuCheck size={14} />
                              <span className="text-xs">Copied</span>
                            </>
                          ) : (
                            <FaRegCopy size={14} />
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom Input Area */}
          <div className="p-4 border-t border-gray-200 bg-white">
            <ChatInput 
              sendUserMessage={(text, file) => sendUserMessage(text, file)} 
              sendVoiceMessage={sendVoiceMessage}
              variant="light"
            />
          </div>
        </>
      )}
    </div>
  );
}