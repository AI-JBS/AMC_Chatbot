import { useState, useCallback, useRef, useEffect } from 'react';
import { ChatMessage, ChatState } from '@/types/chat';
import { chatAPI } from '@/utils/api';
// Simple UUID generator for browser environments
const generateUUID = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

export const useChat = () => {
  const [state, setState] = useState<ChatState>({
    isOpen: false,
    isLoading: false,
    messages: [],
    sessionId: null,
    error: null,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const initialized = useRef(false);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, scrollToBottom]);

  // Initialize chat immediately when hook mounts (page load)
  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;
      const sessionId = generateUUID();
      const welcomeMessage = generateWelcomeMessage();
      
      setState(prev => ({
        ...prev,
        messages: [welcomeMessage],
        sessionId: sessionId,
      }));

      // Optional: Pre-warm the backend connection
      chatAPI.healthCheck().catch(console.error);
    }
  }, []);

  // Generate welcome message for new sessions
  const generateWelcomeMessage = (): ChatMessage => ({
    id: generateUUID(),
    role: 'assistant',
    content: `Hey there! 👋 I'm your AI financial advisor, ready to help with mutual funds. What can I help you with? 📊`,
    timestamp: new Date(),
  });

  // Toggle chat widget (now just opens/closes since chat is pre-initialized)
  const toggleChat = useCallback(() => {
    setState(prev => ({ ...prev, isOpen: !prev.isOpen }));
  }, []);

  // Send message to backend
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || state.isLoading) return;

    const userMessage: ChatMessage = {
      id: generateUUID(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    // Add user message immediately
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      const response = await chatAPI.sendMessage({
        message: content.trim(),
        session_id: state.sessionId || undefined,
        user_context: {
          timestamp: new Date().toISOString(),
          platform: 'web',
        },
      });

      const assistantMessage: ChatMessage = {
        id: response.message_id,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        response_type: response.response_type,
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        sessionId: response.session_id,
        isLoading: false,
      }));

    } catch (error) {
      const errorMessage: ChatMessage = {
        id: generateUUID(),
        role: 'assistant',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment. 🔄",
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      }));
    }
  }, [state.isLoading, state.sessionId]);

  // Clear chat session
  const clearChat = useCallback(async () => {
    try {
      if (state.sessionId) {
        await chatAPI.clearSession(state.sessionId);
      }
    } catch (error) {
      console.error('Error clearing session:', error);
    }

    setState(prev => ({
      ...prev,
      messages: [generateWelcomeMessage()],
      sessionId: generateUUID(),
      error: null,
    }));
  }, [state.sessionId, generateWelcomeMessage]);

  // Close chat
  const closeChat = useCallback(() => {
    setState(prev => ({ ...prev, isOpen: false }));
  }, []);

  return {
    ...state,
    messagesEndRef,
    toggleChat,
    sendMessage,
    clearChat,
    closeChat,
  };
};