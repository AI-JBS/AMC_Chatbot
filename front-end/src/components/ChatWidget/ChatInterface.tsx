'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Minimize2, RotateCcw, TrendingUp } from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import ChatInput from './ChatInput';
import { useChat } from '@/hooks/useChat';

interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ isOpen, onClose }) => {
  const {
    messages,
    isLoading,
    sendMessage,
    clearChat,
    messagesEndRef,
  } = useChat();

  const handleClearChat = async () => {
    if (window.confirm('Are you sure you want to clear this conversation?')) {
      await clearChat();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ 
            opacity: 0, 
            scale: 0.95, 
            y: 20,
            transformOrigin: 'bottom right' 
          }}
          animate={{ 
            opacity: 1, 
            scale: 1, 
            y: 0 
          }}
          exit={{ 
            opacity: 0, 
            scale: 0.95, 
            y: 20 
          }}
          transition={{ 
            duration: 0.2, 
            ease: "easeOut" 
          }}
          className="chat-container widget-animation"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-t-xl shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <TrendingUp size={16} />
              </div>
              <div>
                <h3 className="font-semibold text-sm">Financial Advisor</h3>
                <p className="text-xs text-primary-100">
                  Mutual Fund Expert • Online
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Clear chat button */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleClearChat}
                className="p-1 hover:bg-white/20 rounded"
                title="Clear conversation"
              >
                <RotateCcw size={16} />
              </motion.button>
              
              {/* Minimize button (future feature) */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="p-1 hover:bg-white/20 rounded opacity-50 cursor-not-allowed"
                title="Minimize (Coming Soon)"
                disabled
              >
                <Minimize2 size={16} />
              </motion.button>
              
              {/* Close button */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="p-1 hover:bg-white/20 rounded"
                title="Close chat"
              >
                <X size={16} />
              </motion.button>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto chat-messages p-3 space-y-1">
            {/* Messages */}
            {messages.map((message, index) => (
              <MessageBubble
                key={message.id}
                message={message}
                isLatest={index === messages.length - 1}
                onSendMessage={sendMessage}
              />
            ))}

            {/* Typing indicator */}
            <AnimatePresence>
              {isLoading && <TypingIndicator />}
            </AnimatePresence>

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <ChatInput
            onSendMessage={sendMessage}
            disabled={isLoading}
            placeholder="Ask about mutual funds, portfolios, or market insights..."
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ChatInterface;