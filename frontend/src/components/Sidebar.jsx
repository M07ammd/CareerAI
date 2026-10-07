import { useEffect, useState } from 'react';
import { Target, GitBranch, AlertTriangle, MessageSquare, Map, FileText } from 'lucide-react';

export default function Sidebar({ score }) {
  const [active, setActive] = useState('overview');

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      let current = '';
      entries.forEach(e => { if (e.isIntersecting) current = e.target.id; });
      if (current) setActive(current.replace('section-', ''));
    }, { rootMargin: '-20% 0px -80% 0px' });

    const sections = document.querySelectorAll('.section-card');
    sections.forEach(s => observer.observe(s));
    return () => sections.forEach(s => observer.unobserve(s));
  }, []);

  const links = [
    { id: 'overview',  icon: <Target size={14} />,        label: 'Overview' },
    { id: 'skills',    icon: <GitBranch size={14} />,     label: 'Skills' },
    { id: 'gaps',      icon: <AlertTriangle size={14} />, label: 'Skill Gaps' },
    { id: 'interview', icon: <MessageSquare size={14} />, label: 'Interview' },
    { id: 'roadmap',   icon: <Map size={14} />,           label: 'Roadmap' },
    { id: 'cv',        icon: <FileText size={14} />,      label: 'CV Updates' },
    { id: 'report',    icon: <FileText size={14} />,      label: 'Report' },
  ];

  return (
    <aside className="results-sidebar">
      <div className="sidebar-score-block">
        <span className="sidebar-score-label">Match Score</span>
        <span className="sidebar-score-value">{score}</span>
        <div className="sidebar-score-bar">
          <div className="sidebar-score-fill" style={{ width: `${score}%` }} />
        </div>
      </div>
      <nav style={{display:'flex',flexDirection:'column',gap:2,marginTop:12}}>
        {links.map(l => (
          <a
            key={l.id}
            href={`#section-${l.id}`}
            className={`sidebar-nav-item${active === l.id ? ' active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              const el = document.getElementById(`section-${l.id}`);
              if (el) {
                const y = el.getBoundingClientRect().top + window.scrollY - 80;
                window.scrollTo({ top: y, behavior: 'smooth' });
              }
            }}
          >
            {l.icon}
            <span>{l.label}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}