import { useState, useEffect, useRef } from 'react';
import { CheckCircle, Circle, Loader } from 'lucide-react';

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

  return (
    <div className="progress-panel" role="status" aria-live="polite" aria-label="Analysis in progress">
      <div className="progress-panel-header">
        <span className="progress-panel-title">Running analysis…</span>
        <span className="progress-elapsed">{fmt(elapsed)}</span>
      </div>
      <div className="progress-step-list">
        {STEPS.map((step, i) => {
          const isDone   = doneSteps.includes(i);
          const isActive = i === currentStep;
          return (
            <div key={step.key} className={progress-step}>
              <div className="progress-step-icon">
                {isDone   ? <CheckCircle size={14} /> :
                 isActive ? <div className="progress-spinner" /> :
                            <Circle size={14} />}
              </div>
              <span>{step.label}</span>
            </div>
          );
        })}
      </div>
      {onCancel && (
        <button className="btn btn-ghost btn-sm" onClick={onCancel} style={{marginTop:12}} type="button">
          Cancel
        </button>
      )}
    </div>
  );
}