import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';

/**
 * Final report card with expandable Markdown content.
 * Uses react-markdown + rehype-sanitize to safely render LLM-generated markdown
 * without dangerouslySetInnerHTML (XSS prevention).
 */
export default function ReportCard({ finalReport }) {
  const [expanded, setExpanded] = useState(false);

  if (!finalReport) return null;

  return (
    <div className="card full-width">
      <div className="card-header">
        <div className="card-icon purple">📊</div>
        <div>
          <div className="card-title">Final Career Report</div>
          <div className="card-subtitle">
            Comprehensive analysis — {finalReport.hiring_probability} fit
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div style={{
        padding: '16px 20px',
        background: 'rgba(99,102,241,0.05)',
        borderRadius: 'var(--radius)',
        border: '1px solid rgba(99,102,241,0.15)',
        marginBottom: 20,
      }}>
        <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent-primary)', marginBottom: 8 }}>
          📋 EXECUTIVE SUMMARY
        </p>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          {finalReport.executive_summary}
        </p>
      </div>

      {/* Key columns */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        {finalReport.key_strengths?.length > 0 && (
          <div>
            <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--green)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              ✅ Key Strengths
            </p>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {finalReport.key_strengths.map((s, i) => (
                <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', paddingLeft: 16, position: 'relative' }}>
                  <span style={{ position: 'absolute', left: 0, color: 'var(--green)' }}>✓</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {finalReport.critical_gaps?.length > 0 && (
          <div>
            <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--red)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              ⚠️ Critical Gaps
            </p>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {finalReport.critical_gaps.map((g, i) => (
                <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', paddingLeft: 16, position: 'relative' }}>
                  <span style={{ position: 'absolute', left: 0, color: 'var(--red)' }}>✗</span>
                  {g}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Top Recommendations */}
      {finalReport.top_recommendations?.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            🎯 Top Recommendations
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {finalReport.top_recommendations.map((rec, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 12,
                padding: '10px 14px',
                background: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-sm)',
              }}>
                <span style={{
                  flexShrink: 0,
                  width: 24,
                  height: 24,
                  background: 'var(--accent-gradient)',
                  borderRadius: '50%',
                  display: 'grid',
                  placeItems: 'center',
                  fontSize: 12,
                  fontWeight: 700,
                }}>
                  {i + 1}
                </span>
                <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CV Bullet Rewrites */}
      {finalReport.cv_bullet_rewrites?.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            ✨ CV Bullet Rewrite Suggestions
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {finalReport.cv_bullet_rewrites.map((rewrite, i) => (
              <div key={i} style={{
                background: 'var(--bg-secondary)',
                border: '1px solid rgba(99,102,241,0.2)',
                borderRadius: 'var(--radius-sm)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}>
                <div>
                  <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--red)', textTransform: 'uppercase', marginRight: 8 }}>Original</span>
                  <span style={{ fontSize: 14, color: 'var(--text-secondary)' }}>{rewrite.original_bullet}</span>
                </div>
                <div>
                  <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--green)', textTransform: 'uppercase', marginRight: 8 }}>Suggested</span>
                  <span style={{ fontSize: 14, color: 'var(--text-primary)', fontWeight: 500 }}>{rewrite.suggested_bullet}</span>
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4, fontStyle: 'italic' }}>
                  💡 {rewrite.reasoning}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full Report Toggle — safe markdown via react-markdown + rehype-sanitize */}
      {finalReport.full_report_markdown && (
        <>
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              width: '100%',
              padding: '12px',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              color: 'var(--text-secondary)',
              fontSize: 14,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              marginBottom: expanded ? 20 : 0,
              transition: 'all var(--transition)',
            }}
          >
            <span>{expanded ? '▲' : '▼'}</span>
            {expanded ? 'Collapse Full Report' : 'View Full Markdown Report'}
          </button>

          {expanded && (
            <div style={{
              padding: 24,
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
              className="report-markdown"
            >
              {/* rehypeSanitize strips any injected HTML from LLM output */}
              <ReactMarkdown rehypePlugins={[rehypeSanitize]}>
                {finalReport.full_report_markdown}
              </ReactMarkdown>
            </div>
          )}
        </>
      )}
    </div>
  );
}
