"use client";

import React, { useState } from 'react';

export default function LineChart({ data }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);
  
  const maxSwaps = Math.max(...data.map(d => d.swaps));
  const peakIndex = data.findIndex(d => d.swaps === maxSwaps);
  
  const width = 100;
  const height = 40;
  const padding = { top: 2, right: 2, bottom: 2, left: 2 };
  
  const xScale = (i) => padding.left + (i / (data.length - 1)) * (width - padding.left - padding.right);
  const yScale = (val) => height - padding.bottom - (val / (maxSwaps || 1)) * (height - padding.top - padding.bottom);
  
  // Calculate points
  const points = data.map((d, i) => ({
    x: xScale(i),
    y: yScale(d.swaps),
    original: d
  }));

  // Generate smooth path using Cubic Bezier curves
  const getSmoothPath = (points) => {
    if (points.length === 0) return "";
    if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;

    let path = `M ${points[0].x} ${points[0].y}`;

    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i === 0 ? 0 : i - 1];
      const p1 = points[i];
      const p2 = points[i + 1];
      const p3 = points[i + 2] || p2;

      const cp1x = p1.x + (p2.x - p0.x) * 0.15; // Tension factor
      const cp1y = p1.y + (p2.y - p0.y) * 0.15;
      const cp2x = p2.x - (p3.x - p1.x) * 0.15;
      const cp2y = p2.y - (p3.y - p1.y) * 0.15;

      path += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
    }

    return path;
  };

  const pathD = getSmoothPath(points);
  const areaD = `${pathD} L ${points[points.length - 1].x} ${height - padding.bottom} L ${points[0].x} ${height - padding.bottom} Z`;

  return (
    <div className="relative">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-48" preserveAspectRatio="none">
        <defs>
          <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#22c55e" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#22c55e" stopOpacity="0" />
          </linearGradient>
        </defs>
        
        {/* Area fill */}
        <path d={areaD} fill="url(#areaGradient)" />
        
        {/* Line */}
        <path d={pathD} fill="none" stroke="#22c55e" strokeWidth="0.4" strokeLinecap="round" strokeLinejoin="round" />
        
        {/* Peak point */}
        <circle 
          cx={points[peakIndex].x} 
          cy={points[peakIndex].y} 
          r="1" 
          fill="#22c55e" 
        />
        
        {/* Interactive points */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="1.5"
            fill="transparent"
            className="cursor-pointer"
            onMouseEnter={() => setHoveredPoint({ ...p.original, x: p.x, y: p.y })}
            onMouseLeave={() => setHoveredPoint(null)}
          />
        ))}
      </svg>
      
      {/* X-axis labels */}
      <div className="flex justify-between text-xs text-gray-400 mt-2 px-1">
        <span>6AM</span>
        <span>12PM</span>
        <span>6PM</span>
        <span>11PM</span>
      </div>
      
      {/* Tooltip */}
      {hoveredPoint && (
        <div 
          className="absolute bg-gray-900 text-white text-xs px-2 py-1 rounded pointer-events-none z-10"
          style={{ 
            left: `${hoveredPoint.x}%`, 
            top: `${hoveredPoint.y}%`,
            transform: 'translate(-50%, -120%)'
          }}
        >
          {hoveredPoint.hour}:00 · {hoveredPoint.swaps} swaps
        </div>
      )}
      
      {/* Peak label */}
      <div 
        className="absolute text-xs text-green-600 font-medium"
        style={{ 
          left: `${(peakIndex / (data.length - 1)) * 100}%`, 
          top: '0',
          transform: 'translateX(-50%)'
        }}
      >
        Peak: {maxSwaps}
      </div>
    </div>
  );
}
