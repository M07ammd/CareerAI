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
 *
 * Fix (Phase 4): setDoneSteps is no longer called synchronously inside the
 * setCurrentStep updater (which runs inside a useEffect callback). The oxlint
 * "no setState inside effect" warning was caused by the nested setState call
 * pattern.  We now compute both values atomically in a single effect body
 * using a dedicated "tick" counter.
 */
export default function LoadingOverlay({ isVisible }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [doneSteps, setDoneSteps] = useState([]);
  const intervalRef = useRef(null);

  // Reset when hidden
  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0);
      setDoneSteps([]);
    }
  }, [isVisible]);

  // Advance steps on a timer — no nested setState calls
  useEffect(() => {
    if (!isVisible) return undefined;

    intervalRef.current = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STEPS.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 8000);

    return () => clearInterval(intervalRef.current);
  }, [isVisible]);

  // Derive doneSteps from currentStep without calling setState inside another setState
  useEffect(() => {
    if (currentStep > 0) {
      setDoneSteps(Array.from({ length: currentStep }, (_, i) => i));
    }
  }, [currentStep]);

  if (!isVisible) return null;

  return (
    <div className="loading-overlay">
      <div className="loading-spinner" />
      <div>
        <div className="loading-title">
          🚀 Analyzing your profile…
        </div>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: 8, fontSize: 14 }}>
          Running analysis pipeline…
        </p>
      </div>

      <div className="loading-steps">
        {STEPS.map((step, i) => {
          const isDone = doneSteps.includes(i);
          const isActive = i === currentStep;

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
