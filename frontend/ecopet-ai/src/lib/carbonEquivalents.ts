// Convert carbon grams to relatable everyday equivalents

interface CarbonEquivalent {
  comparison: string;
  emoji: string;
}

export const getCarbonEquivalent = (carbonGrams: number): CarbonEquivalent => {
  // Different equivalents based on the scale of emissions
  
  // Very small amounts (< 0.01g) - use breaths or LED seconds
  if (carbonGrams < 0.01) {
    const breaths = Math.max(1, Math.round(carbonGrams / 0.001));
    return {
      comparison: `${breaths} breath${breaths === 1 ? '' : 's'} of fresh air`,
      emoji: '🌬️'
    };
  }
  
  // Small amounts (0.01g - 0.05g) - use LED light seconds
  if (carbonGrams < 0.05) {
    const ledSeconds = Math.round(carbonGrams / 0.001);
    return {
      comparison: `${ledSeconds} seconds of an LED light glowing`,
      emoji: '💡'
    };
  }
  
  // Medium-small amounts (0.05g - 0.2g) - use phone charging
  if (carbonGrams < 0.2) {
    const phoneSeconds = Math.round(carbonGrams / 0.01);
    return {
      comparison: `${phoneSeconds} seconds of charging your phone`,
      emoji: '📱'
    };
  }
  
  // Medium amounts (0.2g - 1g) - use walking
  if (carbonGrams < 1) {
    const walkSeconds = Math.round(carbonGrams / 0.015);
    return {
      comparison: `${walkSeconds} seconds of walking`,
      emoji: '🚶'
    };
  }
  
  // Larger amounts (1g+) - use streaming video
  const streamMinutes = (carbonGrams / 0.055).toFixed(1);
  return {
    comparison: `${streamMinutes} minutes of streaming video`,
    emoji: '📺'
  };
};

export const formatCarbonSavings = (carbonSaved: number): string => {
  const { comparison, emoji } = getCarbonEquivalent(carbonSaved);
  return `${emoji} That's like saving ${comparison}!`;
};

export const formatCarbonUsage = (carbonUsed: number): string => {
  const { comparison, emoji } = getCarbonEquivalent(carbonUsed);
  return `${emoji} About the same as ${comparison}`;
};
