import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

const PresetManager = ({
  availablePresets = [],
  isLoadingPresets = false,
  currentLoadedPreset = null,
  formIsDirty = false,
  onLoadPreset = () => {},
  onOpenSaveModal = () => {},
  onUpdatePreset = () => {},
  // Props for modal if it were part of this component, kept for reference from plan
  // newPresetNameInput = "",
  // setNewPresetNameInput = () => {},
  // newPresetDescriptionInput = "",
  // setNewPresetDescriptionInput = () => {},
  // showSavePresetModal = false,
  // onCloseSaveModal = () => {},
  // onConfirmSavePreset = () => {},
}) => {
  return (
    <div className="space-y-4 p-4 border rounded-lg mb-4">
      <h3 className="text-lg font-medium">Crawl Presets</h3>
      <div>
        <Label htmlFor="preset-select">Load Crawl Preset</Label>
        <Select
          id="preset-select"
          onValueChange={(value) => onLoadPreset(value)}
          value={currentLoadedPreset?.preset_id || ""}
          disabled={isLoadingPresets}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select a preset..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="" disabled>Select a preset...</SelectItem>
            {availablePresets.map((preset) => (
              <SelectItem key={preset.preset_id} value={preset.preset_id}>
                {preset.preset_name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex space-x-2">
        <Button onClick={onOpenSaveModal}>Save as New Preset</Button>
        <Button
          onClick={onUpdatePreset}
          disabled={!currentLoadedPreset || !formIsDirty}
        >
          Update Current Preset
        </Button>
      </div>
      <div>
        {currentLoadedPreset ? (
          <p className="text-sm text-muted-foreground">
            Current: {currentLoadedPreset.preset_name}
            {formIsDirty ? ' (modified)' : ''}
          </p>
        ) : (
          <p className="text-sm text-muted-foreground">No preset loaded.</p>
        )}
      </div>
    </div>
  );
};

export default PresetManager;
