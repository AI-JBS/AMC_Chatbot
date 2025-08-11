'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Phone, DollarSign, Target, Clock, X } from 'lucide-react';

interface FormField {
  id: string;
  label: string;
  type: string;
  required: boolean;
  placeholder: string;
  options?: string[];
}

interface LeadCollectionFormProps {
  title: string;
  description: string;
  formFields: FormField[];
  submitText: string;
  privacyNote: string;
  declineOption: string;
  onSubmit: (formData: any) => void;
  onDecline: () => void;
  onClose: () => void;
}

const LeadCollectionForm: React.FC<LeadCollectionFormProps> = ({
  title,
  description,
  formFields,
  submitText,
  privacyNote,
  declineOption,
  onSubmit,
  onDecline,
  onClose
}) => {
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (fieldId: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [fieldId]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getFieldIcon = (fieldId: string) => {
    switch (fieldId) {
      case 'name': return <User size={16} />;
      case 'email': return <Mail size={16} />;
      case 'phone': return <Phone size={16} />;
      case 'investment_amount': return <DollarSign size={16} />;
      case 'risk_preference': return <Target size={16} />;
      case 'investment_horizon': return <Clock size={16} />;
      default: return <User size={16} />;
    }
  };

  const isFormValid = () => {
    return formFields.every(field => {
      if (field.required) {
        return formData[field.id] && formData[field.id].trim() !== '';
      }
      return true;
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="bg-white rounded-lg border border-gray-200 shadow-lg max-w-md w-full"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 rounded transition-colors"
        >
          <X size={16} className="text-gray-500" />
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="p-4 space-y-4">
        {formFields.map((field) => (
          <div key={field.id} className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <div className="text-gray-400">
                  {getFieldIcon(field.id)}
                </div>
              </div>
              
              {field.type === 'select' ? (
                <select
                  value={formData[field.id] || ''}
                  onChange={(e) => handleInputChange(field.id, e.target.value)}
                  required={field.required}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select {field.label}</option>
                  {field.options?.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type={field.type}
                  value={formData[field.id] || ''}
                  onChange={(e) => handleInputChange(field.id, e.target.value)}
                  placeholder={field.placeholder}
                  required={field.required}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              )}
            </div>
          </div>
        ))}

        {/* Privacy Note */}
        <p className="text-xs text-gray-500">{privacyNote}</p>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!isFormValid() || isSubmitting}
          className="w-full bg-primary-500 text-white py-2 px-4 rounded-md hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? 'Submitting...' : submitText}
        </button>

        {/* Decline Option */}
        <button
          type="button"
          onClick={onDecline}
          className="w-full text-gray-500 py-2 px-4 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors text-sm"
        >
          {declineOption}
        </button>
      </form>
    </motion.div>
  );
};

export default LeadCollectionForm;
