import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';

export default function Toast({ message, type = 'info' }) {
  const isSuccess = type === 'success';
  const isError = type === 'error';
  
  return (
    <div className="pointer-events-auto w-full max-w-sm rounded-lg shadow-lg">
      <Alert variant={isError ? 'destructive' : 'default'} className={`border ${isSuccess ? 'border-emerald-500 bg-emerald-50 text-emerald-900' : 'bg-background'}`}>
        {isSuccess ? <CheckCircle className="h-4 w-4 text-emerald-600" /> : isError ? <XCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
        <AlertDescription className="font-medium ml-2">
          {message}
        </AlertDescription>
      </Alert>
    </div>
  );
}