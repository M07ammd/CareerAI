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
      </div>
    </div>
  );
}
