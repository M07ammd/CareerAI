// Use relative URL by default so the Vite dev proxy (vite.config.js) and the
// production nginx proxy both work without hardcoding a hostname.
// Override at build time with VITE_API_URL only when deploying to a separate domain.
const API_BASE = import.meta.env.VITE_API_URL || '/api';

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
    const error = await response.json().catch(() => ({ detail: 'Network error or server unavailable' }));
    
    // FastAPI validation errors (422) return an array of objects in error.detail
    let errorMessage = `HTTP ${response.status}`;
    if (error.detail) {
      errorMessage = typeof error.detail === 'string' 
        ? error.detail 
        : JSON.stringify(error.detail);
    }
    
    throw new Error(errorMessage);
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
