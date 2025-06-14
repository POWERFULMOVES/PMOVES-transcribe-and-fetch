// src/components/fetch/PresetSelector.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '@/utils/apiClient'; // Assuming apiClient is set up for this

const PresetSelector = ({ onPresetSelect, selectedPresetId }) => {
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPresets = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/api/presets'); // Corrected path
        setPresets(response.data || []); // Assuming response.data is an array of presets
        setError(null);
      } catch (err) {
        console.error("Error fetching presets:", err);
        setError('Failed to load presets.');
        setPresets([]); // Clear presets on error
      } finally {
        setLoading(false);
      }
    };

    fetchPresets();
  }, []);

  const handleChange = (event) => {
    const presetId = event.target.value;
    const selected = presets.find(p => p.preset_id.toString() === presetId); // Changed p.id to p.preset_id
    if (selected) {
      onPresetSelect(selected);
    } else if (presetId === "") {
      onPresetSelect(null); // Allow deselecting to no preset
    }
  };

  if (loading) {
    return <p>Loading presets...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  return (
    <div>
      <label htmlFor="preset-selector">Select a Crawl Preset:</label>
      <select 
        id="preset-selector" 
        value={selectedPresetId || ""} 
        onChange={handleChange}
        style={{ marginLeft: '10px', padding: '5px' }}
      >
        <option value="">-- Select a Preset --</option>
        {presets.map(preset => (
          <option key={preset.preset_id} value={preset.preset_id}> {/* Changed preset.id to preset.preset_id */}
            {preset.preset_name} {/* Changed preset.name to preset.preset_name */}
          </option>
        ))}
      </select>
    </div>
  );
};

export default PresetSelector;
