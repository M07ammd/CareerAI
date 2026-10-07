import { useState } from 'react';
import { analyzeCareer } from './api';
import { useFileUpload } from './hooks/useFileUpload';
import LoadingOverlay from './components/LoadingOverlay';
import ScoreBanner from './components/ScoreBanner';
import SkillsCard from './components/SkillsCard';
import GapCard from './components/GapCard';
import InterviewCard from './components/InterviewCard';
import RoadmapCard from './components/RoadmapCard';
import ReportCard from './components/ReportCard';
import SummaryCards from './components/SummaryCards';

const SAMPLE_JD = `Senior Machine Learning Engineer

We are building the next generation of AI-powered products and are looking for a Senior ML Engineer to join our team.

Required Skills:
- 5+ years of experience in Machine Learning / AI
- Strong Python programming (expert level)
- PyTorch or TensorFlow proficiency
- Experience with LLMs, prompt engineering, and LangChain/LangGraph
- FastAPI or similar frameworks for ML API development
- Docker and Kubernetes for containerization and orchestration
- Cloud platforms (AWS, GCP, or Azure)
- MLOps practices (MLflow, DVC, model monitoring)

Preferred:
- Experience with transformer architectures (BERT, GPT variants)
- RAG systems and vector databases
- Distributed training (DeepSpeed, FSDP)
- Technical leadership experience

Responsibilities:
- Design and implement production-grade ML pipelines
- Build and deploy LLM-based applications
- Collaborate with product and data teams
- Lead technical decisions and mentor junior engineers
- Drive MLOps and model monitoring best practices`;

