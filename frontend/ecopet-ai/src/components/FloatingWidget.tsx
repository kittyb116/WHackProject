import { useState } from "react";
import { Leaf } from "lucide-react";

interface FloatingWidgetProps {
  mood: "happy" | "energized" | "neutral" | "tired" | "exhausted";
  onClick: () => void;
  isOpen: boolean;
}

export const FloatingWidget = ({ mood, onClick, isOpen }: FloatingWidgetProps) => {
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
        return "bg-accent border-accent";
      case "happy":
        return "bg-primary border-primary";
      case "neutral":
        return "bg-muted border-muted-foreground";
      case "tired":
        return "bg-warning border-warning";
      case "exhausted":
        return "bg-drained border-drained";
      default:
        return "bg-muted border-muted-foreground";
    }
  };

  const getAnimationClass = () => {
    switch (mood) {
      case "energized":
      case "happy":
        return "animate-bounce-subtle";
      case "tired":
      case "exhausted":
        return "animate-pulse-slow";
      default:
        return "";
    }
  };

  if (isOpen) return null;

  return (
    <button
      onClick={onClick}
      className={`fixed bottom-6 right-6 w-16 h-16 rounded-full shadow-lg border-4 ${getMoodColor()} ${getAnimationClass()} 
        flex items-center justify-center text-3xl transition-all duration-300 hover:scale-110 z-50 cursor-pointer`}
      aria-label="Open EcoPet panel"
    >
      <span className="relative">
        🌱
        <span className="absolute -top-1 -right-1 text-xl">{getMoodEmoji()}</span>
      </span>
    </button>
  );
};
