import { AlertTriangle } from 'lucide-react';

export default function GapsTable({ skillGaps }) {
  if (!skillGaps) return null;
  const all = [
    ...(skillGaps.high_priority_gaps   || []).map(g => ({ ...g, priority: 'high' })),
    ...(skillGaps.medium_priority_gaps || []).map(g => ({ ...g, priority: 'medium' })),
    ...(skillGaps.low_priority_gaps    || []).map(g => ({ ...g, priority: 'low' })),
  ];

  return (
    <section className="section-card" id="section-gaps">
      <div className="section-header">
        <div className="section-title">
          <AlertTriangle size={14} />
          Skill Gaps
        </div>
        {skillGaps.critical_blockers?.length > 0 && (
          <span className="chip chip-red">{skillGaps.critical_blockers.length} blockers</span>
        )}
      </div>
      <div className="section-body-flush">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Priority</th>
                <th>Why it matters</th>
                <th>Est. time</th>
              </tr>
            </thead>
            <tbody>
              {all.map((g, i) => (
                <tr key={i}>
                  <td style={{fontWeight:500}}>{g.skill}</td>
                  <td>
                    <span className={`priority priority-${g.priority}`}>{g.priority}</span>
                  </td>
                  <td className="td-muted">{g.reason}</td>
                  <td className="td-muted">{g.estimated_learning_time || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {skillGaps.overall_gap_summary && (
        <div className="section-body" style={{borderTop:'1px solid var(--border)'}}>
          <p style={{fontSize:13,color:'var(--text-2)',lineHeight:1.6}}>{skillGaps.overall_gap_summary}</p>
        </div>
      )}
    </section>
  );
}