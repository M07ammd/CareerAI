const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Run the full career analysis.
 * @param {File} cvFile - PDF file
 * @param {string} jobDescription - Job description text
 * @returns {Promise<object>} Analysis response
 */
export async function analyzeCareer(cvFile, jobDescription) {
  const formData = new FormData();
  formData.append('cv_file', cvFile);
  formData.append('job_description', jobDescription);

  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Check backend health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
