import { useState, useEffect } from 'react';
import { Layers, Moon, Sun, AlertTriangle } from 'lucide-react';
import { analyzeCareer } from './api';
import { useFileUpload } from './hooks/useFileUpload';
import { FileDropzone } from './components/FileDropzone';
import ProgressPanel from './components/ProgressPanel';
import Toast from './components/Toast';
import { useToast } from './hooks/useToast';
import Sidebar from './components/Sidebar';
import OverviewCard from './components/OverviewCard';
import SkillsTable from './components/SkillsTable';
import GapsTable from './components/GapsTable';
import InterviewPanel from './components/InterviewPanel';
import RoadmapPanel from './components/RoadmapPanel';
import ReportPanel from './components/ReportPanel';
import { Button } from './components/ui/button';
import { Alert, AlertTitle, AlertDescription } from './components/ui/alert';
import { Textarea } from './components/ui/textarea';
import { Label } from './components/ui/label';

const SAMPLE_JD = `Senior Software Engineer (Frontend)
We are looking for a Senior Frontend Engineer with deep React experience.
Requirements:
- 5+ years of frontend experience
- Strong React, TypeScript, and state management
- CSS architecture (CSS modules, Tailwind)
- Performance optimization and Web Vitals
- Experience with Next.js or Vite
Responsibilities:
- Architect and build scalable UI systems
- Mentor junior engineers`;

export default function App() {
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [theme, setTheme] = useState('light');
  
  const { toasts, push } = useToast();
  const fileUpload = useFileUpload();

  useEffect(() => {
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const saved = localStorage.getItem('careerpilot-theme');
    const t = saved || (isDark ? 'dark' : 'light');
    setTheme(t);
    document.documentElement.classList.toggle('dark', t === 'dark');
  }, []);

  const toggleTheme = () => {
    const t = theme === 'light' ? 'dark' : 'light';
    setTheme(t);
    localStorage.setItem('careerpilot-theme', t);
    document.documentElement.classList.toggle('dark', t === 'dark');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fileUpload.file) { setError('Please upload your CV PDF.'); return; }
    if (jobDescription.trim().length < 50) {
      setError('Please paste a job description (at least 50 characters).'); return;
    }
    setError('');
    setResult(null);
    setIsLoading(true);

    try {
      const data = await analyzeCareer(fileUpload.file, jobDescription);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Analysis failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError('');
    fileUpload.clear();
    setJobDescription('');
  };

  const score = result?.final_report?.match_score ?? result?.skill_match?.match_score ?? 0;

  return (
    <div className="min-h-screen bg-background font-sans antialiased text-foreground selection:bg-primary/20">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 md:px-8 h-14 flex items-center justify-between">
          <a className="flex items-center gap-2 font-bold tracking-tight text-lg hover:text-primary transition-colors" href="/">
            <div className="bg-primary text-primary-foreground p-1 rounded-md"><Layers className="h-4 w-4" /></div>
            <span>CareerPilot</span>
          </a>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
              {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 md:px-8 py-8 md:py-12 max-w-6xl">
        {!result && !isLoading && (
          <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
            <div className="space-y-3 text-center">
              <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">Career Analysis</h1>
              <p className="text-muted-foreground text-lg">Compare your resume against a target role to find skill gaps and get a tailored learning roadmap.</p>
            </div>
            
            {error && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-8 bg-card border rounded-xl p-6 md:p-8 shadow-sm">
              <FileDropzone {...fileUpload} />
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <Label htmlFor="jd-input">Job Description</Label>
                  <Button type="button" variant="ghost" size="sm" className="h-7 text-xs font-medium" onClick={() => setJobDescription(SAMPLE_JD)}>
                    Load Sample
                  </Button>
                </div>
                <Textarea 
                  id="jd-input" 
                  className="min-h-[200px] resize-y font-mono text-sm shadow-sm focus-visible:ring-primary/50" 
                  placeholder="Paste the job description here…" 
                  value={jobDescription} 
                  onChange={(e) => setJobDescription(e.target.value)} 
                />
                <div className={`text-xs font-medium text-right ${jobDescription.length > 0 && jobDescription.length < 50 ? 'text-destructive' : 'text-muted-foreground'}`}>
                  {jobDescription.length} / 50 characters min
                </div>
              </div>
              
              <Button type="submit" size="lg" className="w-full text-base font-semibold shadow-sm" disabled={!fileUpload.file || jobDescription.length < 50}>
                Analyze Profile
              </Button>
            </form>
          </div>
        )}

        {isLoading && (
          <div className="max-w-xl mx-auto mt-12 animate-in fade-in duration-500">
            <ProgressPanel isVisible={true} onCancel={() => setIsLoading(false)} />
          </div>
        )}

        {result && !isLoading && (
          <div className="flex flex-col md:flex-row gap-8 items-start animate-in fade-in slide-in-from-bottom-8 duration-700 ease-out">
            <Sidebar score={score} />
            <div className="flex-1 w-full max-w-4xl min-w-0 space-y-6">
              <div className="flex justify-between items-end mb-8">
                <div>
                  <h1 className="text-3xl font-extrabold tracking-tight">Analysis Results</h1>
                  <p className="text-muted-foreground mt-1">Based on the uploaded resume and job description.</p>
                </div>
                <Button variant="outline" onClick={handleReset}>New Analysis</Button>
              </div>
              
              {result.error_message && (
                <Alert variant="destructive" className="mb-6">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Partial Results</AlertTitle>
                  <AlertDescription>{result.error_message}</AlertDescription>
                </Alert>
              )}
              
              <OverviewCard result={result} />
              <SkillsTable skillMatch={result.skill_match} />
              <GapsTable skillGaps={result.skill_gaps} />
              <InterviewPanel interviewQuestions={result.interview_questions} />
              <RoadmapPanel careerRoadmap={result.career_roadmap} />
              <ReportPanel finalReport={result.final_report} cvRewrites={result.cv_rewrites} />
              
              <p className="text-center text-xs text-muted-foreground mt-12 pt-8 border-t">
                This report is generated automatically by AI. Please review for accuracy.
              </p>
            </div>
          </div>
        )}
      </main>
      
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map(t => <Toast key={t.id} {...t} />)}
      </div>
    </div>
  );
}