"use client";

import React from 'react';
import { Zap, IndianRupee, Battery, Clock } from 'lucide-react';

// Components
import KpiCard from './components/KpiCard';
import PeakTimeGraph from './components/PeakTimeGraph';
import BatteryStatus from './components/BatteryStatus';
import ChargerStatus from './components/ChargerStatus';
import AlertsPanel from './components/AlertsPanel';
import RecentSwaps from './components/RecentSwaps';

// Constants
import { PEAK_DATA, BATTERY_STATUS, ALERTS, RECENT_SWAPS, CHARGER_STATUS } from './constants';

const KPIS = [
  { label: 'Swaps Today', value: '156', icon: Zap },
  { label: 'Revenue', value: '₹12,480', icon: IndianRupee },
  { label: 'Available', value: '24', icon: Battery },
  { label: 'Avg Time', value: '2:45', icon: Clock },
];

export default function PartnerDashboard() {
  return (
    <div className="min-h-screen bg-gray-50 pb-8">
      <div className="max-screen p-4 space-y-6">
        
        {/* Header */}
        <div className="pt-2">
          <h1 className="text-xl font-semibold text-gray-900">Station Dashboard</h1>
          <p className="text-sm text-gray-500">Koramangala Hub · Live</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 gap-3">
          {KPIS.map((kpi, i) => (
            <KpiCard key={i} label={kpi.label} value={kpi.value} icon={kpi.icon} />
          ))}
        </div>

        {/* Peak Time Graph */}
        <PeakTimeGraph peakData={PEAK_DATA} />

        {/* Battery Status */}
        <BatteryStatus status={BATTERY_STATUS} />

        {/* Charger Status & Alerts Row */}
        <div className="flex gap-4">
          <ChargerStatus 
            active={CHARGER_STATUS.active} 
            total={CHARGER_STATUS.total} 
            gridOn={CHARGER_STATUS.gridOn} 
            backupOn={CHARGER_STATUS.backupOn} 
          />
          <AlertsPanel alerts={ALERTS} />
        </div>

        {/* Recent Swaps */}
        <RecentSwaps swaps={RECENT_SWAPS} />
      </div>
    </div>
  );
}
