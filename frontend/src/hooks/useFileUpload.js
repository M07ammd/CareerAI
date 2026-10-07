import { useState, useCallback } from 'react';

export function useFileUpload() {
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState('');

  const validateAndSet = useCallback((f) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are accepted.');
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File must be under 10 MB.');
      return;
    }
    setError('');
    setFile(f);
  }, []);

  return {
    file,
    isDragOver,
    error,
    clear: () => { setFile(null); setError(''); },
    onInputChange: (e) => validateAndSet(e.target.files?.[0]),
    onDragOver:  (e) => { e.preventDefault(); setIsDragOver(true); },
    onDragLeave: ()  => setIsDragOver(false),
    onDrop: (e) => { e.preventDefault(); setIsDragOver(false); validateAndSet(e.dataTransfer.files?.[0]); },
  };
}