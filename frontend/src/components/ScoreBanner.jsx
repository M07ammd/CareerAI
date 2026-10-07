import ScoreCircle from './ScoreCircle';

function getProbabilityChip(probability) {
  const p = (probability || '').toLowerCase();
  if (p === 'high') return { cls: 'green', icon: '🟢', label: 'High Probability' };
  if (p === 'medium') return { cls: 'yellow', icon: '🟡', label: 'Medium Probability' };
  return { cls: 'red', icon: '🔴', label: 'Low Probability' };
}

/**
 * Top banner showing the match score, candidate info, and summary chips.
 */
export default function ScoreBanner({ result }) {
  const finalReport = result?.final_report;
  const skillMatch = result?.skill_match;
  const resumeAnalysis = result?.resume_analysis;
  const jobAnalysis = result?.job_analysis;

  const score = finalReport?.match_score ?? skillMatch?.match_score ?? 0;
  const probability = getProbabilityChip(finalReport?.hiring_probability);

  return (
    <div className="score-banner">
      <ScoreCircle score={score} />

      <div className="score-details">
        <h2 className="score-title">
          {resumeAnalysis?.candidate_name
            ? `${resumeAnalysis.candidate_name}'s Match Report`
            : 'Career Match Report'}
        </h2>

        <p className="score-interpretation">
          {finalReport?.score_interpretation ||
            skillMatch?.explanation ||
            'Analysis complete. See the detailed breakdown below.'}
        </p>

        <div className="score-meta">
          {/* Role */}
          <span className="meta-chip blue">
            🎯 {jobAnalysis?.job_title || 'Role'}
          </span>

          {/* Seniority */}
          {jobAnalysis?.seniority_level && (
            <span className="meta-chip purple">
              👤 {jobAnalysis.seniority_level}
            </span>
          )}

          {/* Hiring probability */}
          <span className={`meta-chip ${probability.cls}`}>
            {probability.icon} {probability.label}
          </span>

          {/* Matched skills count */}
          {skillMatch?.matched_skills?.length > 0 && (
            <span className="meta-chip green">
              ✓ {skillMatch.matched_skills.length} Skills Matched
            </span>
          )}

          {/* Missing skills count */}
          {skillMatch?.missing_skills?.length > 0 && (
            <span className="meta-chip red">
              ✗ {skillMatch.missing_skills.length} Skills Missing
            </span>
          )}
        </div>
        
        {/* Evidence Grounded Justification Panel */}
        {skillMatch?.evidence_grounded_justification?.length > 0 && (
          <div style={{
            marginTop: 16,
            padding: '12px 16px',
            background: 'var(--bg-secondary)',
            borderLeft: '4px solid var(--accent-primary)',
            borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
          }}>
            <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              🔎 Evidence-Grounded Justification
            </p>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {skillMatch.evidence_grounded_justification.map((ev, i) => (
                <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', paddingLeft: 16, position: 'relative' }}>
                  <span style={{ position: 'absolute', left: 0, color: 'var(--accent-primary)' }}>•</span>
                  {ev}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
