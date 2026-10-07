import { useState, useEffect, useRef } from 'react';
import { CheckCircle, Circle } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Progress } from './ui/progress';
import { Button } from './ui/button';

const STEPS = [
  { key: 'resume',    label: 'Parsing resume' },
  { key: 'job',       label: 'Analyzing job requirements' },
  { key: 'skills',    label: 'Matching skills' },
  { key: 'gaps',      label: 'Identifying skill gaps' },
  { key: 'interview', label: 'Generating interview questions' },
  { key: 'roadmap',   label: 'Building career roadmap' },
  { key: 'report',    label: 'Compiling final report' },
];

export default function ProgressPanel({ isVisible, onCancel }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [doneSteps, setDoneSteps]     = useState([]);
  const [elapsed, setElapsed]         = useState(0);
  const intervalRef = useRef(null);
  const timerRef    = useRef(null);

  useEffect(() => {
    if (!isVisible) { setCurrentStep(0); setDoneSteps([]); setElapsed(0); return; }
    intervalRef.current = setInterval(() => {
      setCurrentStep(p => (p < STEPS.length - 1 ? p + 1 : p));
    }, 7500);
    timerRef.current = setInterval(() => setElapsed(s => s + 1), 1000);
    return () => { clearInterval(intervalRef.current); clearInterval(timerRef.current); };
  }, [isVisible]);

  useEffect(() => {
    if (currentStep > 0) setDoneSteps(Array.from({ length: currentStep }, (_, i) => i));
  }, [currentStep]);

  if (!isVisible) return null;

  const fmt = s => `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;
  const progress = Math.min(((currentStep + 0.5) / STEPS.length) * 100, 100);

  return (
    <Card className="shadow-lg border-primary/20 bg-card overflow-hidden">
      <div className="h-1 w-full bg-muted">
        <div className="h-full bg-primary transition-all duration-1000" style={{ width: `${progress}%` }} />
      </div>
      <CardContent className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            <span className="font-semibold tracking-tight">Running Analysis…</span>
          </div>
          <span className="text-sm font-medium text-muted-foreground font-mono bg-muted px-2 py-1 rounded">{fmt(elapsed)}</span>
        </div>
        
        <div className="space-y-4 mb-6">
          {STEPS.map((step, i) => {
            const isDone   = doneSteps.includes(i);
            const isActive = i === currentStep;
            return (
              <div key={step.key} className={`flex items-center gap-3 text-sm transition-colors duration-500 ${isDone ? 'text-foreground font-medium' : isActive ? 'text-primary font-semibold' : 'text-muted-foreground'}`}>
                {isDone ? (
                  <CheckCircle className="h-4 w-4 text-primary" />
                ) : isActive ? (
                  <div className="h-4 w-4 rounded-full border-2 border-primary border-t-transparent animate-spin shrink-0" />
                ) : (
                  <Circle className="h-4 w-4 opacity-30" />
                )}
                <span>{step.label}</span>
              </div>
            );
          })}
        </div>
        
        {onCancel && (
          <Button variant="outline" size="sm" onClick={onCancel} className="w-full">
            Cancel Analysis
          </Button>
        )}
      </CardContent>
    </Card>
  );
}