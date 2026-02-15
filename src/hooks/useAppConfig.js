import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { BACKEND_URL } from '@/lib/constants';
import { createClient } from '@/lib/client';

export default function useAppConfig() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const supabase = useMemo(() => createClient(), []);

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      try {
        const headers = {};
        const { data } = await supabase.auth.getSession();
        const token = data?.session?.access_token;
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await axios.get(`${BACKEND_URL}/api/app-config`, { headers });
        if (isMounted) {
          setConfig(response.data);
        }
      } catch (err) {
        if (isMounted) {
          setError(err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    load();
    return () => { isMounted = false; };
  }, [supabase]);

  return { config, loading, error };
} 
