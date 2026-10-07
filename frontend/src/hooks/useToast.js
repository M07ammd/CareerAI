import { useState } from 'react';

export function useToast() {
  const [toasts, setToasts] = useState([]);
  const push = (message, type = 'info', ms = 2500) => {
    const id = Date.now();
    setToasts(t => [...t, { id, message, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), ms);
  };
  return { toasts, push };
}