'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Award, Target } from 'lucide-react';

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

interface CompactChartProps {
  funds: FundData[];
  title?: string;
}

const CompactChart: React.FC<CompactChartProps> = ({ funds, title = "Fund Performance" }) => {
  if (!funds || funds.length === 0) return null;

  console.log('📊 CompactChart received funds:', funds);

  // Sort funds by return
  const sortedFunds = [...funds].sort((a, b) => {
    const aReturn = a.performance?.return_365d || 0;
    const bReturn = b.performance?.return_365d || 0;
    return bReturn - aReturn;
  });

  const maxReturn = Math.max(...sortedFunds.map(f => f.performance?.return_365d || 0));
  console.log('📊 Max return:', maxReturn);

  const getBarWidth = (value: number) => {
    return Math.max((value / maxReturn) * 100, 5); // Minimum 5% width
  };

  const getRankIcon = (index: number) => {
    if (index === 0) return <Award className="text-yellow-500" size={12} />;
    if (index === 1) return <Target className="text-gray-400" size={12} />;
    return <span className="text-xs font-bold text-gray-500">#{index + 1}</span>;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg border border-gray-200 p-4 max-w-md"
    >
      {/* Compact Header */}
      <div className="text-center mb-3">
        <h3 className="text-sm font-bold text-gray-900">{title}</h3>
        <p className="text-xs text-gray-500">365D Returns</p>
      </div>

      {/* Compact Fund List */}
      <div className="space-y-2">
        {sortedFunds.slice(0, 5).map((fund, index) => {
          const return365d = fund.performance?.return_365d || 0;
          const nav = fund.nav || 0;
          const barWidth = getBarWidth(return365d);
          
          console.log(`📊 Fund ${index}: ${fund.name}, Return: ${return365d}%`);
          
          return (
            <motion.div
              key={fund.name}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-50 rounded-lg p-2 hover:bg-gray-100 transition-colors"
            >
              {/* Fund Info Row */}
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  {getRankIcon(index)}
                  <span className="text-xs font-medium text-gray-900 truncate">
                    {(fund.name || 'Unknown Fund').replace(' Fund', '').replace('JBS ', '')}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-emerald-600">
                    {return365d.toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Performance Bar */}
              <div className="mb-1">
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barWidth}%` }}
                    transition={{ duration: 0.8, delay: index * 0.1 + 0.2 }}
                    className={`h-1.5 rounded-full ${
                      index === 0 ? 'bg-emerald-500' :
                      index === 1 ? 'bg-blue-500' :
                      index === 2 ? 'bg-purple-500' :
                      'bg-gray-500'
                    }`}
                  />
                </div>
              </div>

              {/* Quick Stats */}
              <div className="flex justify-between text-xs text-gray-600">
                <span>NAV: ₨{nav.toFixed(0)}</span>
                <span>Fee: {(fund.fees?.expense_ratio || 0).toFixed(1)}%</span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Compact Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="mt-3 p-2 bg-blue-50 rounded-lg text-center"
      >
        <div className="text-xs text-gray-700">
          <TrendingUp size={12} className="inline mr-1 text-emerald-600" />
          <span className="font-medium">{sortedFunds[0]?.name?.replace(' Fund', '').replace('JBS ', '')}</span>
          {' '}leads with {(sortedFunds[0]?.performance?.return_365d || 0).toFixed(1)}%
        </div>
      </motion.div>
    </motion.div>
  );
};

export default CompactChart;