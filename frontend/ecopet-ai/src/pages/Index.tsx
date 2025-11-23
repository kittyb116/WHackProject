import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Session } from "@supabase/supabase-js";
import { AuthForm } from "@/components/AuthForm";
import { FloatingWidget } from "@/components/FloatingWidget";
import { ExtensionPanel } from "@/components/ExtensionPanel";
import { TaskInterface } from "@/components/TaskInterface";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface PetState {
  xp: number;
  level: number;
  mood: "happy" | "energized" | "neutral" | "tired" | "exhausted";
  total_carbon_saved: number;
}

const Index = () => {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [petState, setPetState] = useState<PetState>({
    xp: 0,
    level: 1,
    mood: "neutral",
    total_carbon_saved: 0,
  });
  const [lastTaskStats, setLastTaskStats] = useState<{
    carbonImpact: number;
    carbonSaved: number;
    xpChange: number;
  } | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (session?.user) {
      loadPetState();
    }
  }, [session]);

  const loadPetState = async () => {
    if (!session?.user) return;

    try {
      const { data, error } = await supabase
        .from("pet_state")
        .select("*")
        .eq("user_id", session.user.id)
        .maybeSingle();

      if (error && error.code !== "PGRST116") throw error;

      if (data) {
        setPetState({
          xp: data.xp,
          level: data.level,
          mood: data.mood as PetState["mood"],
          total_carbon_saved: parseFloat(String(data.total_carbon_saved)),
        });
      }
    } catch (error) {
      console.error("Error loading pet state:", error);
    }
  };

  const handleTaskComplete = async (taskStats?: {
    carbonImpact: number;
    carbonSaved: number;
    xpChange: number;
  }) => {
    setIsAnimating(true);
    
    if (taskStats) {
      setLastTaskStats(taskStats);
    }
    
    await loadPetState();
    setTimeout(() => setIsAnimating(false), 2000);
  };

  const handleSignOut = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      toast({
        title: "Error signing out",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-6xl animate-pulse">🌱</div>
      </div>
    );
  }

  if (!session) {
    return <AuthForm />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Compact Header */}
      <header className="border-b border-primary/10 bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="text-2xl">🌱</div>
            <div>
              <h1 className="text-lg font-bold text-primary">EcoPet</h1>
              <p className="text-xs text-muted-foreground">AI Energy Companion</p>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSignOut}
            className="gap-2 text-xs"
          >
            <LogOut className="h-3 w-3" />
            Sign Out
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-4">
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold">Try an AI Task</h2>
            <p className="text-sm text-muted-foreground">
              Enter a prompt and EcoPet will help you choose the most energy-efficient model!
            </p>
          </div>
          
          {/* Task Interface - Takes center stage */}
          <TaskInterface 
            onTaskComplete={(stats) => handleTaskComplete(stats)} 
          />
        </div>
      </main>

      {/* Floating Widget & Extension Panel */}
      <FloatingWidget
        mood={petState.mood}
        onClick={() => setIsPanelOpen(true)}
        isOpen={isPanelOpen}
      />
      <ExtensionPanel
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        petState={{
          mood: petState.mood,
          xp: petState.xp,
          level: petState.level,
          totalCarbonSaved: petState.total_carbon_saved,
        }}
        lastTaskStats={lastTaskStats || undefined}
        isAnimating={isAnimating}
      />
    </div>
  );
};

export default Index;