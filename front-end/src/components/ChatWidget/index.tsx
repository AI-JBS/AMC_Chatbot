'use client';

import React, { useState, useEffect } from 'react';
import FloatingButton from './FloatingButton';
import ChatInterface from './ChatInterface';
import { chatAPI } from '@/utils/api';
import toast, { Toaster } from 'react-hot-toast';

const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState(true);
  const [hasUnreadMessage, setHasUnreadMessage] = useState(true); // Show notification initially

  // Check backend health on mount and show ready notification
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        await chatAPI.healthCheck();
        setIsBackendHealthy(true);
        
        // Show a subtle notification that chat is ready (only once)
        const hasShownNotification = localStorage.getItem('chat-ready-shown');
        if (!hasShownNotification) {
          setTimeout(() => {
            toast.success('💬 Financial advisor is ready to help!', {
              duration: 3000,
              position: 'bottom-right',
            });
            localStorage.setItem('chat-ready-shown', 'true');
          }, 2000);
        }
      } catch (error) {
        setIsBackendHealthy(false);
        console.error('Backend health check failed:', error);
      }
    };

    checkBackendHealth();
    
    // Check every 30 seconds
    const interval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleChat = () => {
    if (!isBackendHealthy) {
      toast.error('Chat service is currently unavailable. Please try again later.');
      return;
    }
    setIsOpen(prev => {
      const newIsOpen = !prev;
      if (newIsOpen) {
        setHasUnreadMessage(false); // Clear notification when opening chat
      }
      return newIsOpen;
    });
  };

  const handleCloseChat = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* Toast notifications */}
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
            borderRadius: '8px',
            fontSize: '14px',
            boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.2)',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
            style: {
              background: '#059669',
              color: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      {/* Chat Interface */}
      <ChatInterface 
        isOpen={isOpen} 
        onClose={handleCloseChat} 
      />

      {/* Floating Button */}
      <FloatingButton
        isOpen={isOpen}
        onClick={handleToggleChat}
        hasUnreadMessage={hasUnreadMessage}
      />

      {/* Offline indicator */}
      {!isBackendHealthy && (
        <div className="fixed bottom-20 right-6 bg-red-500 text-white px-3 py-2 rounded-lg text-sm shadow-lg z-40">
          ⚠️ Chat offline
        </div>
      )}
    </>
  );
};

export default ChatWidget;