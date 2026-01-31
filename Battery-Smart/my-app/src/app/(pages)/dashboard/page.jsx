"use client";

import React, { useState } from 'react';
import { 
  Battery, 
  Zap, 
  MapPin, 
  IndianRupee, 
  Route,
  Heart,
  Download,
  Eye,
  CreditCard,
  TrendingUp,
  Calendar,
  FileText,
  ChevronDown
} from 'lucide-react';

// Dummy data for the dashboard
const DUMMY_DATA = {
  todaySummary: {
    swapsToday: 6,
    distanceCovered: 78,
    totalSpent: 480,
    tripsCompleted: 24,
    batteryStatus: 'Healthy'
  },
  swapHistory: {
    today: [
      { time: '8AM', swaps: 1 },
      { time: '10AM', swaps: 2 },
      { time: '12PM', swaps: 1 },
      { time: '2PM', swaps: 0 },
      { time: '4PM', swaps: 1 },
      { time: '6PM', swaps: 1 }
    ],
    last7Days: [
      { date: 'Mon', swaps: 4 },
      { date: 'Tue', swaps: 6 },
      { date: 'Wed', swaps: 3 },
      { date: 'Thu', swaps: 8 },
      { date: 'Fri', swaps: 5 },
      { date: 'Sat', swaps: 7 },
      { date: 'Sun', swaps: 6 }
    ],
    last30Days: [
      { date: 'Week 1', swaps: 28 },
      { date: 'Week 2', swaps: 35 },
      { date: 'Week 3', swaps: 42 },
      { date: 'Week 4', swaps: 38 }
    ]
  },
  spending: {
    daily: [
      { date: 'Mon', amount: 320 },
      { date: 'Tue', amount: 480 },
      { date: 'Wed', amount: 240 },
      { date: 'Thu', amount: 640 },
      { date: 'Fri', amount: 400 },
      { date: 'Sat', amount: 560 },
      { date: 'Sun', amount: 480 }
    ],
    breakdown: {
      batterySwaps: 2800,
      penalties: 150,
      extraServices: 200
    }
  },
  invoices: [
    { id: 'INV-2026-001', dateRange: 'Jan 1 - Jan 15', swaps: 45, amount: 3600, status: 'Paid' },
    { id: 'INV-2026-002', dateRange: 'Jan 16 - Jan 28', swaps: 38, amount: 3040, status: 'Pending' },
    { id: 'INV-2025-024', dateRange: 'Dec 16 - Dec 31', swaps: 52, amount: 4160, status: 'Paid' },
    { id: 'INV-2025-023', dateRange: 'Dec 1 - Dec 15', swaps: 48, amount: 3840, status: 'Paid' }
  ]
};

// Simple Bar Chart Component
function BarChart({ data, xKey, yKey, maxValue, color = 'bg-green-500' }) {
  const max = maxValue || Math.max(...data.map(d => d[yKey]));
  
  return (
    <div className="flex items-end gap-2 h-40">
      {data.map((item, index) => (
        <div key={index} className="flex flex-col items-center flex-1">
          <div className="w-full flex flex-col items-center">
            <span className="text-xs text-gray-500 mb-1">{item[yKey]}</span>
            <div 
              className={`w-full ${color} rounded-t-sm transition-all duration-300`}
              style={{ height: `${(item[yKey] / max) * 100}px` }}
            />
          </div>
          <span className="text-xs text-gray-500 mt-2">{item[xKey]}</span>
        </div>
      ))}
    </div>
  );
}

