'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { motion } from 'framer-motion';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Ask about mutual funds, portfolios, or market insights...",
}) => {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [hasUserSentMessage, setHasUserSentMessage] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea based on content
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.min(textarea.scrollHeight, 120); // Max height of ~4 lines
      textarea.style.height = `${newHeight}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      setHasUserSentMessage(true); // Hide quick questions after first message
      setIsFocused(false); // Remove focus to hide quick questions
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const quickQuestions = [
    "Best funds for beginners",
    "Portfolio diversification tips", 
    "Low-risk investment options",
    "Take risk assessment quiz",
  ];

  return (
    <div className="border-t border-gray-200 bg-white rounded-b-xl">
      {/* Quick Questions (only show when input is empty, focused, and user hasn't sent a message yet) */}
      {message.length === 0 && isFocused && !hasUserSentMessage && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="px-3 py-2 border-b border-gray-100 bg-gray-50"
        >
          <p className="text-xs text-gray-500 mb-1.5">Quick start:</p>
          <div className="grid grid-cols-2 gap-1.5">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onMouseDown={(e) => {
                  e.preventDefault(); // Prevent blur from firing
                  onSendMessage(question);
                  setMessage('');
                  setHasUserSentMessage(true);
                  setIsFocused(false);
                }}
                className="text-xs px-2 py-1.5 bg-white hover:bg-primary-50 hover:text-primary-700 border border-gray-200 rounded-md text-gray-600 transition-all duration-200 text-left cursor-pointer"
                type="button"
              >
                {question}
              </button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex items-end gap-3 p-3">
        {/* Message input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={`
              w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg 
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent 
              resize-none overflow-hidden transition-all duration-200 text-sm
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
              ${isFocused ? 'bg-white shadow-sm border-primary-200' : ''}
            `}
            style={{ minHeight: '40px' }}
          />

          {/* Character count (when approaching limit) */}
          {message.length > 800 && (
            <div className="absolute -top-6 right-0 text-xs text-gray-500">
              {message.length}/1000
            </div>
          )}
        </div>

        {/* Send button */}
        <motion.button
          type="submit"
          disabled={!message.trim() || disabled}
          whileHover={{ scale: disabled || !message.trim() ? 1 : 1.05 }}
          whileTap={{ scale: disabled || !message.trim() ? 1 : 0.95 }}
          className={`
            flex-shrink-0 p-2 rounded-lg transition-all duration-200
            ${message.trim() && !disabled
              ? 'bg-primary-500 text-white hover:bg-primary-600 shadow-sm'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          <Send size={16} />
        </motion.button>
      </form>

      {/* Footer text */}
      <div className="px-3 pb-2">
        <p className="text-xs text-gray-400 text-center">
          AI Financial Advisor • Powered by Azure OpenAI
        </p>
      </div>
    </div>
  );
};

export default ChatInput;