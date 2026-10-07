/**
 * Skill Gap Analysis card with prioritised gaps.
 */
export default function GapCard({ skillGaps }) {
  if (!skillGaps) return null;

  const allGaps = [
    ...skillGaps.high_priority_gaps?.map((g) => ({ ...g, priority: 'high' })) || [],
    ...skillGaps.medium_priority_gaps?.map((g) => ({ ...g, priority: 'medium' })) || [],
    ...skillGaps.low_priority_gaps?.map((g) => ({ ...g, priority: 'low' })) || [],
  ];

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon red">🔍</div>
        <div>
          <div className="card-title">Skill Gap Analysis</div>
          <div className="card-subtitle">{allGaps.length} gaps identified</div>
        </div>
      </div>

      {skillGaps.critical_blockers?.length > 0 && (
        <div style={{
          background: 'rgba(239,68,68,0.08)',
          border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: 'var(--radius)',
          padding: '12px 14px',
          marginBottom: 16,
        }}>
          <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--red)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            🚨 Critical Blockers
          </p>
          <div className="skill-list">
            {skillGaps.critical_blockers.map((s, i) => (
              <span key={i} className="skill-tag missing">{s}</span>
            ))}
          </div>
        </div>
      )}

      <div className="gap-list">
        {allGaps.slice(0, 8).map((gap, i) => (
          <div key={i} className={`gap-item ${gap.priority}`}>
            <div className="gap-item-header">
              <span className="gap-skill-name">{gap.skill}</span>
              <span className={`priority-badge ${gap.priority}`}>
                {gap.priority}
              </span>
            </div>
            <p className="gap-reason">{gap.reason}</p>
            {gap.estimated_learning_time && (
              <p style={{ fontSize: 11, color: 'var(--accent-primary)', marginTop: 4 }}>
                ⏱ {gap.estimated_learning_time}
              </p>
            )}
          </div>
        ))}
      </div>

      {allGaps.length > 8 && (
        <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-muted)', marginTop: 12 }}>
          +{allGaps.length - 8} more gaps in full report
        </p>
      )}
    </div>
  );
}
