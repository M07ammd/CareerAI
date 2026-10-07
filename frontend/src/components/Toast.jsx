import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function Toast({ message, type = 'info' }) {
  const icons = {
    success: <CheckCircle size={14} />,
    error:   <XCircle size={14} />,
    info:    <AlertCircle size={14} />,
  };
  return (
    <div className="toast" role="status">
      {icons[type] || icons.info}
      <span>{message}</span>
    </div>
  );
}