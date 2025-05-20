import { useState, useEffect } from 'react';
import axios from 'axios';
import { BACKEND_URL } from '@/lib/constants';

export default function useAppConfig() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    axios.get(`${BACKEND_URL}/api/app-config`)
      .then(res => { if (isMounted) setConfig(res.data); })
      .catch(err => { if (isMounted) setError(err); })
      .finally(() => { if (isMounted) setLoading(false); });
    return () => { isMounted = false; };
  }, []);

  return { config, loading, error };
} 