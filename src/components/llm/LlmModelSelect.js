import React, { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { BACKEND_URL } from '@/lib/constants'; // Assuming BACKEND_URL is defined here
import { InfoCircledIcon } from "@radix-ui/react-icons";

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
const LlmModelSelect = ({
  value, // External value prop for selected model alias
  onModelChange, // External handler for when the model changes
  label = "LLM Provider/Model", // Label for the select input
  disabled = false, // Disable the select input
  filterCapabilities, // Optional array of required capabilities (e.g., ['text', 'vision'])
  tooltipContent, // Optional tooltip content
  required = false, // Optional required indicator
  ...props // Pass any other props to the Select component
}) => {
  const [models, setModels] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Effect to fetch models on component mount and when filterCapabilities changes
  useEffect(() => {
    const fetchModels = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Use the dedicated backend endpoint
        const response = await fetch(`${BACKEND_URL}/llm/models`);
        if (!response.ok) {
          // Attempt to read error body if available, otherwise use status text
          const errorBody = await response.text().catch(() => 'Unknown Error');
          throw new Error(`Failed to fetch LLM models: ${response.status} ${response.statusText} - ${errorBody.substring(0, 200)}...`);
        }
        const data = await response.json();

        // Filter models based on required capabilities if filterCapabilities is provided
        const filtered = filterCapabilities
          ? (data || []).filter(model =>
              model && // Ensure model is not null/undefined
              model.capabilities &&
              Array.isArray(model.capabilities) &&
              filterCapabilities.every(cap => model.capabilities.includes(cap))
            )
          : (data || []);

        setModels(filtered); // Ensure models is always an array
        console.log("[LlmModelSelect] Fetched and filtered models:", filtered);

      } catch (err) {
        console.error("Error fetching LLM models:", err);
        setError(err.message);
        setModels([]); // Clear models on error
      } finally {
        setIsLoading(false);
      }
    };

    fetchModels();
  }, []); // Empty dependency array means this effect runs only once on mount

  // Filter out models with empty or null aliases for Select.Item value
  // This is done here before mapping to SelectItems
  const validModelsForSelect = models.filter(model => model && model.alias && model.alias.trim() !== '');

  // Determine placeholder text based on loading/error state and model availability
  const placeholder = isLoading
    ? "Loading models..."
    : error
      ? "Error loading models"
      : validModelsForSelect.length === 0
        ? "No models available"
        : "Select an LLM model";

  // Determine if the select should be disabled
  const isSelectDisabled = disabled || isLoading || (validModelsForSelect.length === 0 && !isLoading); // Disabled if explicitly disabled, loading, OR finished loading with no models

  // Find the selected model object to potentially display more info (optional)
  const currentModel = validModelsForSelect.find(model => model.alias === value);

  return (
    <div className="space-y-2" {...props}> {/* Use a div to apply props like className */}
      <Label htmlFor="llm-model">{label} {required && '*'}</Label>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
             <div className="flex items-center gap-2">
               <Select
                 value={value || ''} // Directly controlled by the external value prop
                 onValueChange={onModelChange} // Directly use the external handler
                 disabled={isSelectDisabled} // Use the calculated disabled state
               >
                 <SelectTrigger id="llm-model">
                   <SelectValue placeholder={placeholder} />
                 </SelectTrigger>
                 <SelectContent>
                   {validModelsForSelect.map((model) => (
                     // Use model.alias for value and key, as it's guaranteed non-empty by validModelsFilter
                     <SelectItem
                       key={model.alias}
                       value={model.alias}
                       // Add disabled logic based on filterCapabilities if needed per item
                       // Ensure the SelectItem itself is not disabled if the overall Select is enabled
                       disabled={isSelectDisabled ? true : (filterCapabilities && (!model.capabilities || !Array.isArray(model.capabilities) || !filterCapabilities.every(cap => model.capabilities.includes(cap))))}
                     >
                       {model.alias}
                     </SelectItem>
                   ))}
                 </SelectContent>
               </Select>
                {tooltipContent && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <InfoCircledIcon className="h-4 w-4 text-gray-500 cursor-help" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{tooltipContent}</p>
                    </TooltipContent>
                  </Tooltip>
                )}

             </div>
          </TooltipTrigger>
           {/* If tooltipContent is for the entire Select, it should be outside */}
        </Tooltip>
      </TooltipProvider>

      {/* Optional: Display description or provider of selected model */}
      {/* {currentModel && currentModel.description && (
          <p className="text-gray-600 text-sm">{currentModel.description}</p>
      )} */}
    </div>
  );
};

export default LlmModelSelect;
