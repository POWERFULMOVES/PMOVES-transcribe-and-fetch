"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast"; // Or from "@/hooks/use-toast"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Label } from "@/components/ui/label";
// Duplicate Label import removed
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Loader2 } from 'lucide-react'; // For loading indicator

import { BACKEND_URL } from '@/lib/constants';

const FetchForm = ({
  url,
  setUrl,
  // Props for preset selection
  selectedPresetId, // New prop to receive current selection from parent
  onPresetChange,   // New prop to notify parent of selection change
  fetchDepth,
  setFetchDepth,
  targetContentArea,
  setTargetContentArea,
  advancedSelector,
  setAdvancedSelector,
  fetchingEngine,
  setFetchingEngine,
  handleFetch,
  showAdvanced,
  setShowAdvanced,
}) => {
  const [availablePresets, setAvailablePresets] = useState([]);
  const [isLoadingPresets, setIsLoadingPresets] = useState(false);
  const [errorPresets, setErrorPresets] = useState(null);
  const { toast } = useToast();

  const fetchAvailablePresets = useCallback(async () => {
    if (fetchingEngine !== 'crawl4ai') {
      setAvailablePresets([]); // Clear presets if not using crawl4ai
      return;
    }
    setIsLoadingPresets(true);
    setErrorPresets(null);
    try {
      const response = await fetch(`${BACKEND_URL}/api/presets`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch presets" }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAvailablePresets(data || []);
    } catch (error) {
      console.error("Error fetching presets:", error);
      setErrorPresets(error.message);
      toast({
        title: "Error loading presets",
        description: error.message,
        variant: "destructive",
      });
      setAvailablePresets([]);
    } finally {
      setIsLoadingPresets(false);
    }
  }, [fetchingEngine, toast]);

  useEffect(() => {
    fetchAvailablePresets();
  }, [fetchAvailablePresets]);

  const handleLocalPresetChange = (presetId) => {
    onPresetChange(presetId === "none" ? "" : presetId); // Notify parent. "none" value maps to empty string.
  };

  const handleTargetContentChange = (value) => {
    setTargetContentArea(value);
    if (value !== "advanced") {
      setAdvancedSelector("");
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="url-input">Target URL</Label>
        <Input
          id="url-input"
          type="url"
          placeholder="https://example.com"
          value={url} // Use url prop directly
          onChange={(e) => setUrl(e.target.value)} // Call setUrl prop
          className="w-full"
        />
      </div>

      <div>
        <Label htmlFor="fetching-engine-select">Fetching Engine</Label>
        <RadioGroup
          value={fetchingEngine} // Use prop directly
          onValueChange={setFetchingEngine} // Call prop directly
          className="mt-2 space-y-2"
        >
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="jina" id="engine-standard" />
            <Label htmlFor="engine-standard" className="font-normal pt-0.5">Standard Fetch</Label>
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="crawl4ai" id="engine-advanced" />
            <Label htmlFor="engine-advanced" className="font-normal pt-0.5">Advanced Crawl (`crawl4ai`)</Label>
          </div>
        </RadioGroup>
      </div>

      {fetchingEngine === 'crawl4ai' && (
        <>
          <div>
            <Label htmlFor="crawl-preset-select">Crawl Preset (Optional)</Label>
            <Select value={selectedPresetId || "none"} onValueChange={handleLocalPresetChange} disabled={isLoadingPresets}>
              <SelectTrigger id="crawl-preset-select" className="w-full">
                <SelectValue placeholder="No Preset" />
              </SelectTrigger>
              <SelectContent>
                {isLoadingPresets ? (
                  <div className="flex items-center justify-center p-2">
                    <Loader2 className="h-4 w-4 animate-spin mr-2" /> Loading...
                  </div>
                ) : (
                  <>
                    <SelectItem value="none">No Preset</SelectItem>
                    {availablePresets.map((preset) => (
                      <SelectItem key={preset.preset_id} value={preset.preset_id}>
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <span>{preset.preset_name} (v{preset.version})</span>
                            </TooltipTrigger>
                            <TooltipContent side="right" className="max-w-xs">
                              <p className="font-bold mb-1">{preset.preset_name}</p>
                              <p className="text-xs text-muted-foreground mb-1">Capability: {preset.target_capability || 'N/A'}</p>
                              <p className="text-xs">{preset.description || "No description."}</p>
                              {preset.tags && preset.tags.length > 0 && (
                                <p className="text-xs mt-1">Tags: {preset.tags.join(', ')}</p>
                              )}
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      </SelectItem>
                    ))}
                  </>
                )}
              </SelectContent>
            </Select>
            {errorPresets && <p className="text-xs text-destructive mt-1">{errorPresets}</p>}
          </div>

          <div>
            <Label htmlFor="fetch-depth-select">Fetch Depth</Label>
            <Select value={fetchDepth} onValueChange={setFetchDepth}>
              <SelectTrigger id="fetch-depth-select" className="w-full">
                <SelectValue placeholder="Select fetch depth" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="page_only">This page only</SelectItem>
                <SelectItem value="level_1">1 level deep</SelectItem>
                <SelectItem value="level_2">2 levels deep</SelectItem>
                {/* Add more options as needed */}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="target-content-select">Target Content Area</Label>
            <Select value={targetContentArea} onValueChange={handleTargetContentChange}>
              <SelectTrigger id="target-content-select" className="w-full">
                <SelectValue placeholder="Select target area" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="main_content">Main Article/Content</SelectItem>
                <SelectItem value="full_page">Full Page</SelectItem>
                <SelectItem value="advanced">Advanced Selector</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {targetContentArea === "advanced" && (
            <div>
              <Label htmlFor="advanced-selector-input">Advanced Content Selector (CSS/XPath)</Label>
              <Input
                id="advanced-selector-input"
                type="text"
                placeholder="e.g., #main-content .article-body"
                value={advancedSelector}
                onChange={(e) => setAdvancedSelector(e.target.value)}
                className="w-full"
              />
            </div>
          )}
        </>
      )}

      <Button onClick={handleFetch} className="w-full mt-2"> {/* Added mt-2 */}
        Fetch Content
      </Button>

      <div className="flex items-center space-x-2 mt-4">
        <Switch
          id="advanced-options-toggle"
          checked={showAdvanced}
          onCheckedChange={setShowAdvanced}
        />
        <Label htmlFor="advanced-options-toggle">Show Advanced Options</Label>
      </div>
    </div>
  );
};

export default FetchForm;