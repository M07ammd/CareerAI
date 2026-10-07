import { FileText, X, UploadCloud, CheckCircle } from 'lucide-react';

export function FileDropzone({ file, isDragOver, error, onInputChange, onDragOver, onDragLeave, onDrop, onClear }) {
  return (
    <div className="form-field">
      <label className="form-label" htmlFor="cv-upload">
        Resume / CV
        <span className="chip chip-neutral">PDF only</span>
      </label>
      <div
        className={dropzone}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        role="button"
        tabIndex={0}
        aria-label="Upload PDF resume"
      >
        {!file && (
          <input type="file" accept=".pdf" onChange={onInputChange} id="cv-upload" aria-describedby="cv-hint" />
        )}
        {file ? (
          <>
            <CheckCircle size={20} color="var(--green)" style={{margin:'0 auto 8px'}} />
            <p className="dropzone-label">File ready</p>
            <div className="file-chip">
              <FileText size={14} />
              <span>{file.name}</span>
              <span className="td-muted">({(file.size/1024).toFixed(0)} KB)</span>
              <button className="file-chip-remove" onClick={(e) => { e.stopPropagation(); onClear(); }} aria-label="Remove file" type="button">
                <X size={12} />
              </button>
            </div>
          </>
        ) : (
          <>
            <UploadCloud size={20} color="var(--text-3)" style={{margin:'0 auto 8px'}} />
            <p className="dropzone-label">Drop PDF here or click to browse</p>
            <p className="dropzone-hint" id="cv-hint">PDF only · max 10 MB</p>
          </>
        )}
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
    </div>
  );
}