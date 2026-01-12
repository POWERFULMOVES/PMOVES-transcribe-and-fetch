import { useState, useEffect } from 'react';
import axios from 'axios';
import { BACKEND_URL } from '@/lib/constants';
import { useSession } from '@supabase/auth-helpers-react';

export default function useAppConfig() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const session = useSession();

  useEffect(() => {
    let isMounted = true;
    const headers = {};
    if (session?.access_token) {
      headers['Authorization'] = `Bearer ${session.access_token}`;
    }

    axios.get(`${BACKEND_URL}/api/app-config`, { headers })
      .then(res => { if (isMounted) setConfig(res.data); })
      .catch(err => { if (isMounted) setError(err); })
      .finally(() => { if (isMounted) setLoading(false); });
    return () => { isMounted = false; };
  }, [session]);

  return { config, loading, error };
} 