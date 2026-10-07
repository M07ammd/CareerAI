import { useState } from 'react';

const TABS = [
  { key: 'technical', label: '⚙️ Technical', field: 'technical_questions' },
  { key: 'project', label: '🏗️ Projects', field: 'project_questions' },
  { key: 'behavioral', label: '🧠 Behavioral', field: 'behavioral_questions' },
  { key: 'hr', label: '💼 HR', field: 'hr_questions' },
];

/**
 * Interview questions card with tabbed categories.
 */
export default function InterviewCard({ interviewQuestions }) {
  const [activeTab, setActiveTab] = useState('technical');

  if (!interviewQuestions) return null;

  const currentTab = TABS.find((t) => t.key === activeTab);
  const questions = interviewQuestions[currentTab.field] || [];

  return (
    <div className="card full-width">
      <div className="card-header">
        <div className="card-icon blue">🎤</div>
        <div>
          <div className="card-title">Interview Preparation</div>
          <div className="card-subtitle">
            Personalised questions based on your CV & the job requirements
          </div>
        </div>
      </div>

      <div className="question-tabs">
        {TABS.map((tab) => {
          const count = interviewQuestions[tab.field]?.length || 0;
          return (
            <button
              key={tab.key}
              className={`question-tab ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label} {count > 0 && `(${count})`}
            </button>
          );
        })}
      </div>

      {questions.length === 0 ? (
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
          No questions in this category.
        </p>
      ) : (
        <div className="question-list">
          {questions.map((q, i) => (
            <div key={i} className="question-item">
              <p className="question-text">
                <span style={{ color: 'var(--accent-primary)', marginRight: 8 }}>Q{i + 1}.</span>
                {q.question}
              </p>
              {q.rationale && (
                <p className="question-rationale">💡 {q.rationale}</p>
              )}
              {q.suggested_answer_points?.length > 0 && (
                <ul className="question-points">
                  {q.suggested_answer_points.map((pt, j) => (
                    <li key={j}>{pt}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {interviewQuestions.preparation_tips?.length > 0 && (
        <div style={{
          marginTop: 20,
          padding: '14px 16px',
          background: 'rgba(99,102,241,0.05)',
          borderRadius: 'var(--radius)',
          border: '1px solid rgba(99,102,241,0.15)',
        }}>
          <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent-primary)', marginBottom: 8 }}>
            💡 PREPARATION TIPS
          </p>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
            {interviewQuestions.preparation_tips.map((tip, i) => (
              <li key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', paddingLeft: 16, position: 'relative' }}>
                <span style={{ position: 'absolute', left: 0, color: 'var(--accent-primary)' }}>•</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
