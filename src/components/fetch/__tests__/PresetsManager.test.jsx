import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PresetsManager } from '@/components/fetch/PresetsManager'; // Assuming PresetsManager is default export

// Mock useToast
const mockToast = jest.fn();
jest.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({ toast: mockToast }),
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  PlusCircle: () => <div data-testid="plus-icon" />,
  Edit: () => <div data-testid="edit-icon" />,
  Trash2: () => <div data-testid="trash-icon" />,
  Loader2: () => <div data-testid="loader-icon" />,
}));

const mockPresets = [
  { preset_id: '1', preset_name: 'Preset 1', description: 'Desc 1', target_capability: 'web_research', tags: ['tag1'], version: 1, created_by: 'user1' },
  { preset_id: '2', preset_name: 'Preset 2', description: 'Desc 2', target_capability: 'data_extraction', tags: ['tag2', 'another'], version: 1, created_by: 'user1' },
];

global.fetch = jest.fn();

// Mock window.confirm for delete operations
global.confirm = jest.fn();

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

describe('PresetsManager', () => {
  beforeEach(() => {
    fetch.mockClear();
    mockToast.mockClear();
    confirm.mockClear();
  });

  test('displays loading state initially', () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    render(<PresetsManager />);
    expect(screen.getByText(/Loading presets.../i)).toBeInTheDocument();
  });

  test('displays presets fetched from API', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets });
    render(<PresetsManager />);
    await waitFor(() => expect(screen.getByText('Preset 1')).toBeInTheDocument());
    expect(screen.getByText('Preset 2')).toBeInTheDocument();
    expect(screen.getByText('Desc 1')).toBeInTheDocument();
    expect(screen.getByText('tag1')).toBeInTheDocument();
    expect(screen.getByText('tag2, another')).toBeInTheDocument();
  });

  test('displays empty state if no presets are available', async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    render(<PresetsManager />);
    await waitFor(() => expect(screen.getByText(/No presets found/i)).toBeInTheDocument());
  });

  test('displays error message if fetching presets fails', async () => {
    fetch.mockRejectedValueOnce(new Error('API Error'));
    render(<PresetsManager />);
    await waitFor(() => expect(screen.getByText(/Error: API Error/i)).toBeInTheDocument());
    expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive', description: 'Failed to fetch presets: API Error' }));
  });

  describe('Create Preset', () => {
    test('opens create preset dialog and submits new preset', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [] }); // Initial load
      render(<PresetsManager />);
      await waitFor(() => expect(screen.getByText(/No presets found/i)).toBeInTheDocument());

      fireEvent.click(screen.getByText(/Create New Preset/i));

      await waitFor(() => expect(screen.getByText('Create New Preset')).toBeInTheDocument()); // Dialog title

      fireEvent.change(screen.getByLabelText(/Preset Name/i), { target: { value: 'New Test Preset' } });
      fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'New Description' } });
      fireEvent.change(screen.getByLabelText(/Strategy Definition/i), { target: { value: '{"key": "value"}' } });
      fireEvent.change(screen.getByLabelText(/Tags/i), { target: { value: 'new,test' } });

      const createdPreset = { preset_id: '3', preset_name: 'New Test Preset', description: 'New Description', strategy_definition: {key: "value"}, tags: ['new', 'test'], version: 1, created_by: expect.any(String) };

      // Mock for create
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => createdPreset
      });
      // Mock for refresh list after create
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [createdPreset]
      });

      fireEvent.click(screen.getByRole('button', { name: /Create Preset/i }));

      await waitFor(() => expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ description: 'Preset created successfully.' })));
      await waitFor(() => expect(screen.getByText('New Test Preset')).toBeInTheDocument()); // Check if list refreshed
      expect(fetch).toHaveBeenCalledWith(`${BACKEND_URL}/api/presets`, expect.objectContaining({ method: 'POST' }));

      const fetchBody = JSON.parse(fetch.mock.calls.find(call => call[0].endsWith('/api/presets') && call[1]?.method === 'POST')[1].body);
      expect(fetchBody.preset_name).toBe('New Test Preset');
      expect(fetchBody.tags).toEqual(['new', 'test']);
      expect(fetchBody.strategy_definition).toEqual({key: "value"});
      expect(fetchBody.created_by).toBe("00000000-0000-0000-0000-000000000000"); // Placeholder user ID
    });

    test('shows error if create preset fails', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [] }); // Initial load
      render(<PresetsManager />);
      fireEvent.click(screen.getByText(/Create New Preset/i));
      await waitFor(() => screen.getByLabelText(/Preset Name/i));

      fireEvent.change(screen.getByLabelText(/Preset Name/i), { target: { value: 'Fail Preset' } });
      fireEvent.change(screen.getByLabelText(/Strategy Definition/i), { target: { value: '{"key": "value"}' } });


      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Create failed' }),
        status: 400
      });

      fireEvent.click(screen.getByRole('button', { name: /Create Preset/i }));

      await waitFor(() => expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive', description: 'Failed to save preset: Create failed' })));
    });

    test('validates required fields on create', async () => {
        fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
        render(<PresetsManager />);
        fireEvent.click(screen.getByText(/Create New Preset/i));
        await waitFor(() => screen.getByRole('button', { name: /Create Preset/i }));

        fireEvent.click(screen.getByRole('button', { name: /Create Preset/i })); // Submit with empty form
        // Check for HTML5 validation or specific error messages if implemented
        // For now, we assume browser validation or specific error handling for empty required fields.
        // If strategy_definition is invalid JSON:
        fireEvent.change(screen.getByLabelText(/Strategy Definition/i), { target: { value: 'invalid json' } });
        fireEvent.click(screen.getByRole('button', { name: /Create Preset/i }));
        await waitFor(() => expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ title: "Validation Error", description: "Strategy Definition must be valid JSON." })));
    });
  });

  describe('Edit Preset', () => {
    test('populates form with preset data and submits update', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets }); // Initial load
      render(<PresetsManager />);
      await waitFor(() => expect(screen.getByText('Preset 1')).toBeInTheDocument());

      // Find edit button for Preset 1. Assuming each row has an identifiable structure.
      // This might need data-testid on buttons if a more robust selector is needed.
      const editButtons = screen.getAllByTestId('edit-icon');
      fireEvent.click(editButtons[0].closest('button')); // Click edit for Preset 1

      await waitFor(() => expect(screen.getByDisplayValue('Preset 1')).toBeInTheDocument());
      expect(screen.getByDisplayValue('Desc 1')).toBeInTheDocument();
      expect(screen.getByDisplayValue('tag1')).toBeInTheDocument(); // Tags are formatted as string
      expect(screen.getByDisplayValue(JSON.stringify(mockPresets[0].strategy_definition, null, 2))).toBeInTheDocument();

      fireEvent.change(screen.getByLabelText(/Description/i), { target: { value: 'Updated Desc 1' } });

      const updatedPreset = { ...mockPresets[0], description: 'Updated Desc 1' };
      fetch.mockResolvedValueOnce({ ok: true, json: async () => updatedPreset }); // Mock for PUT
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [updatedPreset, mockPresets[1]] }); // Mock for refresh

      fireEvent.click(screen.getByRole('button', { name: /Save Changes/i }));

      await waitFor(() => expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ description: 'Preset updated successfully.' })));
      await waitFor(() => expect(screen.getByText('Updated Desc 1')).toBeInTheDocument());
      expect(fetch).toHaveBeenCalledWith(`${BACKEND_URL}/api/presets/${mockPresets[0].preset_id}`, expect.objectContaining({ method: 'PUT' }));
      const fetchBody = JSON.parse(fetch.mock.calls.find(call => call[0].includes(mockPresets[0].preset_id) && call[1]?.method === 'PUT')[1].body);
      expect(fetchBody.description).toBe('Updated Desc 1');
    });
  });

  describe('Delete Preset', () => {
    test('deletes a preset after confirmation', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets }); // Initial load
      render(<PresetsManager />);
      await waitFor(() => expect(screen.getByText('Preset 1')).toBeInTheDocument());

      confirm.mockReturnValueOnce(true); // Simulate user confirming deletion

      const deleteButtons = screen.getAllByTestId('trash-icon');
      fireEvent.click(deleteButtons[0].closest('button')); // Click delete for Preset 1

      fetch.mockResolvedValueOnce({ ok: true, status: 204 }); // Mock for DELETE
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [mockPresets[1]] }); // Mock for refresh (Preset 1 removed)

      await waitFor(() => expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ description: 'Preset deleted successfully.' })));
      await waitFor(() => expect(screen.queryByText('Preset 1')).not.toBeInTheDocument());
      expect(screen.getByText('Preset 2')).toBeInTheDocument(); // Preset 2 should still be there
      expect(fetch).toHaveBeenCalledWith(`${BACKEND_URL}/api/presets/${mockPresets[0].preset_id}`, expect.objectContaining({ method: 'DELETE' }));
    });

    test('does not delete if confirmation is cancelled', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets });
      render(<PresetsManager />);
      await waitFor(() => screen.getByText('Preset 1'));

      confirm.mockReturnValueOnce(false); // Simulate user cancelling deletion
      const deleteButtons = screen.getAllByTestId('trash-icon');
      fireEvent.click(deleteButtons[0].closest('button'));

      expect(fetch.mock.calls.filter(call => call[1]?.method === 'DELETE').length).toBe(0); // No DELETE call
      expect(mockToast).not.toHaveBeenCalledWith(expect.objectContaining({ description: 'Preset deleted successfully.' }));
      expect(screen.getByText('Preset 1')).toBeInTheDocument(); // Preset 1 still there
    });

    test('shows error if delete preset fails', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets });
      render(<PresetsManager />);
      await waitFor(() => screen.getByText('Preset 1'));

      confirm.mockReturnValueOnce(true);
      const deleteButtons = screen.getAllByTestId('trash-icon');
      fireEvent.click(deleteButtons[0].closest('button'));

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Delete failed' })
      });

      await waitFor(() => expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive', description: 'Failed to delete preset: Delete failed' })));
      expect(screen.getByText('Preset 1')).toBeInTheDocument(); // Preset 1 still there because delete failed
    });
  });
});

// A simple polyfill for TextEncoder/TextDecoder if needed for JSDOM, though usually not required for basic tests
// if (!global.TextEncoder) {
//   global.TextEncoder = require('util').TextEncoder;
// }
// if (!global.TextDecoder) {
//   global.TextDecoder = require('util').TextDecoder;
// }
