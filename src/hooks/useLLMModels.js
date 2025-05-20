import { useState, useEffect, useCallback } from 'react';
import apiClient from '@/utils/apiClient'; // Assuming you have an apiClient utility

const useLLMModels = () => {
  const [models, setModels] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchModels = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Endpoint based on llm_routes.py: router.get("/models")
      // Full path will be /api/v1/models because llm_router is prefixed with /api/v1
      const modelsArray = await apiClient.get('/api/v1/models'); // apiClient.get returns the array directly
      // The modelsArray is expected to be the direct list of models
      // as returned by llm_registry_service.get_available_models()
      // which is a list of StandardizedLLM objects (dictionaries)
      if (modelsArray && Array.isArray(modelsArray)) {
        // Filter out models with empty or missing model_id
        const validModels = modelsArray.filter(model => model.model_id && model.model_id.trim() !== '');

        // De-duplicate models based on model_id
        const uniqueModels = [];
        const seenModelIds = new Set();
        for (const model of validModels) {
          if (model.model_id && !seenModelIds.has(model.model_id)) {
            uniqueModels.push(model);
            seenModelIds.add(model.model_id);
          }
        }

        // Sort unique models by alias (model_id in StandardizedLLM)
        const sortedModels = [...uniqueModels].sort((a, b) => {
          // We've already filtered and de-duplicated, so model_id should exist and be unique
          return a.model_id.localeCompare(b.model_id);
        });
        setModels(sortedModels);
      } else {
        console.warn('No models data received or data is not an array:', modelsArray);
        setModels([]);
      }
    } catch (err) {
      console.error('Error fetching LLM models:', err);
      setError(err.message || 'Failed to fetch LLM models');
      setModels([]); // Clear models on error
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  return { models, isLoading, error, refetchModels: fetchModels };
};

export default useLLMModels; 