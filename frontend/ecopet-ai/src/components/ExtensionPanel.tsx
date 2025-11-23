import { X } from "lucide-react";
import { EcoPet } from "./EcoPet";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatCarbonSavings } from "@/lib/carbonEquivalents";

interface ExtensionPanelProps {
  isOpen: boolean;
  onClose: () => void;
  petState: {
    mood: "happy" | "energized" | "neutral" | "tired" | "exhausted";
    xp: number;
    level: number;
    totalCarbonSaved: number;
  };
  lastTaskStats?: {
    carbonImpact: number;
    carbonSaved: number;
    xpChange: number;
    equivalent?: string;
  };
  isAnimating: boolean;
}

export const ExtensionPanel = ({
  isOpen,
  onClose,
  petState,
  lastTaskStats,
  isAnimating,
}: ExtensionPanelProps) => {
  if (!isOpen) return null;

  return (
    <div
      className={`fixed bottom-6 right-6 w-96 bg-background border-2 border-primary/20 rounded-2xl shadow-2xl z-50 
        animate-slide-in-right overflow-hidden`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-primary/10 to-accent/10 p-4 flex items-center justify-between border-b border-primary/20">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🌱</span>
          <div>
            <h2 className="font-bold text-lg text-foreground">EcoPet</h2>
            <p className="text-xs text-muted-foreground">Your AI Energy Companion</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="h-8 w-8 rounded-full hover:bg-primary/10"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Pet Display */}
      <div className="p-6 bg-gradient-to-b from-background to-muted/20">
        <EcoPet
          mood={petState.mood}
          xp={petState.xp}
          level={petState.level}
          isAnimating={isAnimating}
        />
      </div>

      {/* Stats */}
      <div className="p-4 space-y-3">
        {/* Total Carbon Saved */}
        <Card className="p-3 bg-primary/5 border-primary/20">
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Total Carbon Saved</p>
            <p className="text-2xl font-bold text-primary">
              {petState.totalCarbonSaved.toFixed(3)}g CO₂
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Compared to ChatGPT-4
            </p>
          </div>
        </Card>

        {/* Last Task Stats */}
        {lastTaskStats && (
          <Card className="p-3 bg-muted/30 border-border space-y-2">
            <p className="text-xs font-semibold text-foreground">Last Task Impact</p>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Carbon Used:</span>
                <span className="font-medium">{lastTaskStats.carbonImpact.toFixed(4)}g</span>
              </div>
              {lastTaskStats.carbonSaved > 0 && (
                <>
                  <div className="flex justify-between text-primary">
                    <span>Carbon Saved:</span>
                    <span className="font-medium">-{lastTaskStats.carbonSaved.toFixed(4)}g</span>
                  </div>
                  <div className="pt-2 text-xs text-muted-foreground">
                    {formatCarbonSavings(lastTaskStats.carbonSaved)}
                  </div>
                </>
              )}
              <div className="flex justify-between pt-2 border-t border-border">
                <span className={lastTaskStats.xpChange > 0 ? "text-primary" : "text-drained"}>
                  XP Change:
                </span>
                <span className={`font-bold ${lastTaskStats.xpChange > 0 ? "text-primary" : "text-drained"}`}>
                  {lastTaskStats.xpChange > 0 ? "+" : ""}{lastTaskStats.xpChange} XP
                </span>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
