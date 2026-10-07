import { useEffect, useRef, useState } from 'react';

const STEPS = [
  { key: 'resume', label: '📄 Parsing your resume' },
  { key: 'job', label: '🎯 Analyzing job requirements' },
  { key: 'skills', label: '⚡ Matching your skills' },
  { key: 'gaps', label: '🔍 Identifying skill gaps' },
  { key: 'interview', label: '🎤 Generating interview questions' },
  { key: 'roadmap', label: '🗺️ Building career roadmap' },
  { key: 'report', label: '📊 Generating final report' },
];

/**
 * Animated loading overlay shown while the analysis pipeline runs.
 */
export default function LoadingOverlay({ isVisible }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [doneSteps, setDoneSteps] = useState([]);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0);
      setDoneSteps([]);
      return;
    }

    // Advance steps at a rate matching typical agent runtime (~10s per step)
    intervalRef.current = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STEPS.length - 1) {
          setDoneSteps((d) => [...d, prev]);
          return prev + 1;
        }
        return prev;
      });
    }, 8000);

    return () => clearInterval(intervalRef.current);
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div className="loading-overlay">
      <div className="loading-spinner" />
      <div>
        <div className="loading-title">
          🚀 Analyzing your profile…
        </div>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: 8, fontSize: 14 }}>
          Our AI agents are working in parallel
        </p>
      </div>

      <div className="loading-steps">
        {STEPS.map((step, i) => {
          const isDone = doneSteps.includes(i);
          const isActive = i === currentStep;
          const isPending = !isDone && !isActive;

          return (
            <div
              key={step.key}
              className={`loading-step ${isDone ? 'done' : isActive ? 'active' : 'pending'}`}
            >
              <div className="step-dot" />
              <span>
                {isDone ? '✓ ' : ''}{step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
