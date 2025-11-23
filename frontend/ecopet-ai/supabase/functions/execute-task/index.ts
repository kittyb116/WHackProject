import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Missing authorization header' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: authHeader } } }
    );

    const { data: { user }, error: userError } = await supabaseClient.auth.getUser();
    
    if (userError || !user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const { 
      prompt, 
      model, 
      detectedTask,
      modelOptions, // Array of 3 recommended models with their XP values
    } = await req.json();

    if (!prompt || !model) {
      return new Response(
        JSON.stringify({ error: 'Prompt and model are required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Execute the actual AI task
    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
    if (!LOVABLE_API_KEY) {
      throw new Error('LOVABLE_API_KEY is not configured');
    }

    const aiResponse = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LOVABLE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
      }),
    });

    if (!aiResponse.ok) {
      if (aiResponse.status === 429) {
        return new Response(
          JSON.stringify({ error: 'Rate limit exceeded. Please try again later.' }),
          { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      if (aiResponse.status === 402) {
        return new Response(
          JSON.stringify({ error: 'Payment required. Please add credits to your workspace.' }),
          { status: 402, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      throw new Error('AI request failed');
    }

    const aiData = await aiResponse.json();
    const aiResult = aiData.choices?.[0]?.message?.content || '';

    // Calculate XP based on which model was chosen
    const chosenOption = modelOptions.find((opt: any) => opt.model === model);
    const xpChange = chosenOption ? chosenOption.xp : -5; // -5 if not in recommended list
    const wasEfficient = chosenOption?.rank === 1;
    const carbonImpact = chosenOption?.carbon || 0;
    const carbonSaved = modelOptions[0].carbon - carbonImpact;

    // Update pet state
    const { data: petState } = await supabaseClient
      .from('pet_state')
      .select('*')
      .eq('user_id', user.id)
      .single();

    const currentXp = petState?.xp || 0;
    const newXp = Math.max(0, currentXp + xpChange);
    const newLevel = newXp < 30 ? 1 : newXp < 70 ? 2 : 3;
    const newTotalCarbon = (petState?.total_carbon_saved || 0) + Math.max(0, carbonSaved);
    
    // Calculate mood based on total XP to show emotional progression
    let newMood = 'neutral';
    if (newXp >= 80) {
      newMood = 'energized';  // Very happy at high XP
    } else if (newXp >= 50) {
      newMood = 'happy';  // Happy at medium-high XP
    } else if (newXp >= 20) {
      newMood = 'neutral';  // Neutral at medium XP
    } else if (newXp >= 10) {
      newMood = 'tired';  // Tired at low XP
    } else {
      newMood = 'exhausted';  // Exhausted at very low XP
    }

    if (petState) {
      await supabaseClient
        .from('pet_state')
        .update({
          xp: newXp,
          level: newLevel,
          mood: newMood,
          total_carbon_saved: newTotalCarbon,
        })
        .eq('user_id', user.id);
    } else {
      await supabaseClient
        .from('pet_state')
        .insert({
          user_id: user.id,
          xp: Math.max(0, newXp),
          level: newLevel,
          mood: newMood,
          total_carbon_saved: Math.max(0, newTotalCarbon),
        });
    }

    // Record task history
    await supabaseClient
      .from('task_history')
      .insert({
        user_id: user.id,
        prompt,
        detected_task: detectedTask,
        recommended_model: modelOptions[0].model,
        chosen_model: model,
        carbon_impact: carbonImpact,
        carbon_saved: Math.max(0, carbonSaved),
        xp_change: xpChange,
        was_efficient: wasEfficient,
      });

    return new Response(
      JSON.stringify({
        result: aiResult,
        petState: {
          xp: Math.max(0, newXp),
          level: newLevel,
          mood: newMood,
          totalCarbonSaved: Math.max(0, newTotalCarbon),
        },
        carbonImpact,
        carbonSaved: Math.max(0, carbonSaved),
        xpChange,
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in execute-task function:', error);
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