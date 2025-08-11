'use client';

import React from 'react';
import { TrendingUp, Shield, PieChart, BarChart3, Users, Star } from 'lucide-react';
import ChatWidget from '@/components/ChatWidget';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Asset Management</h1>
                <p className="text-sm text-gray-600">Financial Advisory Platform</p>
              </div>
            </div>
            
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-600 hover:text-primary-600 transition-colors">Features</a>
              <a href="#about" className="text-gray-600 hover:text-primary-600 transition-colors">About</a>
              <a href="#contact" className="text-gray-600 hover:text-primary-600 transition-colors">Contact</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Your AI-Powered{' '}
            <span className="bg-gradient-to-r from-primary-600 to-emerald-600 bg-clip-text text-transparent">
              Financial Advisor
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Get personalized mutual fund recommendations, portfolio analysis, and market insights 
            powered by advanced AI. Make informed investment decisions with data-driven guidance.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button className="bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors shadow-lg">
              Start Investing
            </button>
            <button className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
              Learn More
            </button>
          </div>

          {/* CTA for chat */}
          <div className="mt-8 p-4 bg-primary-50 rounded-xl border border-primary-200">
            <p className="text-primary-800 font-medium">
              💬 Click the chat button in the bottom right to get started with your AI financial advisor!
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Intelligent Financial Advisory
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI-powered platform provides comprehensive tools for mutual fund investment and portfolio management
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature cards */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Smart Recommendations</h3>
              <p className="text-gray-600">Get personalized mutual fund recommendations based on your risk profile and investment goals.</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                <PieChart className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Portfolio Analysis</h3>
              <p className="text-gray-600">Analyze your portfolio performance, diversification, and optimize your asset allocation.</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-yellow-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Market Insights</h3>
              <p className="text-gray-600">Stay updated with real-time market trends, opportunities, and investment alerts.</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Risk Assessment</h3>
              <p className="text-gray-600">Comprehensive risk profiling to match investments with your risk tolerance.</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Expert Guidance</h3>
              <p className="text-gray-600">Connect with expert financial advisors for personalized investment strategies.</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                <Star className="w-6 h-6 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">24/7 Support</h3>
              <p className="text-gray-600">Round-the-clock AI assistance for all your investment queries and decisions.</p>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-gradient-to-r from-primary-600 to-emerald-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Powered by Advanced AI Technology
          </h2>
          <p className="text-xl text-primary-100 max-w-3xl mx-auto mb-8">
            Our platform leverages Azure OpenAI and cutting-edge machine learning to provide 
            intelligent financial advisory services with real-time data analysis and personalized recommendations.
          </p>
          
          <div className="grid md:grid-cols-3 gap-8 mt-12">
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">1000+</div>
              <div className="text-primary-200">Mutual Funds Analyzed</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">24/7</div>
              <div className="text-primary-200">AI Advisory Available</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">PKR</div>
              <div className="text-primary-200">Localized Currency Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-emerald-500 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-4 h-4 text-white" />
                </div>
                <span className="text-lg font-semibold">Asset Management</span>
              </div>
              <p className="text-gray-400">
                Your trusted AI-powered financial advisor for intelligent investment decisions.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Services</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Mutual Fund Advisory</li>
                <li>Portfolio Management</li>
                <li>Risk Assessment</li>
                <li>Market Analysis</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Investment Guide</li>
                <li>Market Reports</li>
                <li>Educational Content</li>
                <li>FAQ</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li>support@assetmanagement.com</li>
                <li>+92 XXX XXX XXXX</li>
                <li>Karachi, Pakistan</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Asset Management Platform. All rights reserved. Powered by AI technology.</p>
          </div>
        </div>
      </footer>

      {/* Chat Widget */}
      <ChatWidget />
    </div>
  );
};

export default HomePage;