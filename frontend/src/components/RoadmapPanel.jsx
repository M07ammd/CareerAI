import { Map } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Separator } from './ui/separator';

export default function RoadmapPanel({ careerRoadmap }) {
  if (!careerRoadmap) return null;
  const { phases = [] } = careerRoadmap;

  return (
    <Card id="section-roadmap" className="mb-6 shadow-sm">
      <CardHeader className="flex flex-row items-center space-y-0 pb-6 border-b">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Map className="h-5 w-5 text-muted-foreground" />
          Career Roadmap
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {phases.length === 0 ? (
          <div className="p-6 text-sm text-muted-foreground">No roadmap phases available.</div>
        ) : (
          <div className="divide-y divide-border">
            {phases.map((phase, i) => (
              <div key={i} className="p-6 flex flex-col md:flex-row gap-4 md:gap-8 hover:bg-muted/30 transition-colors">
                <div className="md:w-32 shrink-0">
                  <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-1">Phase {i + 1}</div>
                  <div className="text-sm font-medium">{phase.timeframe || '—'}</div>
                </div>
                <div className="flex-1 space-y-3">
                  <h4 className="text-base font-semibold">{phase.focus_area}</h4>
                  {phase.objectives?.length > 0 && (
                    <ul className="text-sm text-muted-foreground space-y-2 list-disc pl-4 marker:text-muted">
                      {phase.objectives.map((obj, j) => <li key={j} className="pl-1 leading-relaxed">{obj}</li>)}
                    </ul>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}