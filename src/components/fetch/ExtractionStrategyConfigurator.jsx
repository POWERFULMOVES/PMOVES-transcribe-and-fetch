"use client";

import React from 'react'; // Keep React, remove useState, useEffect if not used
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { InfoCircledIcon } from '@radix-ui/react-icons';

const extractionStrategies = [
  { value: "none", label: "None / Default" },
  { value: "llm", label: "LLMExtractionStrategy" },
  { value: "json_css", label: "JsonCssExtractionStrategy" },
  { value: "cosine", label: "CosineStrategy" },
  { value: "table", label: "Table Extraction (LLM-based)" }, // Added Table Extraction
];

const ExtractionStrategyConfigurator = ({ onConfigChange, initialConfig = { strategy: 'none', params: {} } }) => {
  // Component is now fully controlled by initialConfig prop.
  // No internal useState for selectedStrategy or strategyParams.
  // useEffect hooks for synchronization are removed.

  const currentStrategy = initialConfig.strategy || 'none';
  const currentParams = initialConfig.params || {};

  const handleStrategyChange = (newStrategyValue) => {
    // When strategy changes, call onConfigChange with the new strategy
    // and reset params to an empty object, as per previous logic.
    if (onConfigChange) {
      onConfigChange({ strategy: newStrategyValue, params: {} });
    }
  };

  const handleParamChange = (paramName, value) => {
    // When a specific parameter changes, call onConfigChange with the current strategy
    // and the updated params object.
    if (onConfigChange) {
      const updatedParams = {
        ...currentParams,
        [paramName]: value,
      };
      onConfigChange({
        strategy: currentStrategy,
        params: updatedParams,
      });
    }
  };

  const renderStrategyParams = () => {
    // Uses currentStrategy and currentParams derived from props.
    switch (currentStrategy) {
      case "json_css":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="json-css-schema">
                Schema (JSON)
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{'JSON schema defining the structure of the data to be extracted using CSS selectors. Example: `{"title": "h1", "author": ".author-name", "content": "article p"}`'}</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Textarea
                id="json-css-schema"
                placeholder='e.g., {"title": "h1", "author": ".author"}'
                value={currentParams.schema || ""}
                onChange={(e) => handleParamChange("schema", e.target.value)}
                className="min-h-[100px]"
              />
            </div>
          </div>
        );
      case "llm":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="llm-instructions">
                LLM Instructions/Prompt
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{'Detailed instructions or prompt for the LLM to guide content extraction. e.g., "Extract the main article content, summarize it, and list key entities." (Corresponds to `LLMExtractionStrategy.llm_instructions`)'}</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Textarea
                id="llm-instructions"
                placeholder="Enter LLM instructions or prompt..."
                value={currentParams.llm_instructions || ""}
                onChange={(e) => handleParamChange("llm_instructions", e.target.value)}
                className="min-h-[100px]"
              />
            </div>
            <div>
              <Label htmlFor="llm-provider-model">
                LLM Provider/Model
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{'Specify the LLM provider and model name (e.g., openai/gpt-4o, ollama/llama3). Determines which language model processes the content. (Corresponds to `LLMConfig.provider`)'}</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Input
                id="llm-provider-model"
                placeholder="e.g., openai/gpt-4o-mini, groq/llama3-70b, ollama/mistral"
                value={currentParams.llm_provider_model || ""}
                onChange={(e) => handleParamChange("llm_provider_model", e.target.value)}
              />
              <p className="text-sm text-muted-foreground mt-1">
                Specify the provider and model.
              </p>
            </div>
            <div>
              <Label htmlFor="llm-api-token">
                LLM API Token
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{'API token for the selected LLM provider. Can be read from env vars (e.g., `env:OPENAI_API_KEY`). Prefer setting via backend environment variables for security. (Corresponds to `LLMConfig.api_token`)'}</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Input
                id="llm-api-token"
                type="password"
                placeholder="Enter LLM API Token (or use ENV)"
                value={currentParams.llm_api_token || ""}
                onChange={(e) => handleParamChange("llm_api_token", e.target.value)}
              />
              <p className="text-sm text-muted-foreground mt-1">
                Note: For backend handling, prefer using environment variables.
              </p>
            </div>
            <div>
              <Label htmlFor="llm-base-url">
                LLM Base URL (Custom Endpoint)
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{'Optional custom base URL for self-hosted or alternative LLM API endpoints (e.g., for local Ollama or a proxy). (Corresponds to `LLMConfig.base_url`)'}</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Input
                id="llm-base-url"
                placeholder="Enter custom LLM endpoint URL (optional)"
                value={currentParams.llm_base_url || ""}
                onChange={(e) => handleParamChange("llm_base_url", e.target.value)}
              />
            </div>
          </div>
        );
      case "table":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="table-filter">
                Filter Description (Optional)
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{"Description to help identify which tables to extract (e.g., 'financial data', 'pricing table'). If empty, tries to extract all tables."}</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Input
                id="table-filter"
                placeholder="e.g., quarterly results, pricing plan"
                value={currentParams.filter || ""}
                onChange={(e) => handleParamChange("filter", e.target.value)}
              />
            </div>
          </div>
        );
      case "cosine":
      case "none":
      default:
        return (
          <p className="text-sm text-muted-foreground">
            No specific parameters required for this strategy.
          </p>
        );
    }
  };

  return (
    <TooltipProvider>
      <Card>
        <CardHeader>
          <CardTitle>Extraction Strategy Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="extraction-strategy">
              Select Strategy
              <Tooltip>
                <TooltipTrigger asChild>
                  <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>{'Choose the method `crawl4ai` will use to extract structured data. \'None\' uses default content extraction. (Corresponds to `CrawlerRunConfig.extraction_strategy`)'}</p>
                </TooltipContent>
              </Tooltip>
            </Label>
            <Select value={currentStrategy} onValueChange={handleStrategyChange}>
              <SelectTrigger id="extraction-strategy">
                <SelectValue placeholder="Select an extraction strategy" />
            </SelectTrigger>
            <SelectContent>
              {extractionStrategies.map((strategy) => (
                <SelectItem key={strategy.value} value={strategy.value}>
                  {strategy.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        {renderStrategyParams()}
        </CardContent>
      </Card>
    </TooltipProvider>
  );
};

export default React.memo(ExtractionStrategyConfigurator);