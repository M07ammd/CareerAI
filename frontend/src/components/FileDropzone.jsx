import { FileText, X, UploadCloud, CheckCircle } from 'lucide-react';
import { Card, CardContent } from './ui/card';

export function FileDropzone({ file, isDragOver, error, onInputChange, onDragOver, onDragLeave, onDrop, onClear }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" htmlFor="cv-upload">
          Resume / CV
        </label>
        <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground bg-secondary px-2 py-0.5 rounded">PDF only</span>
      </div>
      <Card 
        className={`border-2 border-dashed transition-colors relative overflow-hidden group hover:border-primary/50 hover:bg-muted/30 ${isDragOver ? 'border-primary bg-muted/50' : 'border-muted'} ${file ? 'border-emerald-500/50 bg-emerald-50/30' : ''}`}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      >
        <CardContent className="p-8 flex flex-col items-center justify-center text-center">
          {!file && (
            <input type="file" accept=".pdf" onChange={onInputChange} id="cv-upload" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
          )}
          {file ? (
            <div className="flex flex-col items-center gap-2">
              <CheckCircle className="h-8 w-8 text-emerald-500 mb-2" />
              <p className="text-sm font-medium text-emerald-700">File ready</p>
              <div className="flex items-center gap-2 bg-background border shadow-sm rounded-md px-3 py-1.5 mt-2">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium truncate max-w-[150px]">{file.name}</span>
                <span className="text-xs text-muted-foreground">({(file.size/1024).toFixed(0)} KB)</span>
                <button className="ml-2 p-1 hover:bg-muted rounded-full transition-colors text-muted-foreground hover:text-foreground" onClick={(e) => { e.stopPropagation(); onClear(); }} type="button">
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <div className="p-3 bg-secondary rounded-full mb-2 group-hover:scale-110 transition-transform">
                <UploadCloud className="h-6 w-6 text-muted-foreground" />
              </div>
              <p className="text-sm font-medium">Drop PDF here or click to browse</p>
              <p className="text-xs text-muted-foreground">Maximum file size: 10 MB</p>
            </div>
          )}
        </CardContent>
      </Card>
      {error && <p className="text-sm font-medium text-destructive">{error}</p>}
    </div>
  );
}