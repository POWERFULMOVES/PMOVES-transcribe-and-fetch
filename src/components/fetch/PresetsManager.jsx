"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger, DialogClose } from "@/components/ui/dialog"; // Assuming Dialog exists
import { toast } from "sonner";
import { PlusCircle, Edit, Trash2, Loader2 } from 'lucide-react';
import { BACKEND_URL } from '@/lib/constants';

const initialFormState = {
  preset_name: "",
  description: "",
  strategy_definition: "{\n  \"example_key\": \"example_value\"\n}",
  target_capability: "",
  tags: "", // Comma-separated string
  version: 1,
};

// Helper functions
const parseTagsString = (tagsStr) => {
  if (!tagsStr || typeof tagsStr !== 'string') return [];
  return tagsStr.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
};

const formatTagsArray = (tagsArr) => {
  if (!tagsArr || !Array.isArray(tagsArr)) return "";
  return tagsArr.join(', ');
};

export default function PresetsManager() {
  const [presetsList, setPresetsList] = useState([]);
  const [isLoadingPresets, setIsLoadingPresets] = useState(true);
  const [errorPresets, setErrorPresets] = useState("");
  const [showPresetForm, setShowPresetForm] = useState(false);
  const [currentEditingPreset, setCurrentEditingPreset] = useState(null);
  const [presetFormState, setPresetFormState] = useState(initialFormState);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // toast from sonner will be used for notifications


  const fetchPresets = useCallback(async () => {
    setIsLoadingPresets(true);
    setErrorPresets("");
    try {
      const response = await fetch(`${BACKEND_URL}/api/presets`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to fetch presets" }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setPresetsList(data);
    } catch (error) {
      console.error("Error fetching presets:", error);
      setErrorPresets(error.message);
      toast.error(`Failed to fetch presets: ${error.message}`);
    } finally {
      setIsLoadingPresets(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchPresets();
  }, [fetchPresets]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPresetFormState(prevState => ({ ...prevState, [name]: value }));
  };

  const handleOpenCreateForm = () => {
    setCurrentEditingPreset(null);
    setPresetFormState(initialFormState);
    setShowPresetForm(true);
  };

  const handleOpenEditForm = (preset) => {
    setCurrentEditingPreset(preset);
    setPresetFormState({
      preset_id: preset.preset_id,
      preset_name: preset.preset_name,
      description: preset.description || "",
      strategy_definition: typeof preset.strategy_definition === 'string' ? preset.strategy_definition : JSON.stringify(preset.strategy_definition, null, 2),
      target_capability: preset.target_capability || "",
      tags: formatTagsArray(preset.tags),
      version: preset.version,
      created_by: preset.created_by // Keep created_by if needed, though not directly editable by user
    });
    setShowPresetForm(true);
  };

  const handleSavePreset = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorPresets("");

    let strategyDefinitionParsed;
    try {
      strategyDefinitionParsed = JSON.parse(presetFormState.strategy_definition);
    } catch (jsonError) {
      setErrorPresets("Strategy Definition is not valid JSON.");
      toast.error("Strategy Definition must be valid JSON.");
      setIsSubmitting(false);
      return;
    }

    // Ensure created_by is included for new presets. For this example, we'll use a placeholder UUID.
    // In a real app, this would come from the authenticated user's session/context.
    const placeholderUserId = "00000000-0000-0000-0000-000000000000";


    const payload = {
      ...presetFormState,
      tags: parseTagsString(presetFormState.tags),
      strategy_definition: strategyDefinitionParsed, // Send parsed JSON object
      // version might be handled by backend, but we send what's in form
    };

    // Add created_by only for new presets, if not already in formState from editing
    if (!currentEditingPreset && !payload.created_by) {
        payload.created_by = placeholderUserId;
    } else if (currentEditingPreset) {
        payload.created_by = currentEditingPreset.created_by; // Preserve original creator on update
    }


    const url = currentEditingPreset
      ? `${BACKEND_URL}/api/presets/${currentEditingPreset.preset_id}`
      : `${BACKEND_URL}/api/presets`;
    const method = currentEditingPreset ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Failed to save preset" }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      // const savedPreset = await response.json(); // Optional: use savedPreset data
      toast.success(`Preset ${currentEditingPreset ? 'updated' : 'created'} successfully.`);
      setShowPresetForm(false);
      fetchPresets(); // Refresh list
    } catch (error) {
      console.error("Error saving preset:", error);
      setErrorPresets(error.message);
      toast.error(`Failed to save preset: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeletePreset = async (presetId) => {
    if (!window.confirm("Are you sure you want to delete this preset?")) return;
    setIsSubmitting(true); // Use for disabling delete buttons too
    setErrorPresets("");
    try {
      const response = await fetch(`${BACKEND_URL}/api/presets/${presetId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        // For DELETE, response might not have JSON body on error (e.g. 404)
        // Or if it does, try to parse it.
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
            const errorData = await response.json();
            errorDetail = errorData.detail || errorDetail;
        } catch (e) { /* ignore parsing error if no body */ }
        throw new Error(errorDetail);
      }
      toast.success("Preset deleted successfully.");
      fetchPresets(); // Refresh list
    } catch (error) {
      console.error("Error deleting preset:", error);
      setErrorPresets(error.message);
      toast.error(`Failed to delete preset: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Manage Crawl Presets</CardTitle>
        <CardDescription>Create, edit, and delete your crawl configurations.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-end mb-4">
          <Button onClick={handleOpenCreateForm}>
            <PlusCircle className="mr-2 h-4 w-4" /> Create New Preset
          </Button>
        </div>

        {isLoadingPresets && (
          <div className="flex justify-center items-center py-10">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="ml-2">Loading presets...</p>
          </div>
        )}
        {!isLoadingPresets && errorPresets && (
          <div className="text-red-500 text-center py-4">
            <p>Error: {errorPresets}</p>
            <Button onClick={fetchPresets} variant="outline" className="mt-2">Try Again</Button>
          </div>
        )}
        {!isLoadingPresets && !errorPresets && presetsList.length === 0 && (
          <p className="text-center text-gray-500 py-4">No presets found. Get started by creating one!</p>
        )}
        {!isLoadingPresets && !errorPresets && presetsList.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Capability</TableHead>
                <TableHead>Tags</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {presetsList.map((preset) => (
                <TableRow key={preset.preset_id}>
                  <TableCell className="font-medium">{preset.preset_name}</TableCell>
                  <TableCell className="text-sm text-muted-foreground truncate max-w-xs">{preset.description}</TableCell>
                  <TableCell>{preset.target_capability}</TableCell>
                  <TableCell>{formatTagsArray(preset.tags)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" onClick={() => handleOpenEditForm(preset)} className="mr-2">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDeletePreset(preset.preset_id)} disabled={isSubmitting}>
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <Dialog open={showPresetForm} onOpenChange={setShowPresetForm}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>{currentEditingPreset ? 'Edit Preset' : 'Create New Preset'}</DialogTitle>
            <DialogDescription>
              {currentEditingPreset ? 'Modify the details of your existing preset.' : 'Define a new crawl preset for your tasks.'}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSavePreset}>
            <div className="grid gap-4 py-4">
              <div>
                <label htmlFor="preset_name" className="block text-sm font-medium mb-1">Preset Name*</label>
                <Input
                  id="preset_name"
                  name="preset_name"
                  value={presetFormState.preset_name}
                  onChange={handleInputChange}
                  placeholder="e.g., My News Crawler"
                  required
                />
              </div>
              <div>
                <label htmlFor="description" className="block text-sm font-medium mb-1">Description</label>
                <Textarea
                  id="description"
                  name="description"
                  value={presetFormState.description}
                  onChange={handleInputChange}
                  placeholder="A brief summary of what this preset does"
                />
              </div>
              <div>
                <label htmlFor="target_capability" className="block text-sm font-medium mb-1">Target Capability</label>
                <Input
                  id="target_capability"
                  name="target_capability"
                  value={presetFormState.target_capability}
                  onChange={handleInputChange}
                  placeholder="e.g., web_research, data_extraction"
                />
              </div>
              <div>
                <label htmlFor="tags" className="block text-sm font-medium mb-1">Tags (comma-separated)</label>
                <Input
                  id="tags"
                  name="tags"
                  value={presetFormState.tags}
                  onChange={handleInputChange}
                  placeholder="e.g., news, finance, tech"
                />
              </div>
              <div>
                <label htmlFor="strategy_definition" className="block text-sm font-medium mb-1">Strategy Definition (JSON)*</label>
                <Textarea
                  id="strategy_definition"
                  name="strategy_definition"
                  value={presetFormState.strategy_definition}
                  onChange={handleInputChange}
                  rows={8}
                  placeholder='e.g., { "type": "depth_first", "depth": 3 }'
                  required
                />
                <p className="text-xs text-muted-foreground mt-1">Enter the crawl strategy parameters as a valid JSON object.</p>
              </div>
               {currentEditingPreset && presetFormState.version && (
                <div>
                  <label className="block text-sm font-medium mb-1">Version</label>
                  <Input value={presetFormState.version} readOnly disabled />
                </div>
              )}
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="outline">Cancel</Button>
              </DialogClose>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {currentEditingPreset ? 'Save Changes' : 'Create Preset'}
              </Button>
            </DialogFooter>
          </form>
          {errorPresets && <p className="text-red-500 text-sm mt-2 text-center">{errorPresets}</p>}
        </DialogContent>
      </Dialog>
    </Card>
  );
}
