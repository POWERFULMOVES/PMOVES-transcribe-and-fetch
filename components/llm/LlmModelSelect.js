import React, { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { BACKEND_URL } from '@/lib/constants'; // Assuming BACKEND_URL is defined here

// Define a basic type for the model data we expect from the backend
// This should match the structure returned by GET /llm/models
// Based on backend/app/routes/llm_routes.py comment about StandardizedLLM
// We might expect fields like 'id', 'alias', 'provider', 'capabilities', 'description'
// For now, we'll use 'alias' and 'description' and display 'alias'.
// We use type Any for flexibility if the exact structure isn't known/standardized yet.
// type StandardizedLLM = {
//   id: string;
//   alias: string;
//   provider: string;
//   capabilities: string[]; // e.g., ['text', 'chat', 'embeddings', 'vision', 'tool_calling']
//   description?: string;
//   [key: string]: any; // Allow other fields
// };

// This component fetches available LLM models from the backend registry
// and provides a Select dropdown for the user to choose a model.
// It uses the /llm/models endpoint.
export default function LlmModelSelect({
  label = "LLM Model", // Label for the select input
  selectedModelAlias, // The currently selected model alias (controlled from parent)
  onModelSelect, // Callback function when a model is selected (receives alias)
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
        // Assuming the endpoint is at /llm/models relative to BACKEND_URL
        const response = await fetch(`${BACKEND_URL}/llm/models`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: "Failed to parse error response" }));
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Filter models based on required capabilities if filterCapabilities is provided
        const filteredModels = filterCapabilities && Array.isArray(filterCapabilities) && filterCapabilities.length > 0
          ? data.filter(model => 
              model.capabilities && Array.isArray(model.capabilities) && 
              filterCapabilities.every(cap => model.capabilities.includes(cap))
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
    <div className="space-y-2" {...props}> {/* Use a div to apply props like className */}
      <Label>{label}</Label>
      <TooltipProvider delayDuration={300}> {/* Wrap with TooltipProvider */}
        <Select
          value={selectedModelAlias || ''} // Ensure controlled component
          onValueChange={handleValueChange}
          disabled={disabled || isLoading || models.length === 0}
        >
          <SelectTrigger>
            <SelectValue placeholder={isLoading ? "Loading models..." : error ? "Error loading models" : models.length === 0 ? "No models available" : "Select a model"} />
          </SelectTrigger>
          <SelectContent>
            {isLoading && <SelectItem value="" disabled>Loading models...</SelectItem>}
            {models.map(model => (
               <Tooltip key={model.alias}> {/* Wrap SelectItem content with Tooltip */}
                <TooltipTrigger asChild>
                  {/* SelectItem value must be the model alias string */}
                  <SelectItem value={model.alias} disabled={!model.alias || !model.capabilities || !filterCapabilities.every(cap => model.capabilities.includes(cap))}> {/* Disable if missing alias or capabilities mismatch */}
                      {/* Display alias or a user-friendly name if available */}
                      {model.alias || model.id || "Unnamed Model"}
                  </SelectItem>
                </TooltipTrigger>
                <TooltipContent>
                   {/* Display full details in tooltip */}
                   <p>{model.alias || model.id || "Unnamed Model"}</p>
                   {model.description && <p>{model.description}</p>}
                   {model.provider && <p>Provider: {model.provider}</p>}
                   {model.capabilities && Array.isArray(model.capabilities) && 
                    <p>Capabilities: {model.capabilities.join(', ')}</p>}
                </TooltipContent>
              </Tooltip>
            ))}
          </SelectContent>
        </Select>
      </TooltipProvider>
    </div>
  );
} 