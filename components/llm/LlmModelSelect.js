import React, { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { BACKEND_URL } from '@/lib/constants'; // Assuming BACKEND_URL is defined here

// Define a basic type for the model data we expect from the backend
// This should match the structure returned by GET /llm/models
// Based on backend/app/routes/llm_routes.py comment about StandardizedLLM
// We might expect fields like 'id', 'alias', 'provider', 'capabilities', 'description'
// For now, we'll use 'model_id' and 'display_name'.
// Based on backend StandardizedLLM, which has model_id, display_name, provider, capabilities.
// type StandardizedLLM = {
//   model_id: string; // e.g., "openai/gpt-3.5-turbo"
//   display_name: string; // e.g., "GPT-3.5 Turbo (OpenAI)"
//   provider: string; // e.g., "openai"
//   capabilities: Array<{ type: string, description: string }>; // e.g., [{type: 'text', description: '...'}, ...]
//   [key: string]: any; // Allow other fields
// };

// This component fetches available LLM models from the backend registry
// and provides a Select dropdown for the user to choose a model.
// It uses the /api/v1/models endpoint.
export default function LlmModelSelect({
  label = "LLM Model", // Label for the select input
  selectedModelAlias, // The currently selected model ID (prop name will be updated later)
  onModelSelect, // Callback function when a model is selected (receives model_id)
  disabled = false, // Disable the select input
  filterCapabilities, // Optional array of required capabilities (e.g., ['text', 'vision'])
  ...props // Pass any other props to the Select component
}) {
  const [models, setModels] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        setIsLoading(true);
        setError(null);
        // Fetch from the new endpoint /api/v1/models
        const response = await fetch(`${BACKEND_URL}/api/v1/models`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: "Failed to parse error response" }));
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Fetched models:", data); // Inspect the structure of fetched models

        // Filter models based on required capabilities if filterCapabilities is provided
        const filteredModels = filterCapabilities && Array.isArray(filterCapabilities) && filterCapabilities.length > 0
          ? data.filter(model =>
              model.capabilities && Array.isArray(model.capabilities) &&
              filterCapabilities.every(cap => model.capabilities.map(c => c.type).includes(cap))
            )
          : data; // No filtering needed if no filterCapabilities provided

        setModels(filteredModels);
        setIsLoading(false);

      } catch (err) {
        console.error("Error fetching LLM models:", err);
        setError(err.message || "Failed to load models");
        setIsLoading(false);
      }
    };

    fetchModels();
  }, [filterCapabilities]); // Re-fetch if filterCapabilities changes

  // Handle selection change
  const handleValueChange = (value) => {
    if (onModelSelect) {
      onModelSelect(value);
    }
  };

  // If there's an error and no models loaded, display error message
  if (error && models.length === 0) {
    return (
      <div className="text-destructive text-sm mt-2">
        Error loading models: {error}
      </div>
    );
  }

  return (
    <div className="space-y-2" {...props}>
      <Label>{label}</Label>
      <TooltipProvider delayDuration={300}>
        <Select
          value={selectedModelAlias || ''} // Compare with model.model_id
          onValueChange={handleValueChange} // Passes model_id to callback
          disabled={disabled || isLoading || models.length === 0}
        >
          <SelectTrigger>
            <SelectValue placeholder={isLoading ? "Loading models..." : error ? "Error loading models" : models.length === 0 ? "No models available" : "Select a model"} />
          </SelectTrigger>
          <SelectContent>
            {isLoading && <SelectItem value="" disabled>Loading models...</SelectItem>}
            {models.map(model => (
              <Tooltip key={model.model_id}> {/* Use model.model_id as key */}
                <TooltipTrigger asChild>
                  {/* SelectItem value is model.model_id */}
                  <SelectItem
                    value={model.model_id}
                    disabled={
                      !model.model_id ||
                      (filterCapabilities && Array.isArray(filterCapabilities) && filterCapabilities.length > 0 &&
                       !(model.capabilities && Array.isArray(model.capabilities) && filterCapabilities.every(cap => model.capabilities.map(c => c.type).includes(cap)))
                      )
                    }
                  >
                    {model.display_name || model.model_id || "Unnamed Model"} {/* Display model.display_name */}
                  </SelectItem>
                </TooltipTrigger>
                <TooltipContent>
                  <p><strong>{model.display_name || model.model_id}</strong></p>
                  {model.provider && <p>Provider: {model.provider}</p>}
                  <p>ID: {model.model_id}</p>
                  {model.capabilities && Array.isArray(model.capabilities) && model.capabilities.length > 0 &&
                    <p>Capabilities: {model.capabilities.map(c => c.type).join(', ')}</p>}
                </TooltipContent>
              </Tooltip>
            ))}
          </SelectContent>
        </Select>
      </TooltipProvider>
    </div>
  );
}