"use client";

import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import StatusBar from './StatusBar';
import { generateRandomBatteryStatus } from '../utils/batteryRandom';

export default function BatteryStatus({ status }) {
  const total = Object.values(status).reduce((a, b) => a + b, 0);
  const [currentStatus, setCurrentStatus] = useState(status);

  useEffect(() => {
    // Update every 60 seconds
    const interval = setInterval(() => {
      setCurrentStatus(generateRandomBatteryStatus(total));
    }, 60000);

    return () => clearInterval(interval);
  }, [total]);

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-100">
      <h2 className="text-sm font-medium text-gray-900 mb-4">Battery Status</h2>
      <div className="space-y-3">
        <StatusBar label="Charging" count={currentStatus.charging} total={total} color="bg-blue-500" />
        <StatusBar label="Available" count={currentStatus.available} total={total} color="bg-green-500" />
        <StatusBar label="In Use" count={currentStatus.inUse} total={total} color="bg-amber-500" />
        <StatusBar 
          label="Faulty" 
          count={currentStatus.faulty} 
          total={total} 
          color="bg-red-500" 
          icon={AlertTriangle}
        />
      </div>
    </div>
  );
}
