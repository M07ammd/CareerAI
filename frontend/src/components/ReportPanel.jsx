import { FileText, Copy, Download } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
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
    <div className="space-y-6">
      {cvRewrites?.rewritten_bullets?.length > 0 && (
        <Card id="section-cv" className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <FileText className="h-5 w-5 text-muted-foreground" />
              CV Improvements
            </CardTitle>
            <Badge variant="secondary">{cvRewrites.rewritten_bullets.length} Suggestions</Badge>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border">
              {cvRewrites.rewritten_bullets.map((rw, i) => (
                <div key={i} className="p-6 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Original</div>
                      <div className="text-sm p-3 bg-destructive/5 text-destructive-foreground/80 rounded border border-destructive/10 line-through decoration-destructive/30 leading-relaxed">
                        {rw.original_text}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="text-xs font-semibold uppercase tracking-widest text-emerald-600">Suggested Rewrite</div>
                      <div className="text-sm p-3 bg-emerald-50 text-emerald-900 rounded border border-emerald-100 font-medium leading-relaxed">
                        {rw.suggested_rewrite}
                      </div>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <strong className="text-foreground">Why:</strong> {rw.reasoning}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {finalReport?.executive_summary && (
        <Card id="section-report" className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b bg-muted/30">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <FileText className="h-5 w-5 text-muted-foreground" />
              Executive Summary
            </CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleCopy}>
                <Copy className="h-3.5 w-3.5 mr-1.5" /> Copy
              </Button>
              <Button size="sm" onClick={handleDownload}>
                <Download className="h-3.5 w-3.5 mr-1.5" /> Download
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap leading-loose text-muted-foreground font-medium">
              {finalReport.executive_summary}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}