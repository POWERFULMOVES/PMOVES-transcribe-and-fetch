"use client";

import React, { useState } from 'react'; // useEffect removed if no longer needed for other purposes
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
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
import { Switch } from "@/components/ui/switch"; // Assuming a toggle for advanced options

const FetchForm = ({
  url,
  setUrl,
  fetchDepth,
  setFetchDepth,
  targetContentArea,
  setTargetContentArea,
  advancedSelector,
  setAdvancedSelector,
  fetchingEngine, // Add fetchingEngine prop
  setFetchingEngine, // Add setFetchingEngine prop
  handleFetch,
  showAdvanced,
  setShowAdvanced,
}) => {
  const handleTargetContentChange = (value) => {
    setTargetContentArea(value);
    if (value !== "advanced") {
      setAdvancedSelector(""); // Clear advanced selector if a preset is chosen
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
            <Label htmlFor="engine-standard" className="font-normal pt-0.5">Standard Fetch</Label> {/* Adjusted padding */}
          </div>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="crawl4ai" id="engine-advanced" />
            <Label htmlFor="engine-advanced" className="font-normal pt-0.5">Advanced Crawl (`crawl4ai`)</Label> {/* Adjusted padding */}
          </div>
        </RadioGroup>
      </div>

      {fetchingEngine === 'crawl4ai' && (
        <>
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