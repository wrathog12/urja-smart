export type ChatMessage = {
  id: string;
  text: string;
  isUser: boolean;
  timeStamp: number;
  documentId?: string;
  filename?: string;
  audioUrl?: string;
  isLoading?: boolean;
};

export type VoiceChatResponse = {
  transcribed_text: string;
  chat_response: string;
  audio_url: string;
};

export type ChatSummary = {
  id: string;
  userId: string;
  title: string;
  lastUpdated: number;
  createdAt: number;
};
