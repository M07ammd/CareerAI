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
- Mentor junior engineers`;;

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
    document.documentElement.setAttribute('data-theme', t);
  }, []);

  const toggleTheme = () => {
    const t = theme === 'light' ? 'dark' : 'light';
    setTheme(t);
    localStorage.setItem('careerpilot-theme', t);
    document.documentElement.setAttribute('data-theme', t);
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
    <>
      <header className="header">
        <div className="container header-inner">
          <a className="wordmark" href="/">
            <div className="wordmark-icon"><Layers size={16} /></div>
            <span className="wordmark-name">CareerPilot</span>
          </a>
          <div className="header-nav">
            <button className="btn btn-ghost btn-sm" disabled>Compare</button>
            <button className="btn btn-ghost btn-sm" disabled>Practice</button>
          </div>
          <div className="header-actions">
            <button className="btn btn-icon btn-ghost" onClick={toggleTheme} aria-label="Toggle theme">
              {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
            </button>
          </div>
        </div>
      </header>

      <main className="page">
        {!result && !isLoading && (
          <div className="input-page">
            <div className="page-headline">
              <h1>Career Analysis</h1>
              <p>Compare your resume against a target role to find skill gaps and get a tailored learning roadmap.</p>
            </div>
            {error && (
              <div className="alert alert-error" style={{marginBottom:24}}>
                <div className="alert-icon"><AlertTriangle size={14} /></div>
                <div><div className="alert-title">Error</div><div className="alert-desc">{error}</div></div>
              </div>
            )}
            <form onSubmit={handleSubmit} className="form-layout">
              <div className="form-columns">
                <FileDropzone {...fileUpload} />
                <div className="form-field">
                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                    <label className="form-label" htmlFor="jd-input">Job Description</label>
                    <button type="button" className="btn btn-ghost btn-sm" onClick={() => setJobDescription(SAMPLE_JD)} style={{fontSize:11,padding:'2px 6px',height:'auto'}}>
                      Sample
                    </button>
                  </div>
                  <textarea id="jd-input" className="textarea" placeholder="Paste the job description here…" value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
                  <div className={char-count }>
                    {jobDescription.length} chars (min 50)
                  </div>
                </div>
              </div>
              <button type="submit" className="btn btn-primary btn-lg btn-full" disabled={!fileUpload.file || jobDescription.length < 50}>
                Analyze Profile
              </button>
            </form>
          </div>
        )}

        {isLoading && (
          <div className="input-page">
            <div className="page-headline">
              <h1>Analyzing Profile</h1>
              <p>This may take a minute or two as we run multiple AI agents to evaluate your resume against the job description.</p>
            </div>
            <ProgressPanel isVisible={true} onCancel={() => setIsLoading(false)} />
            <div className="skeleton" style={{height:400,marginTop:24}} />
          </div>
        )}

        {result && !isLoading && (
          <div className="container">
            <div className="results-layout">
              <Sidebar score={score} />
              <div className="results-main">
                <div className="results-actions">
                  <h1 className="results-actions-title">Analysis Results</h1>
                  <button className="btn btn-outline btn-sm" onClick={handleReset}>New Analysis</button>
                </div>
                {result.error_message && (
                  <div className="alert alert-warn" style={{marginBottom:16}}>
                    <div className="alert-icon"><AlertTriangle size={14} /></div>
                    <div>
                      <div className="alert-title">Partial Results</div>
                      <div className="alert-desc">{result.error_message}</div>
                    </div>
                  </div>
                )}
                
                <OverviewCard result={result} />
                <SkillsTable skillMatch={result.skill_match} />
                <GapsTable skillGaps={result.skill_gaps} />
                <InterviewPanel interviewQuestions={result.interview_questions} />
                <RoadmapPanel careerRoadmap={result.career_roadmap} />
                <ReportPanel finalReport={result.final_report} cvRewrites={result.cv_rewrites} />
                
                <div className="disclaimer">
                  This report is generated automatically by AI and should be reviewed for accuracy.
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
      
      <div className="toast-container" aria-live="assertive">
        {toasts.map(t => <Toast key={t.id} {...t} />)}
      </div>
    </>
  );
}