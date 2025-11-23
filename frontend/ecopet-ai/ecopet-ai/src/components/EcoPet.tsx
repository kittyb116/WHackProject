import { useEffect, useState } from "react";
import petStage1 from "@/assets/pet-stage-1.png";
import petStage2 from "@/assets/pet-stage-2.png";
import petStage3 from "@/assets/pet-stage-3.png";

interface EcoPetProps {
  mood: "happy" | "energized" | "neutral" | "tired" | "exhausted";
  xp: number;
  level: number;
  isAnimating?: boolean;
}

export const EcoPet = ({ mood, xp, level, isAnimating = false }: EcoPetProps) => {
  const [petScale, setPetScale] = useState(1);

  useEffect(() => {
    // Scale pet based on level
    setPetScale(1 + (level - 1) * 0.1);
  }, [level]);

  const getMoodEmoji = () => {
    switch (mood) {
      case "energized":
        return "🌟";
      case "happy":
        return "😊";
      case "neutral":
        return "😐";
      case "tired":
        return "😔";
      case "exhausted":
        return "😩";
      default:
        return "😐";
    }
  };

  const getMoodColor = () => {
    switch (mood) {
      case "energized":
        return "text-accent";
      case "happy":
        return "text-primary";
      case "neutral":
        return "text-muted-foreground";
      case "tired":
        return "text-warning";
      case "exhausted":
        return "text-drained";
      default:
        return "text-muted-foreground";
    }
  };

  const getAnimationClass = () => {
    if (!isAnimating) return "";
    
    switch (mood) {
      case "energized":
      case "happy":
        return "animate-bounce-subtle animate-glow";
      case "tired":
      case "exhausted":
        return "animate-droop";
      default:
        return "";
    }
  };

  const xpPercentage = (xp % 100);

  const getPetImage = () => {
    if (xp < 30) return petStage1;
    if (xp <= 70) return petStage2;
    return petStage3;
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Pet Display */}
      <div 
        className={`relative transition-all duration-500 ${getAnimationClass()}`}
        style={{ transform: `scale(${petScale})` }}
      >
        <div className="relative">
          {/* Pet body with glow effect for energized state */}
          <img 
            src={getPetImage()}
            alt="EcoPet"
            className={`w-48 h-48 transition-all duration-300 ${
              mood === "energized" ? "animate-glow" : ""
            }`}
          />
          
          {/* Mood indicator */}
          <div className="absolute -top-2 -right-2 text-4xl">
            {getMoodEmoji()}
          </div>
        </div>
      </div>

      {/* Level Badge */}
      <div className="bg-primary/10 backdrop-blur-sm border border-primary/20 rounded-full px-4 py-1">
        <span className="text-sm font-semibold text-primary">
          Level {level}
        </span>
      </div>

      {/* XP Progress Bar */}
      <div className="w-full max-w-xs space-y-2">
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>XP Progress</span>
          <span>{xp % 100}/100</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-500 ease-out"
            style={{ width: `${xpPercentage}%` }}
          />
        </div>
      </div>
    </div>
  );
};