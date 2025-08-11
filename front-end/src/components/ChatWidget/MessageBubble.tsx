'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChatMessage } from '@/types/chat';
import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import RiskProfileMCQ from './RiskProfileMCQ';
import ChartComponent from './ChartComponent';
import GanttChart from './GanttChart';
import FundGrid from './FundGrid';
import SimpleChart from './SimpleChart';
import CompactChart from './CompactChart';
import LeadCollectionForm from './LeadCollectionForm';

interface MessageBubbleProps {
  message: ChatMessage;
  isLatest?: boolean;
  onSendMessage?: (content: string) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isLatest = false, onSendMessage }) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  // Function to parse and render comparison charts
  const renderComparisonChart = (content: string) => {
    try {
      // Try to extract structured data first (from tool JSON response)
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"comparison"[\s\S]*\}/);
      if (jsonMatch) {
        const toolData = JSON.parse(jsonMatch[0]);
        if (toolData.data && Array.isArray(toolData.data)) {
          // Extract metric from the data structure
          const firstItem = toolData.data[0];
          const metric = Object.keys(firstItem).find(key => key !== 'Fund Name') || 'Performance';
          
          return (
            <div className="mt-4 w-full">
              <GanttChart
                title={toolData.title || "Fund Performance Comparison"}
                data={toolData.data}
                metric={metric}
                className="w-full max-w-full"
              />
            </div>
          );
        }
      }

      // Fallback: Extract fund data from text content
      const lines = content.split('\n');
      const fundData: Array<{[key: string]: string | number}> = [];
      let metric = '365D Return';
      
      lines.forEach(line => {
        const match = line.match(/(.+?):\s*(\d+\.?\d*)%/);
        if (match) {
          const [, fundName, value] = match;
          fundData.push({
            'Fund Name': fundName.trim(),
            [metric]: parseFloat(value)
          });
        }
      });

      if (fundData.length >= 2) {
        return (
          <div className="mt-4 w-full">
            <GanttChart
              title="Fund Performance Comparison"
              data={fundData as any}
              metric={metric}
              className="w-full max-w-full"
            />
          </div>
        );
      }
    } catch (error) {
      console.error('Error rendering comparison chart:', error);
    }
    return null;
  };

  // Function to render performance analysis charts
  const renderPerformanceChart = (content: string) => {
    try {
      // Try to extract structured data first (from tool JSON response)
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"performance_analysis"[\s\S]*\}/);
      if (jsonMatch) {
        const toolData = JSON.parse(jsonMatch[0]);
        if (toolData.chart_data && toolData.chart_data.series) {
          const periods = Array.isArray(toolData.chart_data.xAxis) ? toolData.chart_data.xAxis : [];
          return (
            <div className="mt-4 w-full">
              <ChartComponent
                title={toolData.title || "Performance Analysis"}
                data={{
                  labels: periods,
                  datasets: toolData.chart_data.series.map((fund: any, index: number) => ({
                    label: fund.fund_name,
                    data: periods.map((p: string) => {
                      const raw = (fund as any)[p];
                      const num = typeof raw === 'number' ? raw : parseFloat(String(raw));
                      return isNaN(num) ? 0 : num;
                    }),
                    color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][index] || '#6b7280'
                  }))
                }}
                type="bar"
                className="w-full max-w-full"
              />
            </div>
          );
        }
      }

      // Fallback: Extract multi-period performance data from text
      const fundMatches = content.match(/(\w+\s+\w+\s+Fund):/g);
      if (!fundMatches || fundMatches.length < 2) return null;

      const funds = fundMatches.map(f => f.replace(':', '').trim());
      const periods = ['365D', '2Y', '3Y'];
      const colors = ['#3b82f6', '#10b981', '#f59e0b'];
      
      const datasets = funds.map((fund, index) => {
        const data: number[] = [];
        periods.forEach(period => {
          const regex = new RegExp(`${period}:\\s*(\\d+\\.?\\d*)%`);
          const match = content.match(regex);
          data.push(match ? parseFloat(match[1]) : 0);
        });
        
        return {
          label: fund,
          data,
          color: colors[index] || '#6b7280'
        };
      });

      const chartData = {
        labels: periods,
        datasets
      };

      return (
        <div className="mt-3">
          <ChartComponent
            title="Multi-Period Performance Analysis"
            data={chartData}
            type="bar"
          />
        </div>
      );
    } catch (error) {
      console.error('Error rendering performance chart:', error);
    }
    return null;
  };

  // Function to render beautiful fund recommendation cards and clean the content
  const renderRecommendationChart = (content: string) => {
    console.log('🔍 Full content received length:', content.length);
    
    try {
      // Clean the content first - remove extra whitespace and normalize
      const cleanContent = content.trim().replace(/\s+/g, ' ');
      console.log('🔍 Cleaned content sample:', cleanContent.substring(0, 200) + '...');
      
      let toolData = null;
      let jsonStartIndex = -1;
      let jsonEndIndex = -1;
      
      // Strategy 1: Find JSON starting with {"type": "recommendation"
      const startIndex = cleanContent.indexOf('{"type": "recommendation"');
      if (startIndex !== -1) {
        console.log('🔍 Found JSON start at position:', startIndex);
        jsonStartIndex = startIndex;
        
        // Find the end of this JSON object by counting braces
        let braceCount = 0;
        let endIndex = startIndex;
        let inString = false;
        let escapeNext = false;
        
        for (let i = startIndex; i < cleanContent.length; i++) {
          const char = cleanContent[i];
          
          if (escapeNext) {
            escapeNext = false;
            continue;
          }
          
          if (char === '\\') {
            escapeNext = true;
            continue;
          }
          
          if (char === '"' && !escapeNext) {
            inString = !inString;
            continue;
          }
          
          if (!inString) {
            if (char === '{') {
              braceCount++;
            } else if (char === '}') {
              braceCount--;
              if (braceCount === 0) {
                endIndex = i + 1;
                jsonEndIndex = endIndex;
                break;
              }
            }
          }
        }
        
        if (braceCount === 0 && endIndex > startIndex) {
          const jsonString = cleanContent.substring(startIndex, endIndex);
          console.log('🔍 Extracted JSON string length:', jsonString.length);
          console.log('🔍 JSON string preview:', jsonString.substring(0, 100) + '...');
          
          try {
            toolData = JSON.parse(jsonString);
            console.log('✅ Successfully parsed JSON:', toolData);
          } catch (parseError) {
            console.log('❌ JSON parse error:', parseError);
            console.log('❌ Problematic JSON:', jsonString.substring(0, 500));
          }
        }
      }
      
      // Strategy 2: Manual extraction if JSON parsing fails
      if (!toolData) {
        console.log('🔍 Trying manual extraction...');
        
        // Look for fund data patterns in the text
        const fundPattern = /JBS\s+([^:]+):\s*NAV\s*PKR\s*([\d.]+),\s*1Y\s*Return\s*([\d.]+)%/g;
        const funds = [];
        let match;
        
        while ((match = fundPattern.exec(content)) !== null) {
          const [, name, nav, returnValue] = match;
          funds.push({
            name: `JBS ${name.trim()} Fund`,
            nav: parseFloat(nav),
            performance: {
              return_365d: parseFloat(returnValue),
              return_ytd: 0
            },
            fees: {
              expense_ratio: 2.0,
              management_fee: 1.5
            },
            details: {
              risk_profile: 'High'
            }
          });
        }
        
        if (funds.length > 0) {
          console.log('✅ Manual extraction successful:', funds);
          toolData = {
            type: 'recommendation',
            recommended_funds: funds
          };
        }
      }
      
      // If we found valid data, render the chart and return clean content
      if (toolData && toolData.recommended_funds && Array.isArray(toolData.recommended_funds)) {
        console.log('✅ Rendering chart with', toolData.recommended_funds.length, 'funds');
        
        // Remove the JSON from the original content
        let cleanTextContent = content;
        if (jsonStartIndex !== -1 && jsonEndIndex !== -1) {
          cleanTextContent = content.substring(0, jsonStartIndex).trim();
          console.log('🧹 Cleaned text content (removed JSON)');
        }
        
        return {
          chart: (
            <div className="mt-3">
              <CompactChart 
                funds={toolData.recommended_funds}
                title="📊 Fund Performance"
              />
            </div>
          ),
          cleanContent: cleanTextContent
        };
      } else {
        console.log('❌ No valid tool data found');
        return { chart: null, cleanContent: content };
      }

      // Fallback: Extract fund data from text content
      const lines = content.split('\n');
      const funds: any[] = [];
      let currentFund: any = {};
      
      lines.forEach(line => {
        const fundMatch = line.match(/^\d+\.\s*(.+?)$/);
        if (fundMatch) {
          if (currentFund.name) {
            funds.push(currentFund);
          }
          currentFund = { 
            name: fundMatch[1].replace(/\*\*/g, ''),
            performance: {},
            fees: {},
            details: { risk_profile: 'High' }
          };
        }
        
        const navMatch = line.match(/NAV:\s*PKR\s*(\d+\.?\d*)/);
        if (navMatch) {
          currentFund.nav = parseFloat(navMatch[1]);
        }
        
        const returnMatch = line.match(/365D Return:\s*(\d+\.?\d*)%/);
        if (returnMatch) {
          currentFund.performance.return_365d = parseFloat(returnMatch[1]);
        }
        
        const expenseMatch = line.match(/Expense Ratio:\s*(\d+\.?\d*)%/);
        if (expenseMatch) {
          currentFund.fees.expense_ratio = parseFloat(expenseMatch[1]);
        }
      });
      
      if (currentFund.name) {
        funds.push(currentFund);
      }

      if (funds.length >= 2) {
        return {
          chart: (
            <div className="mt-3">
              <CompactChart 
                funds={funds}
                title="📊 Fund Performance"
              />
            </div>
          ),
          cleanContent: content.split('\n').slice(0, -5).join('\n').trim() // Remove last few lines with fund details
        };
      }
    } catch (error) {
      console.error('Error rendering recommendation chart:', error);
    }
    return { chart: null, cleanContent: content };
  };

  // Function to render market insights
  const renderMarketInsights = (content: string) => {
    try {
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"market_insights"[\s\S]*\}/);
      if (jsonMatch) {
        const toolData = JSON.parse(jsonMatch[0]);
        if (toolData.insights && toolData.insights.top_performers) {
          return (
            <div className="mt-4">
              <FundGrid 
                funds={toolData.insights.top_performers.map((fund: any) => ({
                  name: fund.name,
                  nav: fund.nav,
                  performance: { return_365d: fund.return_365d },
                  fees: { expense_ratio: fund.expense_ratio },
                  details: { risk_profile: fund.risk_profile }
                }))}
                title="📊 Top Performing Funds"
              />
            </div>
          );
        }
      }
    } catch (error) {
      console.error('Error rendering market insights:', error);
    }
    return null;
  };

  // Function to render consistency analysis
  const renderConsistencyAnalysis = (content: string) => {
    try {
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"consistency_analysis"[\s\S]*\}/);
      if (jsonMatch) {
        const toolData = JSON.parse(jsonMatch[0]);
        if (toolData.consistency_ranking) {
          // Convert to SimpleChart format
          const funds = toolData.consistency_ranking.map((fund: any) => ({
            name: fund.fund_name,
            nav: 100, // Default NAV
            performance: { 
              return_365d: fund.consistency_score * 100 // Convert to percentage
            },
            fees: { expense_ratio: 2.0 },
            details: { risk_profile: 'High' }
          }));
          
          return (
            <div className="mt-4">
              <SimpleChart
                funds={funds}
                title="🎯 Fund Consistency Scores"
              />
            </div>
          );
        }
      }
    } catch (error) {
      console.error('Error rendering consistency analysis:', error);
    }
    return null;
  };

  // Function to render correlation analysis
  const renderCorrelationAnalysis = (content: string) => {
    try {
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"correlation_analysis"[\s\S]*\}/);
      if (jsonMatch) {
        const toolData = JSON.parse(jsonMatch[0]);
        if (toolData.correlation_matrix) {
          // Convert to SimpleChart format
          const funds = toolData.correlation_matrix.map((item: any, index: number) => ({
            name: `${item.fund1} vs ${item.fund2}`,
            nav: 100, // Default NAV
            performance: { 
              return_365d: Math.abs(item.correlation) * 100 // Convert correlation to percentage
            },
            fees: { expense_ratio: 2.0 },
            details: { risk_profile: 'Medium' }
          }));
          
          return (
            <div className="mt-4">
              <SimpleChart
                funds={funds}
                title="📊 Fund Correlation Matrix"
              />
            </div>
          );
        }
      }
    } catch (error) {
      console.error('Error rendering correlation analysis:', error);
    }
    return null;
  };

  // Function to render portfolio allocation
  const renderPortfolioAllocation = (content: string) => {
    try {
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"portfolio"[\s\S]*\}/);
      if (jsonMatch) {
        const toolData = JSON.parse(jsonMatch[0]);
        console.log('Portfolio data:', toolData);
        
        if (toolData.allocation && Array.isArray(toolData.allocation)) {
          // Convert to SimpleChart format with correct data mapping
          const funds = toolData.allocation.map((item: any) => ({
            name: item.fund_name || 'Unknown Fund',
            nav: parseFloat(item.nav) || 100,
            performance: { 
              return_365d: parseFloat(item.percentage) || 0 // Use percentage as performance metric
            },
            fees: { expense_ratio: parseFloat(item.expense_ratio) || 2.0 },
            details: { 
              risk_profile: item.risk_category || 'Medium',
              amount: item.amount || 0,
              rationale: item.rationale || ''
            }
          }));
          
          return (
            <div className="mt-2 max-w-sm">
              <SimpleChart
                funds={funds}
                title={toolData.title || 'Portfolio Allocation'}
              />
            </div>
          );
        }
      }
    } catch (error) {
      console.error('Error rendering portfolio allocation:', error);
    }
    return null;
  };

  // Function to render smart recommendation chart
  const renderSmartRecommendationChart = (content: string) => {
    try {
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"smart_recommendation"[\s\S]*\}/);
      if (jsonMatch) {
        const toolData = JSON.parse(jsonMatch[0]);
        if (toolData.recommendations && Array.isArray(toolData.recommendations)) {
          // Convert recommendations to fund format for FundGrid
          const funds = toolData.recommendations.map((rec: any) => ({
            name: rec.fund.name,
            nav: parseFloat(rec.fund.nav) || 0,
            performance: { 
              return_365d: parseFloat(rec.fund.return_365d) || 0,
              return_ytd: parseFloat(rec.fund.return_ytd) || 0
            },
            fees: { 
              expense_ratio: parseFloat(rec.fund.expense_ratio) || 0,
              management_fee: parseFloat(rec.fund.management_fee) || 0
            },
            details: { 
              risk_profile: rec.fund.risk_profile || 'Medium'
            }
          }));
          
          return (
            <div className="mt-4 w-full">
              <FundGrid 
                funds={funds}
                title={toolData.title || 'Smart Fund Recommendations'}
                className="w-full max-w-full"
              />
            </div>
          );
        }
      }
    } catch (error) {
      console.error('Error rendering smart recommendation chart:', error);
    }
    return null;
  };

  // Function to render lead collection form
  const renderLeadCollectionForm = (content: string) => {
    try {
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"lead_collection"[\s\S]*\}/);
      if (jsonMatch) {
        const toolData = JSON.parse(jsonMatch[0]);
        
        const handleSubmit = async (formData: any) => {
          if (onSendMessage) {
            onSendMessage(`LEAD_SUBMIT: ${JSON.stringify(formData)}`);
          }
        };

        const handleDecline = () => {
          if (onSendMessage) {
            onSendMessage("LEAD_DECLINE");
          }
        };

        const handleClose = () => {
          if (onSendMessage) {
            onSendMessage("LEAD_CLOSE");
          }
        };

        return (
          <div className="mt-4 w-full">
            <LeadCollectionForm
              title={toolData.title}
              description={toolData.description}
              formFields={toolData.form_fields}
              submitText={toolData.submit_text}
              privacyNote={toolData.privacy_note}
              declineOption={toolData.decline_option}
              onSubmit={handleSubmit}
              onDecline={handleDecline}
              onClose={handleClose}
            />
          </div>
        );
      }
    } catch (error) {
      console.error('Error rendering lead collection form:', error);
    }
    return null;
  };

  // Function to clean content by removing JSON data and detailed listings
  const cleanContentFromJson = (content: string, responseType: string) => {
    try {
      // Find JSON object in the content
      const jsonMatch = content.match(/\{[\s\S]*"type":\s*"[^"]+"[\s\S]*\}/);
      if (jsonMatch) {
        const beforeJson = content.substring(0, content.indexOf(jsonMatch[0])).trim();
        
        // For recommendation types, always return minimal text regardless of beforeJson
        if (responseType === 'recommendation' || responseType === 'smart_recommendation') {
          return responseType === 'recommendation' ? "Fund recommendations" : "Personalized fund recommendations";
        }
        
        // Create simplified content based on response type
        if (responseType === 'comparison') {
          return "Performance comparison";
        } else if (responseType === 'performance_analysis') {
          return "Performance analysis";
        } else if (responseType === 'portfolio') {
          return "Portfolio allocation";
        } else if (responseType === 'market_insights') {
          return "Market insights";
        } else if (responseType === 'lead_collection') {
          return "Would you like to connect with our investment experts?";
        } else if (responseType === 'lead_submitted') {
          return "Thank you for your interest!";
        } else if (responseType === 'lead_declined') {
          return "No problem at all!";
        } else if (responseType === 'lead_collection_declined') {
          return "I understand your preference.";
        } else if (responseType === 'lead_already_submitted') {
          return "Thank you for your previous submission.";
        } else {
          // For other types, return the text before JSON or a generic message
          return beforeJson || "Here are your results";
        }
      }
    } catch (error) {
      console.error('Error cleaning content:', error);
    }
    return content;
  };

  // Check if this is a recommendation response and get clean content
  const recommendationResult = message.response_type === 'recommendation' 
    ? renderRecommendationChart(message.content) 
    : null;
    
  // Clean content for all response types that have JSON data
  const shouldCleanContent = ['recommendation', 'performance_analysis', 'market_insights', 
    'consistency_analysis', 'correlation_analysis', 'portfolio', 'comparison', 'smart_recommendation', 'lead_collection', 'lead_submitted', 'lead_declined', 'lead_collection_declined', 'lead_already_submitted'].includes(message.response_type || '');
  
  const displayContent = recommendationResult?.cleanContent || 
    (shouldCleanContent ? cleanContentFromJson(message.content, message.response_type || '') : message.content);
  const recommendationChart = recommendationResult?.chart || null;

  const formatTime = (timestamp: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    }).format(new Date(timestamp));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`flex items-start gap-2 mb-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`
        flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-white text-sm font-medium
        ${isUser 
          ? 'bg-primary-500' 
          : 'bg-gradient-to-br from-emerald-500 to-emerald-600'
        }
      `}>
        {isUser ? <User size={14} /> : <Bot size={14} />}
      </div>

      {/* Message Content */}
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[85%]`}>
        {/* Message Bubble */}
        <div className={`
          chat-message relative max-w-[280px]
          ${isUser 
            ? 'chat-message-user' 
            : 'chat-message-assistant'
          }
        `}>
          {isAssistant ? (
            <>
              {/* Show Risk Profile MCQ if response_type is 'quiz' - NO TEXT */}
              {message.response_type === 'quiz' ? (
                <div className="mt-1 max-w-sm">
                  <RiskProfileMCQ
                    onComplete={(profileData) => {
                      // Send the profile data back to the chat without showing completion text
                      const profileSummary = `Risk Profile Complete: ${profileData.riskTolerance} risk tolerance, ${profileData.experience} experience, ${profileData.timeHorizon} horizon, goals: ${profileData.financialGoals.join(', ')}`;
                      console.log('✅ Profile completed successfully:', profileData);
                      
                      // Send the profile summary back to the chat for processing
                      if (onSendMessage) {
                        onSendMessage(profileSummary);
                      } else {
                        console.error('❌ Cannot send message - onSendMessage not provided');
                      }
                    }}
                  />
                </div>
              ) : (
                <>
                  <ReactMarkdown 
                    className="prose prose-sm max-w-none"
                    components={{
                      p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="text-sm">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                      em: ({ children }) => <em className="italic">{children}</em>,
                      code: ({ children }) => (
                        <code className="px-1 py-0.5 bg-gray-100 rounded text-xs font-mono">
                          {children}
                        </code>
                      ),
                    }}
                  >
                    {displayContent}
                  </ReactMarkdown>
                  
                  {/* Show Charts for different response types */}
                  {message.response_type === 'comparison' && renderComparisonChart(message.content)}
                  {message.response_type === 'performance_analysis' && renderPerformanceChart(message.content)}
                  {message.response_type === 'recommendation' && recommendationChart}
                  {message.response_type === 'smart_recommendation' && renderSmartRecommendationChart(message.content)}
                  {message.response_type === 'market_insights' && renderMarketInsights(message.content)}
                  {message.response_type === 'consistency_analysis' && renderConsistencyAnalysis(message.content)}
                  {message.response_type === 'correlation_analysis' && renderCorrelationAnalysis(message.content)}
                  {message.response_type === 'portfolio' && renderPortfolioAllocation(message.content)}
                  {message.response_type === 'lead_collection' && renderLeadCollectionForm(message.content)}
                </>
              )}
            </>
          ) : (
            <>
              {/* Hide quiz completion messages from user */}
              {!message.content.startsWith('Risk Profile Complete:') && (
                <p className="whitespace-pre-wrap">{message.content}</p>
              )}
            </>
          )}
        </div>

        {/* Timestamp */}
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {formatTime(message.timestamp)}
          {message.response_type && (
            <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
              {message.response_type}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;