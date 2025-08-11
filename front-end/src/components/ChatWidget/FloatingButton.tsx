'use client';

import React from 'react';
import { MessageCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface FloatingButtonProps {
  isOpen: boolean;
  onClick: () => void;
  hasUnreadMessage?: boolean;
}

const FloatingButton: React.FC<FloatingButtonProps> = ({ 
  isOpen, 
  onClick, 
  hasUnreadMessage = false 
}) => {
  // Don't render the floating button when chat is open
  if (isOpen) {
    return null;
  }

  return (
    <motion.button
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className="floating-button group bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700"
      aria-label="Open chat"
    >
      {/* Notification badge */}
      <AnimatePresence>
        {hasUnreadMessage && !isOpen && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white"
          />
        )}
      </AnimatePresence>

      {/* Button icon - only shows message icon since button is hidden when chat is open */}
      <motion.div
        initial={{ rotate: 90, opacity: 0 }}
        animate={{ rotate: 0, opacity: 1 }}
        transition={{ duration: 0.2 }}
        className="relative"
      >
        <MessageCircle size={24} />
        
        {/* Subtle pulse animation */}
        <motion.div
          className="absolute inset-0 rounded-full bg-white opacity-20"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0, 0.2],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </motion.div>

      {/* Tooltip */}
      <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap pointer-events-none z-10">
        Chat with Financial Advisor
        <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800" />
      </div>
    </motion.button>
  );
};

export default FloatingButton;