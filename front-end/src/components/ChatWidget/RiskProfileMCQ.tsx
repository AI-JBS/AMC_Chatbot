'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MCQComponent from './MCQComponent';
import { TrendingUp, Shield, DollarSign, Clock, Target } from 'lucide-react';

interface RiskProfileData {
  age: string;
  experience: string;
  timeHorizon: string;
  riskTolerance: string;
  financialGoals: string[];
}

interface RiskProfileMCQProps {
  onComplete: (profileData: RiskProfileData) => void;
  className?: string;
}

const RiskProfileMCQ: React.FC<RiskProfileMCQProps> = ({ onComplete, className = '' }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string[]>>({});

  const questions = [
    {
      id: 'age',
      question: 'What is your age group?',
      type: 'single' as const,
      icon: <Clock size={16} />,
      options: [
        { id: 'young', text: '18-30 years', value: 'young' },
        { id: 'middle', text: '31-50 years', value: 'middle' },
        { id: 'senior', text: '51+ years', value: 'senior' },
      ]
    },
    {
      id: 'experience',
      question: 'How would you describe your investment experience?',
      type: 'single' as const,
      icon: <TrendingUp size={16} />,
      options: [
        { id: 'beginner', text: 'New to investing', value: 'beginner' },
        { id: 'intermediate', text: 'Some experience (1-5 years)', value: 'intermediate' },
        { id: 'experienced', text: 'Very experienced (5+ years)', value: 'experienced' },
      ]
    },
    {
      id: 'timeHorizon',
      question: 'What is your investment time horizon?',
      type: 'single' as const,
      icon: <Target size={16} />,
      options: [
        { id: 'short', text: 'Less than 2 years', value: 'short' },
        { id: 'medium', text: '2-5 years', value: 'medium' },
        { id: 'long', text: 'More than 5 years', value: 'long' },
      ]
    },
    {
      id: 'riskTolerance',
      question: 'How do you feel about investment risk?',
      type: 'single' as const,
      icon: <Shield size={16} />,
      options: [
        { id: 'conservative', text: 'I prefer stable, low-risk investments', value: 'conservative' },
        { id: 'moderate', text: 'I can accept some risk for better returns', value: 'moderate' },
        { id: 'aggressive', text: 'I\'m comfortable with high risk for high returns', value: 'aggressive' },
      ]
    },
    {
      id: 'financialGoals',
      question: 'What are your primary financial goals? (Select all that apply)',
      type: 'multiple' as const,
      icon: <DollarSign size={16} />,
      options: [
        { id: 'retirement', text: 'Retirement planning', value: 'retirement' },
        { id: 'wealth', text: 'Wealth building', value: 'wealth' },
        { id: 'education', text: 'Education funding', value: 'education' },
        { id: 'emergency', text: 'Emergency fund', value: 'emergency' },
        { id: 'house', text: 'House purchase', value: 'house' },
      ]
    }
  ];

  const handleAnswer = (questionId: string, selectedOptions: string[]) => {
    const newAnswers = { ...answers, [questionId]: selectedOptions };
    setAnswers(newAnswers);

    // Move to next question or complete
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // All questions answered - compile results
      const profileData: RiskProfileData = {
        age: newAnswers.age?.[0] || '',
        experience: newAnswers.experience?.[0] || '',
        timeHorizon: newAnswers.timeHorizon?.[0] || '',
        riskTolerance: newAnswers.riskTolerance?.[0] || '',
        financialGoals: newAnswers.financialGoals || [],
      };
      onComplete(profileData);
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl border border-gray-200 p-3 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 bg-primary-100 rounded-lg">
          {currentQuestion.icon}
        </div>
        <div className="flex-1">
          <h2 className="text-base font-semibold text-gray-900">Risk Profile Assessment</h2>
          <p className="text-xs text-gray-600">
            Question {currentQuestionIndex + 1} of {questions.length}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <motion.div
            className="bg-primary-600 h-1.5 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Question */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestion.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          <MCQComponent
            question={currentQuestion}
            onAnswer={handleAnswer}
          />
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      {currentQuestionIndex > 0 && (
        <motion.button
          onClick={() => setCurrentQuestionIndex(currentQuestionIndex - 1)}
          className="mt-3 text-xs text-gray-600 hover:text-primary-600 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          ← Previous Question
        </motion.button>
      )}
    </motion.div>
  );
};

export default RiskProfileMCQ;