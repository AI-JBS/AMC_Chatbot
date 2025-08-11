export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  response_type?: string;
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  created_at: Date;
  user_context?: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  message_id: string;
  response_type?: string;
  timestamp: Date;
}

export interface ChatState {
  isOpen: boolean;
  isLoading: boolean;
  messages: ChatMessage[];
  sessionId: string | null;
  error: string | null;
}