/**
 * Career Roadmap card with a visual timeline.
 */
export default function RoadmapCard({ careerRoadmap }) {
  if (!careerRoadmap) return null;

  const phases = [
    {
      label: 'Immediate (0–2 weeks)',
      milestones: careerRoadmap.immediate_actions || [],
      cls: 'immediate',
      emoji: '⚡',
    },
    {
      label: 'Short-term (1–3 months)',
      milestones: careerRoadmap.short_term_goals || [],
      cls: 'short',
      emoji: '📈',
    },
    {
      label: 'Long-term (3–12 months)',
      milestones: careerRoadmap.long_term_goals || [],
      cls: 'long',
      emoji: '🎯',
    },
  ];

  return (
    <div className="card full-width">
      <div className="card-header">
        <div className="card-icon green">🗺️</div>
        <div>
          <div className="card-title">Career Roadmap</div>
          <div className="card-subtitle">
            {careerRoadmap.career_trajectory || 'Your personalised learning path'}
          </div>
        </div>
      </div>

      <div className="roadmap-timeline">
        {phases.map((phase, pi) => (
          phase.milestones.length > 0 && (
            <div key={pi}>
              <p style={{
                fontSize: 12,
                fontWeight: 700,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: 12,
                marginTop: pi > 0 ? 24 : 0,
              }}>
                {phase.emoji} {phase.label}
              </p>
              {phase.milestones.map((milestone, mi) => (
                <div key={mi} className="roadmap-phase">
                  <div className={`roadmap-phase-dot ${phase.cls}`}>
                    {mi + 1}
                  </div>
                  <div className="roadmap-phase-label">{milestone.timeframe}</div>
                  <div className="roadmap-milestone-title">{milestone.title}</div>
                  <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>
                    {milestone.description}
                  </p>
                  {milestone.action_items?.length > 0 && (
                    <ul className="roadmap-actions">
                      {milestone.action_items.slice(0, 4).map((action, ai) => (
                        <li key={ai}>{action}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )
        ))}
      </div>

      {/* Recommendations row */}
      {(careerRoadmap.recommended_projects?.length > 0 ||
        careerRoadmap.recommended_certifications?.length > 0) && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 16,
          marginTop: 24,
          paddingTop: 24,
          borderTop: '1px solid var(--border)',
        }}>
          {careerRoadmap.recommended_projects?.length > 0 && (
            <div>
              <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 10 }}>
                🏗️ Portfolio Projects
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {careerRoadmap.recommended_projects.map((p, i) => (
                  <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', paddingLeft: 16, position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0 }}>🔨</span>
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {careerRoadmap.recommended_certifications?.length > 0 && (
            <div>
              <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 10 }}>
                🎓 Certifications
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {careerRoadmap.recommended_certifications.map((c, i) => (
                  <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', paddingLeft: 16, position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0 }}>📜</span>
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
