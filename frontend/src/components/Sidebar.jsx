import { useEffect, useState } from 'react';
import { Target, GitBranch, AlertTriangle, MessageSquare, Map, FileText } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';

export default function Sidebar({ score }) {
  const [active, setActive] = useState('overview');

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      let current = '';
      entries.forEach(e => { if (e.isIntersecting) current = e.target.id; });
      if (current) setActive(current.replace('section-', ''));
    }, { rootMargin: '-20% 0px -80% 0px' });

    const sections = document.querySelectorAll('[id^="section-"]');
    sections.forEach(s => observer.observe(s));
    return () => sections.forEach(s => observer.unobserve(s));
  }, []);

  const links = [
    { id: 'overview',  icon: <Target className="h-4 w-4" />,        label: 'Overview' },
    { id: 'skills',    icon: <GitBranch className="h-4 w-4" />,     label: 'Skills Match' },
    { id: 'gaps',      icon: <AlertTriangle className="h-4 w-4" />, label: 'Skill Gaps' },
    { id: 'interview', icon: <MessageSquare className="h-4 w-4" />, label: 'Interview Prep' },
    { id: 'roadmap',   icon: <Map className="h-4 w-4" />,           label: 'Roadmap' },
    { id: 'cv',        icon: <FileText className="h-4 w-4" />,      label: 'CV Updates' },
    { id: 'report',    icon: <FileText className="h-4 w-4" />,      label: 'Report' },
  ];

  return (
    <aside className="w-full md:w-64 shrink-0 md:sticky md:top-24 h-fit pb-8">
      <div className="p-4 border rounded-lg bg-card shadow-sm mb-6">
        <div className="flex justify-between items-end mb-2">
          <span className="text-sm font-medium text-muted-foreground">Match Score</span>
          <span className="text-2xl font-bold tracking-tight">{score}</span>
        </div>
        <div className="h-2 w-full bg-secondary overflow-hidden rounded-full">
          <div className="h-full bg-primary transition-all duration-1000 ease-out" style={{ width: `${score}%` }} />
        </div>
      </div>
      <nav className="space-y-1">
        {links.map(l => (
          <a
            key={l.id}
            href={`#section-${l.id}`}
            className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors ${active === l.id ? 'bg-secondary text-secondary-foreground' : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground'}`}
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
            {l.label}
          </a>
        ))}
      </nav>
    </aside>
  );
}