'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, BarChart3, PieChart } from 'lucide-react';

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color: string;
  }[];
}

interface ChartComponentProps {
  title: string;
  data: ChartData;
  type: 'bar' | 'line' | 'pie';
  className?: string;
}

const ChartComponent: React.FC<ChartComponentProps> = ({ 
  title, 
  data, 
  type = 'bar', 
  className = '' 
}) => {
  const validValues = data.datasets.flatMap(d => d.data.filter(val => val !== undefined && val !== null && !isNaN(val)));
  const maxValue = validValues.length > 0 ? Math.max(...validValues) : 1;
  
  const getBarHeight = (value: number) => {
    return (value / maxValue) * 100;
  };

  const formatValue = (value: number | undefined | null) => {
    if (value === undefined || value === null || isNaN(value)) return 'N/A';
    if (value > 1000) return `${(value / 1000).toFixed(1)}K`;
    return value.toFixed(1);
  };

  const getTrendIcon = (value: number) => {
    return value >= 0 ? 
      <TrendingUp size={14} className="text-green-600" /> : 
      <TrendingDown size={14} className="text-red-600" />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-lg border border-gray-200 p-3 ${className}`}
    >
      {/* Chart Header */}
      <div className="flex items-center gap-2 mb-3">
        <BarChart3 size={14} className="text-primary-600" />
        <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
      </div>

      {/* Chart Content */}
      {type === 'bar' && (
        <div className="space-y-3">
          {/* Legend */}
          <div className="flex flex-wrap gap-3 text-xs">
            {data.datasets.map((dataset, index) => (
              <div key={index} className="flex items-center gap-1">
                <div 
                  className="w-2 h-2 rounded"
                  style={{ backgroundColor: dataset.color }}
                />
                <span className="text-gray-600">{dataset.label}</span>
              </div>
            ))}
          </div>

          {/* Bar Chart */}
          <div className="space-y-2">
            {data.labels.map((label, labelIndex) => (
              <div key={labelIndex} className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-medium text-gray-700">{label}</span>
                </div>
                
                <div className="flex gap-1 h-6">
                  {data.datasets.map((dataset, datasetIndex) => {
                    const value = dataset.data[labelIndex];
                    const safeValue = value !== undefined && value !== null && !isNaN(value) ? value : 0;
                    const height = getBarHeight(safeValue);
                    
                    return (
                      <div key={datasetIndex} className="flex-1 relative">
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: `${height}%` }}
                          transition={{ duration: 0.8, delay: labelIndex * 0.1 }}
                          className="w-full rounded-sm relative group cursor-pointer"
                          style={{ backgroundColor: dataset.color }}
                        >
                          {/* Tooltip */}
                          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                            {formatValue(value)}%
                          </div>
                        </motion.div>
                        
                        {/* Value label */}
                        <div className="text-xs text-center mt-1 flex items-center justify-center gap-1">
                          {safeValue !== 0 && getTrendIcon(safeValue)}
                          <span className={safeValue >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {formatValue(value)}%
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Simple comparison table for text data */}
      {type === 'line' && (
        <div className="space-y-2">
          <div className="grid grid-cols-3 gap-2 text-xs font-medium text-gray-600 border-b pb-2">
            <span>Fund</span>
            <span>Value</span>
            <span>Trend</span>
          </div>
          
          {data.labels.map((label, index) => (
            <div key={index} className="grid grid-cols-3 gap-2 text-xs py-1">
              <span className="text-gray-800">{label}</span>
              <span className="font-medium">
                {data.datasets[0] ? formatValue(data.datasets[0].data[index]) : 'N/A'}%
              </span>
              <span className="flex items-center">
                {data.datasets[0] ? getTrendIcon(data.datasets[0].data[index]) : null}
              </span>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default ChartComponent;