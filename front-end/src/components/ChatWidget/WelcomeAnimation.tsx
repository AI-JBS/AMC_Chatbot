'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';

interface WelcomeAnimationProps {
  onComplete?: () => void;
}

const WelcomeAnimation: React.FC<WelcomeAnimationProps> = ({ onComplete }) => {
  const [showMessage, setShowMessage] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowMessage(true);
      onComplete?.();
    }, 1500);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="flex flex-col items-center justify-center py-8 px-4">
      {/* Animated logo */}
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="w-16 h-16 bg-gradient-to-r from-primary-500 to-emerald-500 rounded-full flex items-center justify-center mb-4 shadow-lg"
      >
        <TrendingUp size={28} className="text-white" />
      </motion.div>

      {/* Welcome text */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: showMessage ? 1 : 0, y: showMessage ? 0 : 20 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Welcome to Financial Advisory
        </h3>
        <p className="text-sm text-gray-600">
          Your AI assistant is ready to help! 🚀
        </p>
      </motion.div>

      {/* Animated dots */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex space-x-1 mt-4"
      >
        {[0, 1, 2].map((index) => (
          <motion.div
            key={index}
            className="w-2 h-2 bg-primary-500 rounded-full"
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: index * 0.2,
              ease: "easeInOut",
            }}
          />
        ))}
      </motion.div>
    </div>
  );
};

export default WelcomeAnimation;