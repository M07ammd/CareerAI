import { GitBranch } from 'lucide-react';

export default function SkillsTable({ skillMatch }) {
  if (!skillMatch) return null;
  const { matched_skills = [], missing_skills = [], partially_matched_skills = [] } = skillMatch;

  const rows = [
    ...matched_skills.map(s => ({ skill: s, status: 'matched', evidence: '' })),
    ...partially_matched_skills.map(s => ({ skill: s.skill, status: 'partial', evidence: s.notes || '' })),
    ...missing_skills.map(s => ({ skill: s, status: 'missing', evidence: '' })),
  ];

  const statusTag = (s) => {
    if (s === 'matched') return <span className="tag tag-green">Matched</span>;
    if (s === 'partial')  return <span className="tag tag-amber">Partial</span>;
    return <span className="tag tag-red">Missing</span>;
  };

  return (
    <section className="section-card" id="section-skills">
      <div className="section-header">
        <div className="section-title">
          <GitBranch size={14} />
          Skills
        </div>
        <span className="chip chip-neutral tabular">{rows.length} total</span>
      </div>
      <div className="section-body-flush">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Status</th>
                <th>Evidence / Notes</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i}>
                  <td style={{fontWeight:500}}>{r.skill}</td>
                  <td>{statusTag(r.status)}</td>
                  <td className="td-muted">{r.evidence || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}