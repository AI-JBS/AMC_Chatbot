'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';

interface FundData {
  'Fund Name': string;
  [key: string]: string | number;
}

interface GanttChartProps {
  title: string;
  data: FundData[];
  metric: string;
  className?: string;
}

const GanttChart: React.FC<GanttChartProps> = ({ 
  title, 
  data, 
  metric, 
  className = '' 
}) => {
  if (!data || data.length === 0) return null;

  // Extract values and calculate max for scaling
  const values = data.map(item => {
    const value = item[metric];
    return typeof value === 'number' ? value : parseFloat(String(value)) || 0;
  });
  
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  
  const getBarWidth = (value: number) => {
    if (maxValue === minValue) return 50; // Default width if all values are same
    return ((value - minValue) / (maxValue - minValue)) * 70 + 15; // 15% minimum, 85% maximum
  };

  const formatValue = (value: number) => {
    if (value > 1000) return `${(value / 1000).toFixed(1)}K`;
    return value.toFixed(2);
  };

  const getTrendIcon = (value: number, average: number) => {
    return value >= average ? 
      <TrendingUp size={14} className="text-green-600" /> : 
      <TrendingDown size={14} className="text-red-600" />;
  };

  const average = values.reduce((a, b) => a + b, 0) / values.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-3 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1 bg-blue-100 rounded">
          <BarChart3 size={16} className="text-blue-600" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-gray-900">{title}</h3>
          <p className="text-xs text-gray-600">Performance comparison</p>
        </div>
      </div>

      {/* Chart */}
      <div className="space-y-2">
        {data.map((fund, index) => {
          const value = values[index];
          const barWidth = getBarWidth(value);
          const isAboveAverage = value >= average;
          
          return (
            <motion.div
              key={fund['Fund Name']}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="space-y-1"
            >
              {/* Fund Name and Value */}
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-gray-800 truncate">
                    {fund['Fund Name'].replace(' Fund', '')}
                  </span>
                  {getTrendIcon(value, average)}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-bold ${
                    isAboveAverage ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatValue(value)}%
                  </span>
                </div>
              </div>

              {/* Gantt Bar */}
              <div className="relative">
                {/* Background track */}
                <div className="w-full h-6 bg-gray-200 rounded relative overflow-hidden">
                  {/* Average line */}
                  <div 
                    className="absolute top-0 w-0.5 h-full bg-gray-400 z-10"
                    style={{ 
                      left: `${((average - minValue) / (maxValue - minValue)) * 100}%` 
                    }}
                  >
                    <div className="absolute -top-5 -left-6 text-xs text-gray-500 font-medium">
                      Avg
                    </div>
                  </div>
                  
                  {/* Performance bar */}
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${barWidth}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className={`h-full rounded flex items-center justify-end pr-2 ${
                      isAboveAverage 
                        ? 'bg-gradient-to-r from-green-400 to-green-600' 
                        : 'bg-gradient-to-r from-red-400 to-red-600'
                    }`}
                  >
                    <span className="text-xs font-semibold text-white">
                      {formatValue(value)}%
                    </span>
                  </motion.div>
                </div>

                {/* Timeline markers */}
                <div className="flex justify-between mt-1 text-xs text-gray-400">
                  <span>{formatValue(minValue)}%</span>
                  <span>{formatValue(average)}%</span>
                  <span>{formatValue(maxValue)}%</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-3 pt-2 border-t border-blue-200">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="text-sm font-bold text-green-600">{formatValue(maxValue)}%</div>
            <div className="text-xs text-gray-500">Best</div>
          </div>
          <div>
            <div className="text-sm font-bold text-gray-600">{formatValue(average)}%</div>
            <div className="text-xs text-gray-500">Average</div>
          </div>
          <div>
            <div className="text-sm font-bold text-red-600">{formatValue(minValue)}%</div>
            <div className="text-xs text-gray-500">Lowest</div>
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="mt-2 p-2 bg-white rounded border border-blue-100">
        <div className="flex items-start gap-1">
          <div className="w-2 h-2 bg-blue-500 rounded-full mt-1 flex-shrink-0"></div>
          <div className="text-xs text-gray-700">
            <span className="font-semibold">
              {data.find((_, i) => values[i] === maxValue)?.['Fund Name']}
            </span>
            {' '}leads with {formatValue(maxValue)}% {metric.toLowerCase()}, 
            outperforming average by {formatValue(maxValue - average)}%.
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default GanttChart;