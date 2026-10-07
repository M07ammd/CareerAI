import { Target } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';

function ScoreRing({ score }) {
  const r = 48, stroke = 5;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 70 ? '#10b981' : score >= 45 ? '#f59e0b' : '#ef4444';
  return (
    <div className="relative w-[120px] h-[120px] flex items-center justify-center shrink-0">
      <svg width="120" height="120" viewBox="0 0 110 110" className="-rotate-90">
        <circle cx="55" cy="55" r={r} fill="none" className="stroke-muted" strokeWidth={stroke} />
        <circle
          cx="55" cy="55" r={r} fill="none"
          stroke={color} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={offset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-3xl font-bold tracking-tighter tabular-nums">{score}</span>
        <span className="text-xs text-muted-foreground font-medium uppercase tracking-widest">Score</span>
      </div>
    </div>
  );
}

function fitLabel(score) {
  if (score >= 80) return { label: 'Strong Fit', variant: 'default', cls: 'bg-emerald-100 text-emerald-800 hover:bg-emerald-100/80' };
  if (score >= 60) return { label: 'Good Fit',   variant: 'default', cls: 'bg-emerald-100 text-emerald-800 hover:bg-emerald-100/80' };
  if (score >= 40) return { label: 'Partial Fit', variant: 'secondary', cls: 'bg-amber-100 text-amber-800 hover:bg-amber-100/80' };
  return { label: 'Weak Fit', variant: 'destructive', cls: '' };
}

export default function OverviewCard({ result }) {
  const fr = result?.final_report;
  const sm = result?.skill_match;
  const ra = result?.resume_analysis;
  const ja = result?.job_analysis;

  const score = fr?.match_score ?? sm?.match_score ?? 0;
  const fit   = fitLabel(score);

  return (
    <Card id="section-overview" className="mb-6 shadow-sm overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 bg-muted/30 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Target className="h-5 w-5 text-muted-foreground" />
          Overview
        </CardTitle>
        <div className="flex gap-2">
          <Badge className={fit.cls} variant={fit.variant}>{fit.label}</Badge>
          {fr?.hiring_probability && (
            <Badge variant="outline" className="capitalize">
              {fr.hiring_probability} Probability
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
          <ScoreRing score={score} />
          <div className="flex-1 space-y-4">
            <div>
              <h2 className="text-xl font-bold tracking-tight">{ja?.job_title || 'Target Role'}</h2>
              {ra?.candidate_name && <p className="text-muted-foreground">{ra.candidate_name}</p>}
            </div>
            {(fr?.score_interpretation || sm?.explanation) && (
              <p className="text-sm leading-relaxed text-muted-foreground">
                {fr?.score_interpretation || sm?.explanation}
              </p>
            )}
            <div className="flex flex-wrap gap-2 pt-2">
              {sm?.matched_skills?.length > 0 && (
                <Badge variant="secondary" className="bg-emerald-50 text-emerald-700 hover:bg-emerald-50/80 border-emerald-200">
                  {sm.matched_skills.length} Matched Skills
                </Badge>
              )}
              {sm?.missing_skills?.length > 0 && (
                <Badge variant="secondary" className="bg-red-50 text-red-700 hover:bg-red-50/80 border-red-200">
                  {sm.missing_skills.length} Missing Skills
                </Badge>
              )}
              {ja?.seniority_level && (
                <Badge variant="outline">{ja.seniority_level}</Badge>
              )}
            </div>
          </div>
        </div>
        
        {sm?.evidence_grounded_justification?.length > 0 && (
          <>
            <Separator className="my-6" />
            <div className="space-y-3">
              <h4 className="text-sm font-semibold tracking-tight">Evidence Grounded Justification</h4>
              <ul className="text-sm text-muted-foreground space-y-2 list-disc pl-4 marker:text-muted">
                {sm.evidence_grounded_justification.map((ev, i) => (
                  <li key={i} className="pl-1 leading-relaxed">{ev}</li>
                ))}
              </ul>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}