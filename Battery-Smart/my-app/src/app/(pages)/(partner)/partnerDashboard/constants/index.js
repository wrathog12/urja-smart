// Peak time swap data - morning and evening rush hours
export const PEAK_DATA = {
  today: [
    { hour: '6', swaps: 4 },
    { hour: '7', swaps: 12 },
    { hour: '8', swaps: 28 },
    { hour: '9', swaps: 35 },
    { hour: '10', swaps: 22 },
    { hour: '11', swaps: 15 },
    { hour: '12', swaps: 18 },
    { hour: '13', swaps: 14 },
    { hour: '14', swaps: 10 },
    { hour: '15', swaps: 8 },
    { hour: '16', swaps: 12 },
    { hour: '17', swaps: 25 },
    { hour: '18', swaps: 42 },
    { hour: '19', swaps: 38 },
    { hour: '20', swaps: 28 },
    { hour: '21', swaps: 15 },
    { hour: '22', swaps: 8 },
    { hour: '23', swaps: 3 },
  ],
  week: [
    { hour: '6', swaps: 28 },
    { hour: '7', swaps: 85 },
    { hour: '8', swaps: 196 },
    { hour: '9', swaps: 245 },
    { hour: '10', swaps: 154 },
    { hour: '11', swaps: 105 },
    { hour: '12', swaps: 126 },
    { hour: '13', swaps: 98 },
    { hour: '14', swaps: 70 },
    { hour: '15', swaps: 56 },
    { hour: '16', swaps: 84 },
    { hour: '17', swaps: 175 },
    { hour: '18', swaps: 294 },
    { hour: '19', swaps: 266 },
    { hour: '20', swaps: 196 },
    { hour: '21', swaps: 105 },
    { hour: '22', swaps: 56 },
    { hour: '23', swaps: 21 },
  ]
};

export const BATTERY_STATUS = {
  charging: 12,
  available: 24,
  inUse: 18,
  faulty: 2
};

export const ALERTS = [
  { id: 1, type: 'critical', message: 'Battery #B-0847 overheating', time: '2 min ago' },
  { id: 2, type: 'warning', message: 'Charger slot 3 not responding', time: '15 min ago' },
];

export const RECENT_SWAPS = [
  { time: '14:02', batteryId: 'B-1234', vehicle: '2W' },
  { time: '13:58', batteryId: 'B-0987', vehicle: '3W' },
  { time: '13:45', batteryId: 'B-1122', vehicle: '2W' },
  { time: '13:32', batteryId: 'B-0654', vehicle: '2W' },
  { time: '13:28', batteryId: 'B-0789', vehicle: '3W' },
];

export const CHARGER_STATUS = {
  active: 6,
  total: 8,
  gridOn: true,
  backupOn: false
};
