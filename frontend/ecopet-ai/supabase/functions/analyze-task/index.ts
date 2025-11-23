import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Model efficiency data (carbon per request in grams)
const MODEL_EFFICIENCY = {
  "google/gemini-2.5-flash-lite": { carbon: 0.008, category: "very-efficient" },
  "google/gemini-2.5-flash": { carbon: 0.015, category: "efficient" },
  "google/gemini-2.5-pro": { carbon: 0.045, category: "moderate" },
  "openai/gpt-5-nano": { carbon: 0.012, category: "efficient" },
  "openai/gpt-5-mini": { carbon: 0.028, category: "moderate" },
  "openai/gpt-5": { carbon: 0.062, category: "heavy" },
};

// Task type detection and model recommendations
const TASK_RECOMMENDATIONS = {
  "classification": ["google/gemini-2.5-flash-lite", "openai/gpt-5-nano"],
  "summarization": ["google/gemini-2.5-flash-lite", "google/gemini-2.5-flash"],
  "simple-qa": ["google/gemini-2.5-flash", "openai/gpt-5-nano"],
  "complex-reasoning": ["google/gemini-2.5-pro", "openai/gpt-5"],
  "creative-writing": ["google/gemini-2.5-flash", "openai/gpt-5-mini"],
  "code-generation": ["google/gemini-2.5-flash", "openai/gpt-5-mini"],
  "translation": ["google/gemini-2.5-flash-lite", "google/gemini-2.5-flash"],
  "analysis": ["google/gemini-2.5-pro", "openai/gpt-5-mini"],
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { prompt, currentModel = "google/gemini-2.5-flash" } = await req.json();

    if (!prompt || typeof prompt !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Prompt is required and must be a string' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Use Lovable AI to detect task type
    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
    if (!LOVABLE_API_KEY) {
      throw new Error('LOVABLE_API_KEY is not configured');
    }

    const taskDetectionResponse = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LOVABLE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'google/gemini-2.5-flash-lite',
        messages: [
          {
            role: 'system',
            content: `You are a task classifier. Analyze the user prompt and classify it into ONE of these categories:
- classification: Categorizing or labeling data
- summarization: Condensing longer text
- simple-qa: Straightforward questions with clear answers
- complex-reasoning: Multi-step logical problems or deep analysis
- creative-writing: Stories, poems, or creative content
- code-generation: Writing or explaining code
- translation: Converting between languages
- analysis: Data interpretation or detailed examination

Respond with ONLY the category name, nothing else.`
          },
          {
            role: 'user',
            content: prompt
          }
        ],
      }),
    });

    if (!taskDetectionResponse.ok) {
      console.error('Task detection failed:', await taskDetectionResponse.text());
      throw new Error('Failed to detect task type');
    }

    const taskData = await taskDetectionResponse.json();
    let detectedTask = taskData.choices?.[0]?.message?.content?.trim().toLowerCase() || "simple-qa";
    
    // Ensure it's a valid task type
    if (!TASK_RECOMMENDATIONS[detectedTask as keyof typeof TASK_RECOMMENDATIONS]) {
      detectedTask = "simple-qa";
    }

    console.log('Detected task:', detectedTask);

    // Get recommended models for this task
    const recommendedModels = TASK_RECOMMENDATIONS[detectedTask as keyof typeof TASK_RECOMMENDATIONS];
    
    // Select 3 models ranked by efficiency for this task type
    // Sort all models by carbon footprint for this task
    const allModels = Object.keys(MODEL_EFFICIENCY) as Array<keyof typeof MODEL_EFFICIENCY>;
    const sortedModels = allModels
      .filter(model => 
        recommendedModels.includes(model) || 
        MODEL_EFFICIENCY[model].category === MODEL_EFFICIENCY[recommendedModels[0] as keyof typeof MODEL_EFFICIENCY].category
      )
      .sort((a, b) => MODEL_EFFICIENCY[a].carbon - MODEL_EFFICIENCY[b].carbon)
      .slice(0, 3);
    
    // Create 3 model options with XP values
    const modelOptions = sortedModels.map((model, index) => ({
      model,
      carbon: MODEL_EFFICIENCY[model].carbon,
      category: MODEL_EFFICIENCY[model].category,
      xp: index === 0 ? 20 : index === 1 ? 10 : 5, // Highest to lowest XP
      rank: index + 1
    }));
    
    const bestModel = modelOptions[0].model;
    const currentModelData = MODEL_EFFICIENCY[currentModel as keyof typeof MODEL_EFFICIENCY] || MODEL_EFFICIENCY["google/gemini-2.5-flash"];
    const bestModelData = MODEL_EFFICIENCY[bestModel as keyof typeof MODEL_EFFICIENCY];
    
    const isRecommended = modelOptions.some(opt => opt.model === currentModel);
    const carbonSaved = currentModelData.carbon - bestModelData.carbon;

    return new Response(
      JSON.stringify({
        detectedTask,
        modelOptions,
        currentModel,
        isRecommended,
        carbonSaved: Math.max(0, carbonSaved),
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200 
      }
    );

  } catch (error) {
    console.error('Error in analyze-task function:', error);
    return new Response(
      JSON.stringify({ 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
});