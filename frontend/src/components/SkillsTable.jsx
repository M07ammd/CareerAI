import { GitBranch } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

export default function SkillsTable({ skillMatch }) {
  if (!skillMatch) return null;
  const { matched_skills = [], missing_skills = [], partially_matched_skills = [] } = skillMatch;

  const rows = [
    ...matched_skills.map(s => ({ skill: s, status: 'matched', evidence: '' })),
    ...partially_matched_skills.map(s => ({ skill: s.skill, status: 'partial', evidence: s.notes || '' })),
    ...missing_skills.map(s => ({ skill: s, status: 'missing', evidence: '' })),
  ];

  return (
    <Card id="section-skills" className="mb-6 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <GitBranch className="h-5 w-5 text-muted-foreground" />
          Skills Match
        </CardTitle>
        <Badge variant="secondary">{rows.length} Total</Badge>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Skill</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Evidence / Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((r, i) => (
                <TableRow key={i}>
                  <TableCell className="font-medium">{r.skill}</TableCell>
                  <TableCell>
                    {r.status === 'matched' ? (
                      <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100/80">Matched</Badge>
                    ) : r.status === 'partial' ? (
                      <Badge variant="secondary" className="bg-amber-100 text-amber-800 hover:bg-amber-100/80">Partial</Badge>
                    ) : (
                      <Badge variant="destructive">Missing</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-muted-foreground">{r.evidence || '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}