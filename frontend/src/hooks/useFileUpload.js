import { useState, useCallback } from 'react';

/**
 * Custom hook managing drag-and-drop file upload state.
 */
export function useFileUpload() {
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState('');

  const validateFile = (f) => {
    if (!f) return 'No file selected.';
    if (!f.name.toLowerCase().endsWith('.pdf')) return 'Only PDF files are supported.';
    if (f.size > 10 * 1024 * 1024) return 'File must be smaller than 10MB.';
    return null;
  };

  const handleFile = useCallback((f) => {
    const err = validateFile(f);
    if (err) {
      setError(err);
      setFile(null);
    } else {
      setError('');
      setFile(f);
    }
  }, []);

  const onInputChange = useCallback((e) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const onDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const onDragLeave = useCallback(() => setIsDragOver(false), []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  }, [handleFile]);

  return { file, isDragOver, error, onInputChange, onDragOver, onDragLeave, onDrop, setFile };
}
