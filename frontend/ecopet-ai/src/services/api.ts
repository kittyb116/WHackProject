const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ModelRecommendation {
  rank: number;
  model: string;
  energy_cost: number;
  energy_saved: number;
  energy_points: number;
  savings_message: string;
  comparisons: {
    google_searches: number;
    miles: number;
    streaming_minutes: number;
    led_minutes: number;
  };
  performance_rank: number;
  source: string;
}

export interface RecommendResponse {
  category: string;
  recommendations: ModelRecommendation[];
  baseline_comparison: string;
  comparison_unit: string;
  energy_system: {
    rank_1: number;
    rank_2: number;
    rank_3: number;
    none_selected: number;
  };
}

export interface ModelOption {
  model: string;
  carbon: number;
  category: string;
  xp: number;
  rank: number;
  savingsMessage: string;
  comparisons: {
    google_searches: number;
    miles: number;
    streaming_minutes: number;
    led_minutes: number;
  };
}

export interface TaskAnalysis {
  detectedTask: string;
  modelOptions: ModelOption[];
  currentModel: string;
  isRecommended: boolean;
  carbonSaved: number;
}

export async function analyzeTask(prompt: string, currentModel: string): Promise<TaskAnalysis> {
  const response = await fetch(`${API_URL}/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const data: RecommendResponse = await response.json();

  // Transform backend response to frontend format
  const modelOptions: ModelOption[] = data.recommendations.map((rec) => ({
    model: rec.model,
    carbon: rec.energy_cost,
    category: data.category,
    xp: rec.energy_points,
    rank: rec.rank,
    savingsMessage: rec.savings_message,
    comparisons: rec.comparisons,
  }));

  // Check if current model is in recommendations
  const isRecommended = modelOptions.some(opt => opt.model === currentModel);

  // Calculate potential carbon saved (difference from highest to lowest)
  const carbonSaved = modelOptions.length > 1
    ? modelOptions[modelOptions.length - 1].carbon - modelOptions[0].carbon
    : 0;

  return {
    detectedTask: data.category,
    modelOptions,
    currentModel,
    isRecommended,
    carbonSaved,
  };
}

export interface ExecuteTaskResult {
  result: string;
  carbonImpact: number;
  carbonSaved: number;
  xpChange: number;
}

export async function executeTask(
  _prompt: string,
  model: string,
  detectedTask: string,
  modelOptions: ModelOption[]
): Promise<ExecuteTaskResult> {
  // Find the selected model option
  const selectedOption = modelOptions.find(opt => opt.model === model);

  if (!selectedOption) {
    throw new Error('Selected model not found in options');
  }

  // GPT-4 baseline for comparison
  const GPT4_BASELINE_CO2 = 4.32;

  // Calculate carbon impact and savings (compared to GPT-4)
  const carbonImpact = selectedOption.carbon;
  const carbonSaved = GPT4_BASELINE_CO2 - selectedOption.carbon;
  const xpChange = selectedOption.xp;

  // Build result message based on user's choice
  const modelName = model.split('/').pop() || model;
  let result: string;

  // Include savings message for all choices
  const savingsContext = selectedOption.savingsMessage ? `\n\n${selectedOption.savingsMessage}` : '';

  if (selectedOption.rank === 1) {
    result = `Great choice! You selected ${modelName}, the most energy-efficient model for this ${detectedTask} task.\n\nCarbon footprint: ${carbonImpact.toFixed(3)}g CO2${savingsContext}`;
  } else if (selectedOption.rank === 2) {
    result = `Good choice! You selected ${modelName}, a balanced option for this ${detectedTask} task.\n\nCarbon footprint: ${carbonImpact.toFixed(3)}g CO2${savingsContext}`;
  } else {
    result = `You selected ${modelName} for this ${detectedTask} task.\n\nCarbon footprint: ${carbonImpact.toFixed(3)}g CO2${savingsContext}\n\nTip: Consider using more efficient models to help your EcoPet thrive!`;
  }

  return {
    result,
    carbonImpact,
    carbonSaved: Math.max(0, carbonSaved),
    xpChange,
  };
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`);
    const data = await response.json();
    return data.status === 'healthy';
  } catch {
    return false;
  }
}
