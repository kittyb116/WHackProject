-- Create pet_state table to track EcoPet status
CREATE TABLE public.pet_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  xp INTEGER NOT NULL DEFAULT 0,
  level INTEGER NOT NULL DEFAULT 1,
  mood TEXT NOT NULL DEFAULT 'neutral',
  total_carbon_saved NUMERIC(10, 4) NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(user_id)
);

-- Create task_history table to track user tasks
CREATE TABLE public.task_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  prompt TEXT NOT NULL,
  detected_task TEXT NOT NULL,
  recommended_model TEXT NOT NULL,
  chosen_model TEXT NOT NULL,
  carbon_impact NUMERIC(10, 4) NOT NULL,
  carbon_saved NUMERIC(10, 4) NOT NULL,
  xp_change INTEGER NOT NULL,
  was_efficient BOOLEAN NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.pet_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for pet_state
CREATE POLICY "Users can view their own pet state"
  ON public.pet_state
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own pet state"
  ON public.pet_state
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own pet state"
  ON public.pet_state
  FOR UPDATE
  USING (auth.uid() = user_id);

-- RLS Policies for task_history
CREATE POLICY "Users can view their own task history"
  ON public.task_history
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own task history"
  ON public.task_history
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Create function for updating timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for pet_state
CREATE TRIGGER update_pet_state_updated_at
  BEFORE UPDATE ON public.pet_state
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create indexes for better performance
CREATE INDEX idx_pet_state_user_id ON public.pet_state(user_id);
CREATE INDEX idx_task_history_user_id ON public.task_history(user_id);
CREATE INDEX idx_task_history_created_at ON public.task_history(created_at DESC);