"use client";

import { useState, useEffect, useCallback } from 'react';
import { useToast } from "@/hooks/use-toast";
// Removed createClient as we are now using the API endpoint
// import { createClient } from '@/lib/client';

export function useFetchPresets() {
  const [presets, setPresets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { toast } = useToast();
  // Supabase client is no longer needed here
  // const supabase = createClient();

  const fetchPresets = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch from the backend API endpoint instead of directly from Supabase
      const response = await fetch('/api/presets');

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({})); // Try to parse error, fallback to empty object
        throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      setPresets(data || []);
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : "An unknown error occurred while fetching presets.";
      setError(errorMessage);
      toast({
        title: "Error Fetching Presets",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]); // Removed supabase from dependency array

  useEffect(() => {
    fetchPresets();
  }, [fetchPresets]);

  return { presets, isLoading, error, refetchPresets: fetchPresets };
} 