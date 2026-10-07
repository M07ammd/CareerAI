import { Map } from 'lucide-react';

export default function RoadmapPanel({ careerRoadmap }) {
  if (!careerRoadmap) return null;
  const { phases = [] } = careerRoadmap;

  return (
    <section className="section-card" id="section-roadmap">
      <div className="section-header">
        <div className="section-title">
          <Map size={14} />
          Career Roadmap
        </div>
      </div>
      <div className="section-body-flush">
        {phases.length === 0 ? (
          <div style={{padding:20,color:'var(--text-3)'}}>No roadmap phases available.</div>
        ) : (
          phases.map((phase, i) => (
            <div key={i}>
              <div className="roadmap-section-title">Phase {i + 1}</div>
              <div className="roadmap-item">
                <div className="roadmap-timeframe">{phase.timeframe || '—'}</div>
                <div className="roadmap-item-body">
                  <div className="roadmap-item-title">{phase.focus_area}</div>
                  {phase.objectives?.length > 0 && (
                    <ul className="roadmap-bullets">
                      {phase.objectives.map((obj, j) => <li key={j}>{obj}</li>)}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}