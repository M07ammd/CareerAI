import { AlertTriangle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

export default function GapsTable({ skillGaps }) {
  if (!skillGaps) return null;
  const all = [
    ...(skillGaps.high_priority_gaps   || []).map(g => ({ ...g, priority: 'High' })),
    ...(skillGaps.medium_priority_gaps || []).map(g => ({ ...g, priority: 'Medium' })),
    ...(skillGaps.low_priority_gaps    || []).map(g => ({ ...g, priority: 'Low' })),
  ];

  return (
    <Card id="section-gaps" className="mb-6 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-muted-foreground" />
          Skill Gaps
        </CardTitle>
        {skillGaps.critical_blockers?.length > 0 && (
          <Badge variant="destructive">{skillGaps.critical_blockers.length} Blockers</Badge>
        )}
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Skill</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Why it matters</TableHead>
                <TableHead>Est. time</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {all.map((g, i) => (
                <TableRow key={i}>
                  <TableCell className="font-medium">{g.skill}</TableCell>
                  <TableCell>
                    <Badge variant={g.priority === 'High' ? 'destructive' : g.priority === 'Medium' ? 'secondary' : 'outline'}>
                      {g.priority}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{g.reason}</TableCell>
                  <TableCell className="text-muted-foreground">{g.estimated_learning_time || '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        {skillGaps.overall_gap_summary && (
          <p className="mt-4 text-sm text-muted-foreground leading-relaxed">
            {skillGaps.overall_gap_summary}
          </p>
        )}
      </CardContent>
    </Card>
  );
}