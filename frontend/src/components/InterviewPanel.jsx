import { MessageSquare } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Separator } from './ui/separator';

const CATEGORIES = [
  { key: 'technical_questions',  label: 'Technical' },
  { key: 'project_questions',    label: 'Project' },
  { key: 'behavioral_questions', label: 'Behavioral' },
  { key: 'hr_questions',         label: 'HR' },
];

export default function InterviewPanel({ interviewQuestions }) {
  if (!interviewQuestions) return null;

  return (
    <Card id="section-interview" className="mb-6 shadow-sm">
      <CardHeader className="flex flex-row items-center space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-muted-foreground" />
          Interview Preparation
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs defaultValue="technical_questions" className="w-full">
          <div className="px-6 border-b">
            <TabsList className="bg-transparent h-12 w-full justify-start overflow-x-auto rounded-none p-0">
              {CATEGORIES.map(c => {
                const count = interviewQuestions[c.key]?.length || 0;
                return (
                  <TabsTrigger 
                    key={c.key} 
                    value={c.key} 
                    className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:shadow-none rounded-none h-12 px-4"
                  >
                    {c.label}
                    {count > 0 && <span className="ml-2 text-muted-foreground tabular-nums text-xs bg-muted px-1.5 py-0.5 rounded-full">{count}</span>}
                  </TabsTrigger>
                );
              })}
            </TabsList>
          </div>
          
          {CATEGORIES.map(c => (
            <TabsContent key={c.key} value={c.key} className="p-6 m-0 focus-visible:outline-none focus-visible:ring-0">
              <div className="space-y-6">
                {(interviewQuestions[c.key] || []).length === 0 ? (
                  <p className="text-sm text-muted-foreground">No questions in this category.</p>
                ) : (
                  interviewQuestions[c.key].map((q, i) => (
                    <div key={i} className="space-y-3">
                      <p className="font-medium text-sm leading-relaxed">{q.question}</p>
                      {q.rationale && <p className="text-sm text-muted-foreground leading-relaxed bg-muted/50 p-3 rounded-md border">{q.rationale}</p>}
                      {q.suggested_answer_points?.length > 0 && (
                        <ul className="text-sm text-muted-foreground list-disc pl-5 space-y-1 marker:text-muted">
                          {q.suggested_answer_points.map((pt, j) => <li key={j} className="pl-1 leading-relaxed">{pt}</li>)}
                        </ul>
                      )}
                      {i < interviewQuestions[c.key].length - 1 && <Separator className="mt-6" />}
                    </div>
                  ))
                )}
              </div>
            </TabsContent>
          ))}
        </Tabs>
        
        {interviewQuestions.preparation_tips?.length > 0 && (
          <div className="p-6 bg-muted/30 border-t">
            <h4 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">Preparation Tips</h4>
            <ul className="text-sm text-muted-foreground space-y-2 list-disc pl-4 marker:text-muted">
              {interviewQuestions.preparation_tips.map((tip, i) => <li key={i} className="pl-1 leading-relaxed">{tip}</li>)}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}