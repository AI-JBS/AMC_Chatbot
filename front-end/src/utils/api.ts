import axios from 'axios';
import { ChatRequest, ChatResponse } from '@/types/chat';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8022',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export const chatAPI = {
  // Send message to chatbot
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    try {
      const response = await api.post<ChatResponse>('/chat', request);
      return response.data;
    } catch (error) {
      console.error('Chat API Error:', error);
      throw new Error('Failed to send message. Please try again.');
    }
  },

  // Get chat history for a session
  getChatHistory: async (sessionId: string) => {
    try {
      const response = await api.get(`/sessions/${sessionId}/history`);
      return response.data;
    } catch (error) {
      console.error('Get history error:', error);
      throw new Error('Failed to load chat history.');
    }
  },

  // Clear a chat session
  clearSession: async (sessionId: string) => {
    try {
      const response = await api.delete(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Clear session error:', error);
      throw new Error('Failed to clear session.');
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check error:', error);
      throw new Error('Backend service unavailable.');
    }
  },

  // Get available tools
  getTools: async () => {
    try {
      const response = await api.get('/tools');
      return response.data;
    } catch (error) {
      console.error('Get tools error:', error);
      throw new Error('Failed to load available tools.');
    }
  },
};

export default api;