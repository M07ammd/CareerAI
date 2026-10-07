/**
 * Skill matching card — shows matched, missing, and partial skills.
 */
export default function SkillsCard({ skillMatch }) {
  if (!skillMatch) return null;

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon purple">⚡</div>
        <div>
          <div className="card-title">Skill Analysis</div>
          <div className="card-subtitle">
            Match score: {skillMatch.match_score}/100
          </div>
        </div>
      </div>

      {/* Strengths */}
      {skillMatch.strengths?.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            STRENGTHS
          </p>
          <div className="skill-list">
            {skillMatch.strengths.map((s, i) => (
              <span key={i} className="skill-tag matched">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Matched skills */}
      {skillMatch.matched_skills?.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            ✓ MATCHED SKILLS ({skillMatch.matched_skills.length})
          </p>
          <div className="skill-list">
            {skillMatch.matched_skills.map((skill, i) => (
              <span key={i} className="skill-tag matched">{skill}</span>
            ))}
          </div>
        </div>
      )}

      {/* Partially matched */}
      {skillMatch.partially_matched_skills?.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            ≈ PARTIAL MATCHES ({skillMatch.partially_matched_skills.length})
          </p>
          <div className="skill-list">
            {skillMatch.partially_matched_skills.map((item, i) => (
              <span key={i} className="skill-tag partial" title={item.notes || ''}>
                {item.skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Missing skills */}
      {skillMatch.missing_skills?.length > 0 && (
        <div>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            ✗ MISSING SKILLS ({skillMatch.missing_skills.length})
          </p>
          <div className="skill-list">
            {skillMatch.missing_skills.map((skill, i) => (
              <span key={i} className="skill-tag missing">{skill}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
