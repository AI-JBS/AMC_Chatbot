'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Circle } from 'lucide-react';

interface MCQOption {
  id: string;
  text: string;
  value: string;
}

interface MCQQuestion {
  id: string;
  question: string;
  options: MCQOption[];
  type: 'single' | 'multiple';
}

interface MCQComponentProps {
  question: MCQQuestion;
  onAnswer: (questionId: string, selectedOptions: string[]) => void;
  className?: string;
}

const MCQComponent: React.FC<MCQComponentProps> = ({ 
  question, 
  onAnswer, 
  className = '' 
}) => {
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);

  const handleOptionClick = (optionId: string) => {
    let newSelection: string[];
    
    if (question.type === 'single') {
      // Single selection - replace current selection
      newSelection = [optionId];
    } else {
      // Multiple selection - toggle option
      newSelection = selectedOptions.includes(optionId)
        ? selectedOptions.filter(id => id !== optionId)
        : [...selectedOptions, optionId];
    }
    
    setSelectedOptions(newSelection);
  };

  const handleSubmit = () => {
    if (selectedOptions.length > 0) {
      onAnswer(question.id, selectedOptions);
    }
  };

  const isSelected = (optionId: string) => selectedOptions.includes(optionId);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-lg p-3 border border-gray-200 ${className}`}
    >
      {/* Question */}
      <h3 className="text-sm font-medium text-gray-900 mb-3">
        {question.question}
      </h3>

      {/* Options */}
      <div className="space-y-2 mb-3">
        {question.options.map((option) => (
          <motion.button
            key={option.id}
            onClick={() => handleOptionClick(option.id)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`
              w-full flex items-center gap-2 p-2 rounded-lg border-2 transition-all duration-200 text-left
              ${isSelected(option.id)
                ? 'border-primary-500 bg-primary-50 text-primary-900'
                : 'border-gray-200 bg-gray-50 hover:border-primary-200 hover:bg-primary-25'
              }
            `}
          >
            {/* Checkbox/Radio Icon */}
            <div className="flex-shrink-0">
              {isSelected(option.id) ? (
                <CheckCircle size={16} className="text-primary-600" />
              ) : (
                <Circle size={16} className="text-gray-400" />
              )}
            </div>
            
            {/* Option Text */}
            <span className="text-xs flex-1">{option.text}</span>
          </motion.button>
        ))}
      </div>

      {/* Submit Button */}
      <motion.button
        onClick={handleSubmit}
        disabled={selectedOptions.length === 0}
        whileHover={{ scale: selectedOptions.length > 0 ? 1.05 : 1 }}
        whileTap={{ scale: selectedOptions.length > 0 ? 0.95 : 1 }}
        className={`
          w-full py-2 px-3 rounded-lg font-medium text-xs transition-all duration-200
          ${selectedOptions.length > 0
            ? 'bg-primary-600 text-white hover:bg-primary-700 shadow-sm'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }
        `}
      >
        {selectedOptions.length === 0 
          ? `Select ${question.type === 'single' ? 'an option' : 'options'}`
          : 'Submit Answer'
        }
      </motion.button>

      {/* Helper Text */}
      <p className="text-xs text-gray-500 mt-2 text-center">
        {question.type === 'multiple' 
          ? 'You can select multiple options' 
          : 'Select one option'
        }
      </p>
    </motion.div>
  );
};

export default MCQComponent;