'use client';

import React from 'react';
import { motion } from 'framer-motion';
import FundCard from './FundCard';
import { BarChart3, TrendingUp, DollarSign } from 'lucide-react';

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

interface FundGridProps {
  funds: FundData[];
  title?: string;
  className?: string;
}

const FundGrid: React.FC<FundGridProps> = ({ 
  funds, 
  title = "Fund Recommendations",
  className = '' 
}) => {
  if (!funds || funds.length === 0) return null;

  // Sort funds by 365D return (descending) with safe fallbacks
  const sortedFunds = [...funds].sort((a, b) => {
    const aReturn = a.performance?.return_365d || 0;
    const bReturn = b.performance?.return_365d || 0;
    return bReturn - aReturn;
  });
  
  const topPerformer = sortedFunds[0];
  const avgReturn = funds.reduce((sum, fund) => {
    return sum + (fund.performance?.return_365d || 0);
  }, 0) / funds.length;
  
  const avgExpense = funds.reduce((sum, fund) => {
    return sum + (fund.fees?.expense_ratio || 0);
  }, 0) / funds.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-br from-slate-50 to-blue-50 rounded-lg p-4 ${className}`}
    >
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1 bg-blue-500 rounded">
            <BarChart3 size={16} className="text-white" />
          </div>
          <h2 className="text-sm font-bold text-gray-900">{title}</h2>
        </div>
        
        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-2 mt-3">
          <div className="bg-white rounded p-2 text-center">
            <TrendingUp size={14} className="text-emerald-600 mx-auto mb-1" />
            <div className="text-sm font-bold text-emerald-600">{(topPerformer?.performance?.return_365d || 0).toFixed(1)}%</div>
            <div className="text-xs text-gray-500">Best Return</div>
          </div>
          
          <div className="bg-white rounded p-2 text-center">
            <BarChart3 size={14} className="text-blue-600 mx-auto mb-1" />
            <div className="text-sm font-bold text-blue-600">{avgReturn.toFixed(1)}%</div>
            <div className="text-xs text-gray-500">Avg Return</div>
          </div>
          
          <div className="bg-white rounded p-2 text-center">
            <DollarSign size={14} className="text-orange-600 mx-auto mb-1" />
            <div className="text-sm font-bold text-orange-600">{avgExpense.toFixed(2)}%</div>
            <div className="text-xs text-gray-500">Avg Fees</div>
          </div>
        </div>
      </div>

      {/* Fund Cards Grid */}
      <div className="grid grid-cols-1 gap-3">
        {sortedFunds.map((fund, index) => (
          <FundCard
            key={fund.name}
            fund={fund}
            rank={index + 1}
            isTopPerformer={index === 0}
          />
        ))}
      </div>

      {/* Insight */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-6 p-4 bg-white rounded-lg border border-blue-200"
      >
        <div className="flex items-start gap-3">
          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
          <div className="text-sm text-gray-700">
            <span className="font-semibold text-emerald-600">{topPerformer?.name || 'Top Fund'}</span>
            {' '}leads with {(topPerformer?.performance?.return_365d || 0).toFixed(1)}% annual return. 
            All funds shown are suitable for long-term investment (5+ years) with high growth potential.
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default FundGrid;