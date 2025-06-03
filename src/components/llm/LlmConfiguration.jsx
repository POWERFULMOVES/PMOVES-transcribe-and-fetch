"use client";

import React from 'react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { InfoCircledIcon } from '@radix-ui/react-icons';

const LlmConfiguration = ({
  llmProvider, // Selected model's crawl4ai_compatible_id or model_id
  setLlmProvider, // Handler to update the selected model ID
  llmApiToken,
  setLlmApiToken,
  llmBaseUrl,
  setLlmBaseUrl,
  availableLlmModels, // List of available LLM models from the backend
  isLoadingLlmModels, // Boolean indicating if models are currently being loaded
  // Props for Crawl4AI specific LLM-related Markdown generator (optional)
  showCrawl4aiMarkdownGenerator = false, // Control visibility based on context
  crawl4aiMarkdownGenerator,
  setCrawl4aiMarkdownGenerator,
}) => {
  return (
    <TooltipProvider>
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
          <div>
            <Label htmlFor="llm-provider">
              LLM Provider/Model
              <Tooltip>
                <TooltipTrigger asChild>
                  <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Select a registered LLM. List is dynamically loaded from the backend. This model may be used for various LLM-powered features within the selected fetching engine (e.g., LLM-based extraction, image captioning with Crawl4AI).</p>
                </TooltipContent>
              </Tooltip>
            </Label>
            <Select value={llmProvider} onValueChange={setLlmProvider}>
              <SelectTrigger id="llm-provider">
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {isLoadingLlmModels ? (
                  <SelectItem value="loading-true" disabled>
                    Loading models...
                  </SelectItem>
                ) : availableLlmModels && availableLlmModels.length > 0 ? (
                  availableLlmModels.map((model) => (
                    <SelectItem 
                      key={model.model_id || model.id} 
                      value={model.model_id || model.id}
                    >
                      {model.display_name || model.name || model.model_id || model.id} {model.provider && `(${model.provider})`}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="no-models" disabled>
                    No models available or failed to load.
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground mt-1">
              Choose an LLM for tasks like content extraction or analysis.
            </p>
          </div>

          <div>
            <Label htmlFor="llm-api-token">
              LLM API Token/Key
              <Tooltip>
                <TooltipTrigger asChild>
                  <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Enter the API token if the selected provider requires one and it's not set globally on the backend. For self-hosted models like Ollama, this might not be needed. It is generally recommended to configure API keys on the backend via environment variables for security.</p>
                </TooltipContent>
              </Tooltip>
            </Label>
            <Input 
              id="llm-api-token" 
              type="password" 
              value={llmApiToken || ""} 
              onChange={(e) => setLlmApiToken(e.target.value)} 
              placeholder="Optional: Enter API token if needed"
            />
          </div>

          <div>
            <Label htmlFor="llm-base-url">
              LLM Base URL (Optional)
              <Tooltip>
                <TooltipTrigger asChild>
                  <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Specify a custom base URL for the LLM API, e.g., for local Ollama (http://localhost:11434) or a proxy. If empty, the default URL for the provider will be used (if known by the backend).</p>
                </TooltipContent>
              </Tooltip>
            </Label>
            <Input 
              id="llm-base-url" 
              value={llmBaseUrl || ""} 
              onChange={(e) => setLlmBaseUrl(e.target.value)} 
              placeholder="e.g., http://localhost:11434"
            />
             <p className="text-xs text-muted-foreground mt-1">
              Needed for local models (like Ollama) or custom API endpoints.
            </p>
          </div>

          {showCrawl4aiMarkdownGenerator && (
            <div>
              <Label htmlFor="crawl4ai-markdown-generator">
                Markdown Generator (Crawl4AI)
                <Tooltip>
                  <TooltipTrigger asChild>
                    <InfoCircledIcon className="inline-block ml-1 h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Choose how Crawl4AI generates the final Markdown output. 'LLM' option uses the selected LLM Provider/Model above for generation (experimental and may incur costs).</p>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <Select value={crawl4aiMarkdownGenerator || 'Default'} onValueChange={setCrawl4aiMarkdownGenerator}>
                <SelectTrigger id="crawl4ai-markdown-generator">
                  <SelectValue placeholder="Select Markdown Generator" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Default">Default (Rule-based)</SelectItem>
                  <SelectItem value="Newspaper3k">Newspaper3k</SelectItem>
                  <SelectItem value="Readability">Readability</SelectItem>
                  <SelectItem value="LLM">LLM (Uses selected model)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>
    </TooltipProvider>
  );
};

export default LlmConfiguration; 