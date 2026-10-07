import { useState } from 'react';
import { MessageSquare } from 'lucide-react';

const CATEGORIES = [
  { key: 'technical_questions',  label: 'Technical' },
  { key: 'project_questions',    label: 'Project' },
  { key: 'behavioral_questions', label: 'Behavioral' },
  { key: 'hr_questions',         label: 'HR' },
];

export default function InterviewPanel({ interviewQuestions }) {
  const [activeTab, setActiveTab] = useState('technical_questions');
  if (!interviewQuestions) return null;

  const questions = interviewQuestions[activeTab] || [];

  return (
    <section className="section-card" id="section-interview">
      <div className="section-header">
        <div className="section-title">
          <MessageSquare size={14} />
          Interview Questions
        </div>
      </div>
      <div className="section-body" style={{paddingBottom:0}}>
        <div className="tab-bar" role="tablist">
          {CATEGORIES.map(c => {
            const count = interviewQuestions[c.key]?.length || 0;
            return (
              <button
                key={c.key}
                role="tab"
                aria-selected={activeTab === c.key}
                className={	ab-item}
                onClick={() => setActiveTab(c.key)}
                type="button"
              >
                {c.label}
                {count > 0 && <span className="tabular" style={{color:'var(--text-3)'}}>&nbsp;{count}</span>}
              </button>
            );
          })}
        </div>
      </div>
      <div className="q-list" role="tabpanel">
        {questions.length === 0 ? (
          <div className="q-item" style={{color:'var(--text-3)'}}>No questions in this category.</div>
        ) : (
          questions.map((q, i) => (
            <div key={i} className="q-item">
              <p className="q-text">{q.question}</p>
              {q.rationale && <p className="q-rationale">{q.rationale}</p>}
              {q.suggested_answer_points?.length > 0 && (
                <ul className="q-points">
                  {q.suggested_answer_points.map((pt, j) => <li key={j}>{pt}</li>)}
                </ul>
              )}
            </div>
          ))
        )}
      </div>
      {interviewQuestions.preparation_tips?.length > 0 && (
        <div className="section-body" style={{borderTop:'1px solid var(--border)'}}>
          <p style={{fontSize:12,fontWeight:600,color:'var(--text-3)',textTransform:'uppercase',letterSpacing:'0.4px',marginBottom:8}}>Preparation tips</p>
          <ul className="q-points">
            {interviewQuestions.preparation_tips.map((tip, i) => <li key={i}>{tip}</li>)}
          </ul>
        </div>
      )}
    </section>
  );
}