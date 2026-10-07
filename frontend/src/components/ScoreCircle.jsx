import { useEffect, useRef, useState } from 'react';

/**
 * Animated circular score display.
 * @param {number} score - 0 to 100
 */
export default function ScoreCircle({ score }) {
  const [displayed, setDisplayed] = useState(0);
  const animRef = useRef(null);

  const getColor = (s) => {
    if (s >= 75) return '#10b981'; // green
    if (s >= 50) return '#f59e0b'; // yellow
    return '#ef4444';              // red
  };

  useEffect(() => {
    let start = null;
    const duration = 1200;
    const target = Math.min(100, Math.max(0, score || 0));

    const animate = (ts) => {
      if (!start) start = ts;
      const elapsed = ts - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setDisplayed(Math.round(eased * target));
      if (progress < 1) animRef.current = requestAnimationFrame(animate);
    };

    animRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animRef.current);
  }, [score]);

  const radius = 65;
  const circumference = 2 * Math.PI * radius;
  const fillFraction = (displayed / 100);
  const strokeDashoffset = circumference * (1 - fillFraction);
  const color = getColor(score);

  return (
    <div className="score-circle-wrap">
      <svg viewBox="0 0 160 160" width="160" height="160">
        <circle
          className="score-circle-bg"
          cx="80" cy="80" r={radius}
        />
        <circle
          className="score-circle-fill"
          cx="80" cy="80" r={radius}
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
        />
      </svg>
      <div className="score-circle-text">
        <span className="score-number" style={{ color }}>
          {displayed}
        </span>
        <span className="score-label">/ 100</span>
      </div>
    </div>
  );
}
