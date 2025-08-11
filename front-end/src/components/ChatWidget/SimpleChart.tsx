'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, DollarSign, Target, Award } from 'lucide-react';

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

interface SimpleChartProps {
  funds: FundData[];
  title?: string;
}

const SimpleChart: React.FC<SimpleChartProps> = ({ funds, title = "Fund Performance" }) => {
  if (!funds || funds.length === 0) return null;

  console.log('📊 SimpleChart received funds:', funds);

  // Sort funds by return
  const sortedFunds = [...funds].sort((a, b) => {
    const aReturn = a.performance?.return_365d || 0;
    const bReturn = b.performance?.return_365d || 0;
    console.log(`Comparing ${a.name}: ${aReturn} vs ${b.name}: ${bReturn}`);
    return bReturn - aReturn;
  });

  const maxReturn = Math.max(...sortedFunds.map(f => f.performance?.return_365d || 0));
  console.log('📊 Max return calculated:', maxReturn);

  const getBarWidth = (value: number) => {
    return (value / maxReturn) * 100;
  };

  const getRankIcon = (index: number) => {
    if (index === 0) return <Award className="text-yellow-500" size={16} />;
    if (index === 1) return <Target className="text-gray-400" size={16} />;
    if (index === 2) return <Target className="text-amber-600" size={16} />;
    return <span className="text-sm font-bold text-gray-500">#{index + 1}</span>;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-4 shadow-lg"
    >
      {/* Header */}
      <div className="text-center mb-4">
        <h2 className="text-lg font-bold text-gray-900 mb-1">{title}</h2>
        <p className="text-sm text-gray-600">Allocation Analysis</p>
      </div>

      {/* Performance Bars */}
      <div className="space-y-3">
        {sortedFunds.map((fund, index) => {
          const return365d = fund.performance?.return_365d || 0;
          const expenseRatio = fund.fees?.expense_ratio || 0;
          const nav = fund.nav || 0;
          const barWidth = getBarWidth(return365d);
          
          console.log(`📊 Fund ${index}: ${fund.name}, Return: ${return365d}, NAV: ${nav}, Expense: ${expenseRatio}`);
          
          return (
            <motion.div
              key={fund.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow"
            >
              {/* Fund Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  {getRankIcon(index)}
                  <span className="font-semibold text-gray-900 text-sm">
                    {fund.name?.replace(' Fund', '') || 'Unknown Fund'}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-emerald-600">
                    {return365d.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500">Allocation</div>
                </div>
              </div>

              {/* Performance Bar */}
              <div className="mb-3">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barWidth}%` }}
                    transition={{ duration: 1, delay: index * 0.1 + 0.3 }}
                    className={`h-3 rounded-full ${
                      index === 0 ? 'bg-gradient-to-r from-emerald-400 to-emerald-600' :
                      index === 1 ? 'bg-gradient-to-r from-blue-400 to-blue-600' :
                      index === 2 ? 'bg-gradient-to-r from-purple-400 to-purple-600' :
                      'bg-gradient-to-r from-gray-400 to-gray-600'
                    }`}
                  />
                </div>
              </div>

              {/* Fund Details */}
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center">
                  <DollarSign size={12} className="text-blue-600 mx-auto mb-1" />
                  <div className="font-semibold text-gray-900 text-xs">₨{nav.toFixed(2)}</div>
                  <div className="text-xs text-gray-500">NAV</div>
                </div>
                
                <div className="text-center">
                  <TrendingUp size={12} className="text-orange-600 mx-auto mb-1" />
                  <div className="font-semibold text-gray-900 text-xs">{expenseRatio.toFixed(2)}%</div>
                  <div className="text-xs text-gray-500">Expense</div>
                </div>
                
                <div className="text-center">
                  <Target size={12} className="text-red-600 mx-auto mb-1" />
                  <div className="font-semibold text-gray-900 text-xs">{fund.details?.risk_profile || 'High'}</div>
                  <div className="text-xs text-gray-500">Risk</div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-4 text-center p-3 bg-white rounded-lg"
      >
        <div className="text-xs text-gray-600">
          <span className="font-semibold text-emerald-600">{sortedFunds[0]?.name?.replace(' Fund', '')}</span>
          {' '}leads with <span className="font-semibold">{(sortedFunds[0]?.performance?.return_365d || 0).toFixed(1)}%</span> allocation.
          <br />
          Perfect for long-term growth with balanced risk.
        </div>
      </motion.div>
    </motion.div>
  );
};

export default SimpleChart;