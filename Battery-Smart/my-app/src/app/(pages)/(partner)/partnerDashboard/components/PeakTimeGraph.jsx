"use client";

import React, { useState } from 'react';
import LineChart from './LineChart';

export default function PeakTimeGraph({ peakData }) {
  const [timeRange, setTimeRange] = useState('today');

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-medium text-gray-900">Peak Swap Hours</h2>
        <div className="flex gap-1 bg-gray-100 rounded-lg p-0.5">
          <button 
            onClick={() => setTimeRange('today')}
            className={`text-xs px-3 py-1 rounded-md transition-colors ${
              timeRange === 'today' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            }`}
          >
            Today
          </button>
          <button 
            onClick={() => setTimeRange('week')}
            className={`text-xs px-3 py-1 rounded-md transition-colors ${
              timeRange === 'week' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            }`}
          >
            7 Days
          </button>
        </div>
      </div>
      <LineChart data={peakData[timeRange]} />
    </div>
  );
}
