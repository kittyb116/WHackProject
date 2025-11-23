import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Loader2, Sparkles, Leaf } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { formatCarbonSavings } from "@/lib/carbonEquivalents";
import { analyzeTask as apiAnalyzeTask, executeTask as apiExecuteTask, TaskAnalysis } from "@/services/api";

interface TaskInterfaceProps {
  onTaskComplete: (stats?: {
    carbonImpact: number;
    carbonSaved: number;
    xpChange: number;
  }) => void;
}

export const TaskInterface = ({ onTaskComplete }: TaskInterfaceProps) => {
  const [prompt, setPrompt] = useState("");
  const [currentModel, setCurrentModel] = useState("google/gemini-2.5-flash");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [analysis, setAnalysis] = useState<TaskAnalysis | null>(null);
  const [result, setResult] = useState<string>("");
  const { toast } = useToast();

  const analyzeTask = async () => {
    if (!prompt.trim()) {
      toast({
        title: "Empty prompt",
        description: "Please enter a task for your EcoPet to analyze.",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setAnalysis(null);
    setResult("");

    try {
      const data = await apiAnalyzeTask(prompt, currentModel);
      setAnalysis(data);
    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "Analysis failed",
        description: "Unable to analyze your task. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const executeTask = async (modelToUse: string) => {
    if (!analysis) return;

    setIsExecuting(true);

    try {
      const data = await apiExecuteTask(
        prompt,
        modelToUse,
        analysis.detectedTask,
        analysis.modelOptions
      );

      setResult(data.result);
      onTaskComplete({
        carbonImpact: data.carbonImpact,
        carbonSaved: data.carbonSaved,
        xpChange: data.xpChange,
      });

      const chosenOption = analysis.modelOptions.find(opt => opt.model === modelToUse);
      const xpGained = chosenOption ? chosenOption.xp : -5;

      toast({
        title: xpGained > 0 ? "Great choice!" : "Task completed",
        description: xpGained > 0
          ? `+${xpGained} XP earned! ${data.carbonSaved > 0 ? formatCarbonSavings(data.carbonSaved) : ''}`
          : `${xpGained} XP. Try using recommended models for more XP!`,
        variant: xpGained > 0 ? "default" : "destructive",
      });

      // Reset for next task
      setPrompt("");
      setAnalysis(null);
    } catch (error) {
      console.error('Execution error:', error);
      toast({
        title: "Execution failed",
        description: "Unable to complete your task. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="w-full max-w-2xl space-y-4">
      {/* Prompt Input */}
      <div className="space-y-2">
        <Textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your AI task... (e.g., 'Summarize this article', 'Generate a story', 'Classify this text')"
          className="min-h-[100px] resize-none"
          disabled={isAnalyzing || isExecuting}
        />
        <Button 
          onClick={analyzeTask}
          disabled={isAnalyzing || isExecuting || !prompt.trim()}
          className="w-full"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Analyzing task...
            </>
          ) : (
            <>
              <Sparkles className="mr-2 h-4 w-4" />
              Analyze Task
            </>
          )}
        </Button>
      </div>

      {/* Model Selection Cards */}
      {analysis && !result && (
        <div className="animate-grow space-y-3">
          <p className="text-sm font-medium text-muted-foreground">
            Choose a model for your task:
          </p>
          <div className="space-y-2">
            {analysis.modelOptions.map((option, index) => (
              <div
                key={option.model}
                className={`border-2 rounded-xl p-4 transition-all ${
                  index === 0
                    ? 'bg-primary/10 border-primary/30'
                    : index === 1
                    ? 'bg-accent/10 border-accent/30'
                    : 'bg-muted/50 border-border'
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {index === 0 && <Leaf className="h-4 w-4 text-primary" />}
                      <p className="text-sm font-semibold">
                        {option.model}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        index === 0
                          ? 'bg-primary/20 text-primary'
                          : index === 1
                          ? 'bg-accent/20 text-accent'
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        {index === 0 ? 'Most Efficient' : index === 1 ? 'Balanced' : 'Standard'}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      +{option.xp} XP • {option.carbon.toFixed(3)}g CO2
                    </p>
                  </div>
                  <Button
                    onClick={() => executeTask(option.model)}
                    disabled={isExecuting}
                    size="sm"
                    variant={index === 0 ? "default" : "outline"}
                    className={index === 0 ? "bg-primary hover:bg-primary/90" : ""}
                  >
                    {isExecuting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      "Run"
                    )}
                  </Button>
                </div>
              </div>
            ))}

            {/* Skip Button */}
            <div className="pt-2 border-t border-border">
              <Button
                onClick={() => {
                  onTaskComplete({
                    carbonImpact: 0,
                    carbonSaved: 0,
                    xpChange: -5,
                  });
                  toast({
                    title: "No model selected",
                    description: "-5 XP. Your EcoPet is getting tired!",
                    variant: "destructive",
                  });
                  setPrompt("");
                  setAnalysis(null);
                }}
                disabled={isExecuting}
                variant="ghost"
                size="sm"
                className="w-full text-muted-foreground hover:text-destructive"
              >
                Skip (lose 5 XP)
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Result Display */}
      {result && (
        <Card className="p-6 space-y-3 animate-grow">
          <h3 className="font-semibold text-primary flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Result
          </h3>
          <div className="text-sm text-foreground whitespace-pre-wrap bg-muted/50 p-4 rounded-lg">
            {result}
          </div>
        </Card>
      )}
    </div>
  );
};