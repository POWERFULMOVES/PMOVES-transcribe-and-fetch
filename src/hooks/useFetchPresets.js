"use client";

import { useState, useEffect, useCallback } from 'react';
import { toast } from "sonner";
import { useToast } from "@/hooks/use-toast";
import { BACKEND_URL } from '@/lib/constants';
// Removed createClient as we are now using the API endpoint
// import { createClient } from '@/lib/client';

export function useFetchPresets() {
  const [presets, setPresets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  // Supabase client is no longer needed here
  // const supabase = createClient();

  const fetchPresets = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch from the backend API endpoint instead of directly from Supabase
      const response = await fetch(`${BACKEND_URL}/api/presets`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({})); // Try to parse error, fallback to empty object
        throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      setPresets(data || []);
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "An unknown error occurred while fetching presets.";
      setError(errorMessage);
      toast.error(`Error fetching presets: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  }, []); // Removed supabase from dependency array

  useEffect(() => {
    fetchPresets();
  }, [fetchPresets]);

  return { presets, isLoading, error, refetchPresets: fetchPresets };
} 