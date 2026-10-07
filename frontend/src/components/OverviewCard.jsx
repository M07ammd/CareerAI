import { useState } from 'react';
import { ChevronRight, Target, Users } from 'lucide-react';

function ScoreRing({ score }) {
  const r = 48, stroke = 5;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 70 ? 'var(--green)' : score >= 45 ? 'var(--amber)' : 'var(--red)';
  return (
    <div className="score-ring-wrap">
      <svg width="120" height="120" viewBox="0 0 110 110" aria-hidden="true">
        <circle cx="55" cy="55" r={r} fill="none" stroke="var(--border)" strokeWidth={stroke} />
        <circle
          cx="55" cy="55" r={r} fill="none"
          stroke={color} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1s var(--ease)' }}
        />
      </svg>
      <div className="score-ring-number">
        <span className="tabular">{score}</span>
        <span className="score-ring-sub">/ 100</span>
      </div>
    </div>
  );
}

function fitLabel(score) {
  if (score >= 80) return { label: 'Strong fit', cls: 'chip-green' };
  if (score >= 60) return { label: 'Good fit',   cls: 'chip-green' };
  if (score >= 40) return { label: 'Partial fit', cls: 'chip-amber' };
  return { label: 'Weak fit', cls: 'chip-red' };
}

export default function OverviewCard({ result }) {
  const [showEvidence, setShowEvidence] = useState(false);
  const fr = result?.final_report;
  const sm = result?.skill_match;
  const ra = result?.resume_analysis;
  const ja = result?.job_analysis;

  const score = fr?.match_score ?? sm?.match_score ?? 0;
  const fit   = fitLabel(score);

  return (
    <section className="section-card" id="section-overview">
      <div className="section-header">
        <div className="section-title">
          <Target size={14} />
          Overview
        </div>
        <div className="score-chips">
          <span className={chip }>{fit.label}</span>
          {fr?.hiring_probability && (
            <span className={`chip chip-${fr.hiring_probability.toLowerCase() === 'high' ? 'green' : fr.hiring_probability.toLowerCase() === 'medium' ? 'amber' : 'red'}`}>
              {fr.hiring_probability} probability
            </span>
          )}
        </div>
      </div>
      <div className="section-body">
        <div className="score-summary">
          <ScoreRing score={score} />
          <div className="score-details">
            <p className="score-role">{ja?.job_title || 'Role'}</p>
            {ra?.candidate_name && <p className="score-person">{ra.candidate_name}</p>}
            {(fr?.score_interpretation || sm?.explanation) && (
              <p className="score-interpretation">
                {fr?.score_interpretation || sm?.explanation}
              </p>
            )}
            <div className="score-chips">
              {sm?.matched_skills?.length > 0 && (
                <span className="chip chip-green">{sm.matched_skills.length} matched</span>
              )}
              {sm?.missing_skills?.length > 0 && (
                <span className="chip chip-red">{sm.missing_skills.length} missing</span>
              )}
              {ja?.seniority_level && (
                <span className="chip chip-neutral">{ja.seniority_level}</span>
              )}
            </div>
          </div>
        </div>

        {sm?.evidence_grounded_justification?.length > 0 && (
          <div style={{marginTop:16}}>
            <button
              className="expand-toggle"
              onClick={() => setShowEvidence(v => !v)}
              aria-expanded={showEvidence}
              type="button"
            >
              <ChevronRight size={12} />
              How was this score calculated?
            </button>
            <div className={expand-content}>
              <div className="table-wrap">
                <table className="data-table">
                  <thead>
                    <tr><th>Evidence from your resume</th></tr>
                  </thead>
                  <tbody>
                    {sm.evidence_grounded_justification.map((ev, i) => (
                      <tr key={i}><td>{ev}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}