// Spending Breakdown Component (Simple horizontal bars)
function SpendingBreakdown({ data }) {
  const total = Object.values(data).reduce((a, b) => a + b, 0);
  const items = [
    { label: 'Battery Swaps', value: data.batterySwaps, color: 'bg-green-500' },
    { label: 'Penalties', value: data.penalties, color: 'bg-red-400' },
    { label: 'Extra Services', value: data.extraServices, color: 'bg-emerald-400' }
  ];
  
  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <div key={index}>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">{item.label}</span>
            <span className="font-medium text-gray-800">₹{item.value.toLocaleString()}</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className={`h-full ${item.color} rounded-full transition-all duration-500`}
              style={{ width: `${(item.value / total) * 100}%` }}
            />
          </div>
        </div>
      ))}
      <div className="pt-2 border-t border-gray-200">
        <div className="flex justify-between">
          <span className="text-gray-600 font-medium">Total</span>
          <span className="font-semibold text-gray-800">₹{total.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [swapHistoryFilter, setSwapHistoryFilter] = useState('last7Days');
  const [spendingFilter, setSpendingFilter] = useState('daily');
  
  const { todaySummary, swapHistory, spending, invoices } = DUMMY_DATA;
  
  const summaryCards = [
    { 
      label: 'Swaps Today', 
      value: todaySummary.swapsToday, 
      icon: Zap, 
      color: 'text-green-500',
      bgColor: 'bg-green-50'
    },
    { 
      label: 'Distance Covered', 
      value: `${todaySummary.distanceCovered} km`, 
      icon: MapPin, 
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-50'
    },
    { 
      label: 'Total Spent Today', 
      value: `₹${todaySummary.totalSpent}`, 
      icon: IndianRupee, 
      color: 'text-amber-500',
      bgColor: 'bg-amber-50'
    },
    { 
      label: 'Trips Completed', 
      value: todaySummary.tripsCompleted, 
      icon: Route, 
      color: 'text-violet-500',
      bgColor: 'bg-violet-50'
    },
    { 
      label: 'Battery Status', 
      value: todaySummary.batteryStatus, 
      icon: Heart, 
      color: 'text-rose-500',
      bgColor: 'bg-rose-50'
    }
  ];
  
  return (
    <div className="p-6 md:p-8 w-screen space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold text-gray-800">Dashboard</h1>
        <p className="text-gray-500 mt-1">Welcome back! Here's your battery usage overview.</p>
      </div>
      
      {/* Section 1: Today's Summary */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Battery className="w-5 h-5 text-green-500" />
          <h2 className="text-lg font-semibold text-gray-800">Today's Summary</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {summaryCards.map((card, index) => (
            <div 
              key={index}
              className="bg-white rounded-xl border border-gray-200 p-4 hover:border-green-400 transition-colors"
            >
              <div className={`w-10 h-10 ${card.bgColor} rounded-lg flex items-center justify-center mb-3`}>
                <card.icon className={`w-5 h-5 ${card.color}`} />
              </div>
              <p className="text-2xl font-semibold text-gray-800">{card.value}</p>
              <p className="text-sm text-gray-500 mt-1">{card.label}</p>
            </div>
          ))}
        </div>
      </section>
      
      {/* Section 2: Usage Over Time */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-500" />
            <h2 className="text-lg font-semibold text-gray-800">Swap History</h2>
          </div>
          <div className="relative">
            <select
              value={swapHistoryFilter}
              onChange={(e) => setSwapHistoryFilter(e.target.value)}
              className="appearance-none bg-white border border-gray-200 rounded-lg px-4 py-2 pr-8 text-sm text-gray-600 focus:outline-none focus:border-green-500"
            >
              <option value="today">Today</option>
              <option value="last7Days">Last 7 Days</option>
              <option value="last30Days">Last 30 Days</option>
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <BarChart 
            data={swapHistory[swapHistoryFilter]} 
            xKey={swapHistoryFilter === 'today' ? 'time' : 'date'}
            yKey="swaps"
            color="bg-green-500"
          />
        </div>
      </section>
      
      {/* Section 3: Spending Dashboard */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <IndianRupee className="w-5 h-5 text-green-500" />
          <h2 className="text-lg font-semibold text-gray-800">Spending Dashboard</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Spending Over Time */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-gray-700">Money Spent Over Time</h3>
              <div className="relative">
                <select
                  value={spendingFilter}
                  onChange={(e) => setSpendingFilter(e.target.value)}
                  className="appearance-none bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 pr-7 text-xs text-gray-600 focus:outline-none focus:border-green-500"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
                <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-400 pointer-events-none" />
              </div>
            </div>
            <BarChart 
              data={spending.daily} 
              xKey="date"
              yKey="amount"
              color="bg-emerald-400"
            />
          </div>
          
          {/* Monthly Breakdown */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-medium text-gray-700 mb-4">Monthly Spend Breakdown</h3>
            <SpendingBreakdown data={spending.breakdown} />
          </div>
        </div>
      </section>
      
      {/* Section 4: Invoices & Payments */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-5 h-5 text-green-500" />
          <h2 className="text-lg font-semibold text-gray-800">Invoices & Payments</h2>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="text-left px-6 py-4 text-sm font-medium text-gray-600">Invoice ID</th>
                  <th className="text-left px-6 py-4 text-sm font-medium text-gray-600">Date Range</th>
                  <th className="text-left px-6 py-4 text-sm font-medium text-gray-600">Swaps</th>
                  <th className="text-left px-6 py-4 text-sm font-medium text-gray-600">Amount</th>
                  <th className="text-left px-6 py-4 text-sm font-medium text-gray-600">Status</th>
                  <th className="text-left px-6 py-4 text-sm font-medium text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice, index) => (
                  <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <span className="font-mono text-sm text-gray-800">{invoice.id}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-600">{invoice.dateRange}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-800">{invoice.swaps}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-medium text-gray-800">₹{invoice.amount.toLocaleString()}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                        invoice.status === 'Paid' 
                          ? 'bg-emerald-50 text-emerald-600' 
                          : 'bg-amber-50 text-amber-600'
                      }`}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button 
                          className="p-2 text-gray-400 hover:text-green-500 hover:bg-green-50 rounded-lg transition-colors"
                          title="Download PDF"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button 
                          className="p-2 text-gray-400 hover:text-green-500 hover:bg-green-50 rounded-lg transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {invoice.status === 'Pending' && (
                          <button 
                            className="px-3 py-1.5 bg-green-500 text-white text-xs font-medium rounded-lg hover:bg-green-600 transition-colors flex items-center gap-1"
                          >
                            <CreditCard className="w-3 h-3" />
                            Pay Now
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}