export default function App() {
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const { file, isDragOver, error: fileError, onInputChange, onDragOver, onDragLeave, onDrop } =
    useFileUpload();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) { setError('Please upload your CV PDF.'); return; }
    if (!jobDescription.trim() || jobDescription.trim().length < 50) {
      setError('Please paste a complete job description (at least 50 characters).'); return;
    }
    setError('');
    setResult(null);
    setIsLoading(true);

    try {
      const data = await analyzeCareer(file, jobDescription);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError('');
    setJobDescription('');
  };

  return (
    <>
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-inner">
            <a className="logo" href="/">
              <div className="logo-icon">🚀</div>
              <span className="logo-text">CareerPilot AI</span>
              <span className="logo-badge">Beta</span>
            </a>
            {result && (
              <button className="btn-reset" onClick={handleReset}>
                ← New Analysis
              </button>
            )}
          </div>
        </div>
      </header>

      <LoadingOverlay isVisible={isLoading} />

      <main>
        {/* ===== UPLOAD FORM (shown when no results) ===== */}
        {!result && (
          <>
            <section className="hero">
              <div className="container">
                <div className="hero-badge">
                  <span>✨</span>
                  Agentic AI · LangGraph · Multi-Agent Workflow
                </div>
                <h1 className="hero-title">
                  Land Your Dream Job<br />
                  with <span className="gradient-text">AI-Powered</span><br />
                  Career Intelligence
                </h1>
                <p className="hero-subtitle">
                  Upload your CV and a job description. Our multi-agent AI pipeline
                  analyzes your profile, identifies gaps, generates interview questions,
                  and builds a personalised career roadmap.
                </p>
              </div>
            </section>

            <section className="upload-section">
              <div className="container">
                {error && (
                  <div className="error-banner" style={{ marginBottom: 24 }}>
                    <div className="error-icon">⚠️</div>
                    <div>
                      <div className="error-title">Error</div>
                      <div className="error-message">{error}</div>
                    </div>
                  </div>
                )}

                <div className="form-card">
                  <form onSubmit={handleSubmit} className="form-grid">
                    {/* CV Upload */}
                    <div className="form-group">
                      <label className="form-label">
                        Resume / CV
                        <span className="label-badge required">Required</span>
                      </label>
                      <div
                        className={`dropzone ${isDragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
                        onDragOver={onDragOver}
                        onDragLeave={onDragLeave}
                        onDrop={onDrop}
                      >
                        <input
                          type="file"
                          accept=".pdf"
                          onChange={onInputChange}
                          id="cv-upload"
                        />
                        <div className="dropzone-icon">
                          {file ? '✅' : '📄'}
                        </div>
                        {file ? (
                          <>
                            <div className="dropzone-title">File Uploaded!</div>
                            <div className="dropzone-file-name">{file.name}</div>
                            <div className="dropzone-subtitle" style={{ marginTop: 4 }}>
                              {(file.size / 1024).toFixed(1)} KB · Click to replace
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="dropzone-title">Drop your PDF here</div>
                            <div className="dropzone-subtitle">or click to browse · PDF only · Max 10MB</div>
                          </>
                        )}
                      </div>
                      {fileError && (
                        <p style={{ fontSize: 13, color: 'var(--red)' }}>{fileError}</p>
                      )}
                    </div>

                    {/* Job Description */}
                    <div className="form-group">
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <label className="form-label" htmlFor="jd-textarea">
                          Job Description
                          <span className="label-badge required">Required</span>
                        </label>
                        <button
                          type="button"
                          onClick={() => setJobDescription(SAMPLE_JD)}
                          style={{
                            fontSize: 12,
                            color: 'var(--accent-primary)',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            textDecoration: 'underline',
                          }}
                        >
                          Use sample JD
                        </button>
                      </div>
                      <textarea
                        id="jd-textarea"
                        className="textarea"
                        placeholder="Paste the full job description here…&#10;&#10;Include: required skills, responsibilities, qualifications, and any technologies mentioned."
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        rows={10}
                      />
                      <p style={{ fontSize: 12, color: 'var(--text-muted)', textAlign: 'right' }}>
                        {jobDescription.length} characters
                        {jobDescription.length < 50 && jobDescription.length > 0 && (
                          <span style={{ color: 'var(--red)' }}> (min 50)</span>
                        )}
                      </p>
                    </div>

                    <button
                      type="submit"
                      className="btn-analyze"
                      disabled={isLoading || !file || jobDescription.trim().length < 50}
                    >
                      🚀 Analyze My Career Profile
                    </button>
                  </form>
                </div>

                {/* Feature bullets */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: 16,
                  marginTop: 32,
                }}>
                  {[
                    { icon: '⚡', title: 'Skill Matching', desc: 'Compare your skills vs requirements' },
                    { icon: '🔍', title: 'Gap Analysis', desc: 'Prioritised missing skills' },
                    { icon: '🎤', title: 'Interview Prep', desc: 'Personalised questions' },
                    { icon: '🗺️', title: 'Career Roadmap', desc: 'Step-by-step learning plan' },
                  ].map((feat) => (
                    <div key={feat.title} style={{
                      padding: '16px 20px',
                      background: 'var(--bg-card)',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--border)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                    }}>
                      <span style={{ fontSize: 24 }}>{feat.icon}</span>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 14 }}>{feat.title}</div>
                        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{feat.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </>
        )}

        {/* ===== RESULTS DASHBOARD ===== */}
        {result && (
          <div className="results-section">
            <div className="container">
              <div className="results-header">
                <div>
                  <h1 className="results-title">📊 Analysis Results</h1>
                  <p className="results-subtitle">
                    {result.processing_steps?.length || 0} agents completed ·{' '}
                    {result.status === 'success' ? '✅ Full analysis' : '⚠️ Partial results'}
                  </p>
                </div>
                <button className="btn-reset" onClick={handleReset}>
                  ← New Analysis
                </button>
              </div>

              {/* Error banner for partial results */}
              {result.error_message && (
                <div className="error-banner">
                  <div className="error-icon">⚠️</div>
                  <div>
                    <div className="error-title">Partial Results</div>
                    <div className="error-message">{result.error_message}</div>
                  </div>
                </div>
              )}

              {/* Score Banner */}
              <ScoreBanner result={result} />

              {/* Dashboard Grid */}
              <div className="dashboard-grid">
                {/* Candidate + Job summaries */}
                <SummaryCards
                  resumeAnalysis={result.resume_analysis}
                  jobAnalysis={result.job_analysis}
                />

                {/* Skill Match */}
                {result.skill_match && <SkillsCard skillMatch={result.skill_match} />}

                {/* Gap Analysis */}
                {result.skill_gaps && <GapCard skillGaps={result.skill_gaps} />}

                {/* Interview Questions — full width */}
                {result.interview_questions && (
                  <div className="full-width">
                    <InterviewCard interviewQuestions={result.interview_questions} />
                  </div>
                )}

                {/* Roadmap — full width */}
                {result.career_roadmap && (
                  <div className="full-width">
                    <RoadmapCard careerRoadmap={result.career_roadmap} />
                  </div>
                )}

                {/* Final Report — full width */}
                {result.final_report && (
                  <div className="full-width">
                    <ReportCard finalReport={result.final_report} />
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border)',
        padding: '24px 0',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: 13,
      }}>
        <div className="container">
          CareerPilot AI · Powered by LangGraph + Multi-Agent AI
        </div>
      </footer>
    </>
  );
}
