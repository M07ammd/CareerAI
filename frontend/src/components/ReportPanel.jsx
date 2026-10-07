import { FileText, Copy, Download } from 'lucide-react';
import { useToast } from '../hooks/useToast';

export default function ReportPanel({ finalReport, cvRewrites }) {
  const { push } = useToast();

  const handleCopy = () => {
    if (!finalReport?.executive_summary) return;
    navigator.clipboard.writeText(finalReport.executive_summary)
      .then(() => push('Report copied to clipboard', 'success'))
      .catch(() => push('Failed to copy', 'error'));
  };

  const handleDownload = () => {
    if (!finalReport?.executive_summary) return;
    const blob = new Blob([finalReport.executive_summary], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'careerpilot-report.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    push('Download started', 'success');
  };

  return (
    <div style={{display:'flex',flexDirection:'column',gap:24}}>
      {cvRewrites?.rewritten_bullets?.length > 0 && (
        <section className="section-card" id="section-cv">
          <div className="section-header">
            <div className="section-title"><FileText size={14} /> CV Improvements</div>
            <span className="chip chip-neutral">{cvRewrites.rewritten_bullets.length} suggestions</span>
          </div>
          <div className="section-body" style={{display:'flex',flexDirection:'column',gap:16}}>
            {cvRewrites.rewritten_bullets.map((rw, i) => (
              <div key={i} className="rewrite-item">
                <div className="rewrite-original">
                  <div className="rewrite-label">Original</div>
                  <div className="rewrite-text">{rw.original_text}</div>
                </div>
                <div className="rewrite-suggested">
                  <div className="rewrite-label">Suggested</div>
                  <div className="rewrite-text">{rw.suggested_rewrite}</div>
                </div>
                <div className="rewrite-reasoning">
                  <strong>Why:</strong> {rw.reasoning}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {finalReport?.executive_summary && (
        <section className="section-card" id="section-report">
          <div className="section-header">
            <div className="section-title"><FileText size={14} /> Executive Summary</div>
            <div style={{display:'flex',gap:8}}>
              <button className="btn btn-outline btn-sm" onClick={handleCopy} type="button">
                <Copy size={12} /> Copy
              </button>
              <button className="btn btn-primary btn-sm" onClick={handleDownload} type="button">
                <Download size={12} /> Download
              </button>
            </div>
          </div>
          <div className="section-body">
            <div className="report-markdown" style={{whiteSpace:'pre-wrap'}}>
              {finalReport.executive_summary}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}