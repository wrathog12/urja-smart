"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, User, Bot, Paperclip, MoreHorizontal, RotateCcw, PhoneForwarded, Sparkles } from 'lucide-react';
import { chatSocket } from '../services/chatSocket';
import { useRedirectPopup } from '@/context/RedirectPopupContext';

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [isEscalated, setIsEscalated] = useState(false);
  const scrollRef = useRef(null);
  const { showPopup } = useRedirectPopup();
  
  // Use ref to avoid stale closure in useEffect
  const showPopupRef = useRef(showPopup);
  useEffect(() => {
    showPopupRef.current = showPopup;
  }, [showPopup]);

  const hasMessages = messages.length > 0;

  useEffect(() => {
    chatSocket.connect();
    chatSocket.startSession(`c-${Date.now()}`);

    chatSocket.onChatResponse((text, isPartial) => {
      setStreamingText(text);
      if (!isPartial) {
        setIsTyping(false);
      }
    });

    chatSocket.onChatResponseEnd((fullText) => {
      const aiResponse = {
        id: Date.now(),
        text: fullText,
        sender: 'ai'
      };
      setMessages(prev => [...prev, aiResponse]);
      setStreamingText('');
      setIsTyping(false);
    });

    chatSocket.onChatProcessing(() => {
      setIsTyping(true);
    });

    chatSocket.onError((error) => {
      console.error('Chat socket error:', error);
      setIsTyping(false);
      setStreamingText('');
    });

    chatSocket.onEscalation((data) => {
      setIsEscalated(true);
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: data.message || 'Your conversation has been escalated to an agent. Please wait...',
        sender: 'system'
      }]);
    });

    // Listen for redirect popup events
    chatSocket.onRedirectPopup((redirectType) => {
      console.log('Redirect popup callback fired:', redirectType);
      showPopupRef.current(redirectType);
    });

    return () => {
      chatSocket.endSession();
      chatSocket.disconnect();
    };
  }, []);


  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping, streamingText]);

  const handleSend = useCallback(() => {
    if (!inputValue.trim()) return;

    const messageId = `msg-${Date.now()}`;
    const userMessage = {
      id: messageId,
      text: inputValue,
      sender: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    chatSocket.sendMessage(inputValue, messageId);
  }, [inputValue]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleReset = () => {
    setMessages([]);
    setStreamingText('');
    setIsTyping(false);
    setIsEscalated(false);
  };

  const handleEscalate = () => {
    chatSocket.triggerEscalation('User requested to speak with an agent');
  };



  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header - only show when there are messages */}
      {hasMessages && (
        <div className="px-6 py-3 border-b border-gray-200 bg-white flex items-center justify-between rounded-xl">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-green-500 flex items-center justify-center text-white">
              <Bot size={20} />
            </div>
            <div>
              <h2 className="font-semibold text-gray-800 text-sm">Battery Smart Assistant</h2>
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
                <span className="text-[10px] text-gray-500 font-medium uppercase tracking-wider">Online</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
             <button
               onClick={handleEscalate}
               disabled={isEscalated}
               className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                 isEscalated 
                   ? 'bg-orange-100 text-orange-600 cursor-not-allowed'
                   : 'bg-red-50 text-red-600 hover:bg-red-100'
               }`}
               title="Escalate to Agent"
             >
               <PhoneForwarded size={14} />
               {isEscalated ? 'Escalated' : 'Talk to Agent'}
             </button>
             <button 
               onClick={handleReset}
               className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500" 
               title="Reset chat"
             >
               <RotateCcw size={16} />
             </button>
             <button className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-500">
               <MoreHorizontal size={16} />
             </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      {!hasMessages ? (
        /* Empty State - Centered Input */
        <div className="flex-1 flex flex-col items-center justify-center px-6">
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-green-500 flex items-center justify-center text-white mx-auto mb-4 shadow-lg">
              <Sparkles size={32} />
            </div>
            <h1 className="text-2xl font-semibold text-gray-800 mb-2">
              How can I help you today?
            </h1>
            <p className="text-gray-500">
              Ask me anything about Battery Smart services
            </p>
          </div>

          {/* Centered Input */}
          <div className="w-full max-w-2xl mx-auto">
            <div className="relative">
              <input
                type="text"
                placeholder="Ask me anything about Battery Smart..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                className="w-full bg-white border border-blue-400 rounded-xl px-5 py-3 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-[0.95rem] text-gray-700 shadow-sm"
                style={{ '::placeholder': { color: '#60a5fa' } }}
              />
              <style jsx>{`
                input::placeholder {
                  color: #60a5fa;
                }
              `}</style>
              <button 
                onClick={handleSend}
                disabled={!inputValue.trim() || isTyping}
                className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all duration-200 flex items-center justify-center
                  ${!inputValue.trim() || isTyping 
                    ? 'text-blue-300 cursor-not-allowed' 
                    : 'text-blue-500 hover:bg-blue-50 active:scale-95'}
                `}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Chat State - Messages + Bottom Input */
        <>
          {/* Messages Area */}
          <div 
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-6 space-y-4 scroll-smooth"
          >
            {messages.map((msg) => (
            <div 
              key={msg.id} 
              className={`flex ${msg.sender === 'user' ? 'justify-end' : msg.sender === 'system' ? 'justify-center' : 'justify-start'}`}
            >
              {msg.sender === 'system' ? (
                <div className="px-4 py-2 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">
                  {msg.text}
                </div>
              ) : (
              <div className={`flex gap-3 max-w-[80%] ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white
                  ${msg.sender === 'user' ? 'bg-gray-600' : 'bg-green-500'}
                `}>
                  {msg.sender === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className={`px-4 py-3 rounded-2xl
                  ${msg.sender === 'user' 
                    ? 'bg-green-500 text-white rounded-tr-none' 
                    : 'bg-white text-gray-700 rounded-tl-none border border-gray-200'}
                `}>
                  <p className="text-[0.95rem] leading-relaxed">{msg.text}</p>
                </div>
              </div>
              )}
            </div>
          ))}

          {/* Streaming response or typing indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex gap-3 max-w-[80%]">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white">
                  <Bot size={16} />
                </div>
                <div className="px-4 py-3 bg-white border border-gray-200 rounded-2xl rounded-tl-none">
                  {streamingText ? (
                    <p className="text-[0.95rem] leading-relaxed text-gray-700">
                      {streamingText}
                      <span className="animate-pulse ml-1">▊</span>
                    </p>
                  ) : (
                    <div className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce"></div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          </div>

          {/* Bottom Input Area */}
          <div>
            <div className="w-full max-w-4xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Ask me anything about Battery Smart..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  className="w-full bg-white border border-blue-400 rounded-xl px-5 py-3 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-[0.95rem] text-gray-700 shadow-sm"
                  style={{ '::placeholder': { color: '#60a5fa' } }}
                />
                <style jsx>{`
                  input::placeholder {
                    color: #60a5fa;
                  }
                `}</style>
                <button 
                  onClick={handleSend}
                  disabled={!inputValue.trim() || isTyping}
                  className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all duration-200 flex items-center justify-center
                    ${!inputValue.trim() || isTyping 
                      ? 'text-blue-300 cursor-not-allowed' 
                      : 'text-blue-500 hover:bg-blue-50 active:scale-95'}
                  `}
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
