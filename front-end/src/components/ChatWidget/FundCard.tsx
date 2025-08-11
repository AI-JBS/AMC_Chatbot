'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, Target, Award, AlertCircle } from 'lucide-react';

interface FundData {
  name: string;
  nav: number;
  performance: {
    return_365d: number;
    return_ytd?: number;
  };
  fees: {
    expense_ratio: number;
    management_fee?: number;
  };
  details: {
    risk_profile: string;
  };
}

interface FundCardProps {
  fund: FundData;
  rank: number;
  isTopPerformer?: boolean;
  className?: string;
}

const FundCard: React.FC<FundCardProps> = ({ 
  fund, 
  rank, 
  isTopPerformer = false, 
  className = '' 
}) => {
  const return365d = fund.performance?.return_365d || 0;
  const expenseRatio = fund.fees?.expense_ratio || 0;
  
  const getPerformanceColor = (value: number) => {
    if (value >= 70) return 'text-emerald-600';
    if (value >= 60) return 'text-green-600';
    if (value >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceIcon = (value: number) => {
    return value >= 60 ? 
      <TrendingUp size={16} className={getPerformanceColor(value)} /> : 
      <TrendingDown size={16} className={getPerformanceColor(value)} />;
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Award className="text-yellow-500" size={18} />;
    if (rank === 2) return <Target className="text-gray-400" size={18} />;
    if (rank === 3) return <Target className="text-amber-600" size={18} />;
    return <span className="text-gray-500 font-bold text-sm">#{rank}</span>;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: rank * 0.1 }}
      className={`relative overflow-hidden rounded-xl border-2 transition-all duration-300 hover:shadow-lg ${
        isTopPerformer 
          ? 'border-emerald-400 bg-gradient-to-br from-emerald-50 to-green-50' 
          : 'border-gray-200 bg-white hover:border-blue-300'
      } ${className}`}
    >
      {/* Rank Badge */}
      <div className="absolute top-3 left-3 flex items-center gap-1">
        {getRankIcon(rank)}
      </div>

      {/* Top Performer Badge */}
      {isTopPerformer && (
        <div className="absolute top-3 right-3">
          <div className="bg-emerald-500 text-white text-xs px-2 py-1 rounded-full font-semibold">
            🏆 Top Pick
          </div>
        </div>
      )}

      <div className="p-4 pt-12">
        {/* Fund Name */}
        <h3 className="font-bold text-gray-900 text-sm mb-3 pr-8">
          {(fund.name || 'Unknown Fund').replace(' Fund', '')}
        </h3>

        {/* Performance Metrics */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          {/* 365D Return */}
          <div className="space-y-1">
            <div className="flex items-center gap-1">
              {getPerformanceIcon(return365d)}
              <span className="text-xs text-gray-500">365D Return</span>
            </div>
            <div className={`text-lg font-bold ${getPerformanceColor(return365d)}`}>
              {return365d.toFixed(1)}%
            </div>
          </div>

          {/* NAV */}
          <div className="space-y-1">
            <div className="flex items-center gap-1">
              <DollarSign size={16} className="text-blue-600" />
              <span className="text-xs text-gray-500">NAV</span>
            </div>
            <div className="text-lg font-bold text-gray-900">
              ₨{(fund.nav || 0).toFixed(2)}
            </div>
          </div>
        </div>

        {/* Expense Ratio Bar */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-500">Expense Ratio</span>
            <span className="text-xs font-semibold text-gray-700">{expenseRatio}%</span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(expenseRatio * 20, 100)}%` }}
              transition={{ duration: 1, delay: rank * 0.1 + 0.5 }}
              className={`h-2 rounded-full ${
                expenseRatio <= 1.5 ? 'bg-green-500' :
                expenseRatio <= 2.0 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
            />
          </div>
        </div>

        {/* Risk Profile */}
        <div className="mt-3 flex items-center gap-2">
          <AlertCircle size={14} className="text-orange-500" />
          <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full font-medium">
            {fund.details?.risk_profile || 'High'} Risk
          </span>
        </div>
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 to-purple-500/0 hover:from-blue-500/5 hover:to-purple-500/5 transition-all duration-300" />
    </motion.div>
  );
};

export default FundCard;