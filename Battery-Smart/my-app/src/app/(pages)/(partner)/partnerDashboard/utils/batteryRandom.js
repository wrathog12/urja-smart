/**
 * Generates random battery status values while keeping the total constant
 * @param {number} total - Total number of batteries
 * @returns {Object} Object with charging, available, inUse, faulty counts
 */
export function generateRandomBatteryStatus(total = 56) {
  // Faulty is typically low (0-4)
  const faulty = Math.floor(Math.random() * 5);
  const remaining = total - faulty;
  
  // Distribute remaining across charging, available, inUse
  const charging = Math.floor(Math.random() * (remaining * 0.4)) + Math.floor(remaining * 0.1);
  const afterCharging = remaining - charging;
  
  const available = Math.floor(Math.random() * (afterCharging * 0.6)) + Math.floor(afterCharging * 0.2);
  const inUse = afterCharging - available;
  
  return {
    charging,
    available,
    inUse,
    faulty
  };
}
