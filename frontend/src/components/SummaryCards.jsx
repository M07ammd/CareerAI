/**
 * Candidate Summary + Job Overview side-by-side cards.
 */
export default function SummaryCards({ resumeAnalysis, jobAnalysis }) {
  return (
    <>
      {/* Candidate Summary */}
      {resumeAnalysis && (
        <div className="card">
          <div className="card-header">
            <div className="card-icon purple">👤</div>
            <div>
              <div className="card-title">Candidate Profile</div>
              <div className="card-subtitle">
                {resumeAnalysis.total_experience_years != null
                  ? `${resumeAnalysis.total_experience_years} yrs experience`
                  : 'Experience details below'}
              </div>
            </div>
          </div>

          <p className="summary-text">{resumeAnalysis.summary}</p>

          {resumeAnalysis.education?.length > 0 && (
            <>
              <div style={{ height: 1, background: 'var(--border)', margin: '16px 0' }} />
              {resumeAnalysis.education.slice(0, 2).map((edu, i) => (
                <div key={i} className="info-row">
                  <span className="info-label">🎓 {edu.degree}</span>
                  <span className="info-value">{edu.institution}{edu.year ? `, ${edu.year}` : ''}</span>
                </div>
              ))}
            </>
          )}

          {resumeAnalysis.languages?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <p style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>
                Languages
              </p>
              <div className="skill-list">
                {resumeAnalysis.languages.map((lang, i) => (
                  <span key={i} className="skill-tag neutral">{lang}</span>
                ))}
              </div>
            </div>
          )}

          {resumeAnalysis.certifications?.length > 0 && (
            <div style={{ marginTop: 12 }}>
              <p style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>
                Certifications
              </p>
              <div className="skill-list">
                {resumeAnalysis.certifications.map((cert, i) => (
                  <span key={i} className="skill-tag neutral">{cert}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Job Requirements Summary */}
      {jobAnalysis && (
        <div className="card">
          <div className="card-header">
            <div className="card-icon blue">🎯</div>
            <div>
              <div className="card-title">Job Requirements</div>
              <div className="card-subtitle">{jobAnalysis.domain} · {jobAnalysis.seniority_level}</div>
            </div>
          </div>

          <div className="info-row">
            <span className="info-label">Role</span>
            <span className="info-value">{jobAnalysis.job_title}</span>
          </div>
          {jobAnalysis.company && (
            <div className="info-row">
              <span className="info-label">Company</span>
              <span className="info-value">{jobAnalysis.company}</span>
            </div>
          )}
          {jobAnalysis.required_experience_years != null && (
            <div className="info-row">
              <span className="info-label">Experience</span>
              <span className="info-value">{jobAnalysis.required_experience_years}+ years</span>
            </div>
          )}

          {jobAnalysis.key_qualifications?.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <p style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>
                Key Qualifications
              </p>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {jobAnalysis.key_qualifications.slice(0, 5).map((q, i) => (
                  <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', paddingLeft: 14, position: 'relative' }}>
                    <span style={{ position: 'absolute', left: 0, color: 'var(--accent-primary)' }}>›</span>
                    {q}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {jobAnalysis.technologies?.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <p style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>
                Technologies
              </p>
              <div className="skill-list">
                {jobAnalysis.technologies.slice(0, 12).map((tech, i) => (
                  <span key={i} className="skill-tag neutral">{tech}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
}
