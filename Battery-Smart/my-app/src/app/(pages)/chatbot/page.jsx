"use client";

import React from 'react';
import Chatbot from './components/chatbot';

export default function ChatbotPage() {
  return (
    <div className="h-full w-full p-4 md:p-8 bg-gray-50 flex flex-col">
      <div className="flex-1 min-h-0">
        <Chatbot />
      </div>
    </div>
  );
}
