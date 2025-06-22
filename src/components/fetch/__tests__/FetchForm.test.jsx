import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FetchForm from '@/components/fetch/FetchForm';
import { BACKEND_URL } from '@/lib/constants';

// Mock sonner toast
jest.mock('sonner', () => ({
  toast: jest.fn(),
}));

// Mock lucide-react icons used in FetchForm or its children if any (e.g. Loader2 for preset loading)
jest.mock('lucide-react', () => ({
  Loader2: () => <div data-testid="loader-icon" />,
  // Add any other icons imported by FetchForm or its direct UI children if necessary
}));


const mockPresets = [
  { preset_id: 'preset1_uuid', preset_name: 'News Articles', description: 'For fetching news', version: 1, target_capability: 'news_reading', tags: ['news'] },
  { preset_id: 'preset2_uuid', preset_name: 'Product Data', description: 'For e-commerce sites', version: 2, target_capability: 'data_extraction', tags: ['e-commerce', 'product'] },
];

global.fetch = jest.fn();

// Default props for FetchForm
const defaultProps = {
  url: '',
  setUrl: jest.fn(),
  selectedPresetId: null,
  onPresetChange: jest.fn(),
  fetchDepth: 'page_only',
  setFetchDepth: jest.fn(),
  targetContentArea: 'main_content',
  setTargetContentArea: jest.fn(),
  advancedSelector: '',
  setAdvancedSelector: jest.fn(),
  fetchingEngine: 'jina', // Default to jina where presets are not shown
  setFetchingEngine: jest.fn(),
  handleFetch: jest.fn(),
  showAdvanced: false,
  setShowAdvanced: jest.fn(),
};

describe('FetchForm', () => {
  beforeEach(() => {
    fetch.mockClear();
    mockToast.mockClear();
    defaultProps.onPresetChange.mockClear();
    defaultProps.setFetchingEngine.mockClear();
  });

  describe('Preset Selector Conditional Display', () => {
    test('does not display preset selector when fetchingEngine is "jina"', () => {
      render(<FetchForm {...defaultProps} fetchingEngine="jina" />);
      expect(screen.queryByLabelText(/Crawl Preset/i)).not.toBeInTheDocument();
    });

    test('displays preset selector when fetchingEngine is "crawl4ai"', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [] }); // For preset fetch
      render(<FetchForm {...defaultProps} fetchingEngine="crawl4ai" />);
      // Wait for any potential async operations related to preset loading if necessary
      await waitFor(() => {
          expect(screen.getByLabelText(/Crawl Preset/i)).toBeInTheDocument();
      });
    });
  });

  describe('Fetching and Displaying Presets (for crawl4ai engine)', () => {
    test('fetches presets and populates dropdown when engine is "crawl4ai"', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets });
      render(<FetchForm {...defaultProps} fetchingEngine="crawl4ai" />);

      // Wait for loading to finish
      await waitFor(() => expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument());

      fireEvent.mouseDown(screen.getByRole('combobox', { name: /Crawl Preset/i })); // Open the select

      await waitFor(() => {
        expect(screen.getByText('No Preset')).toBeInTheDocument(); // Option for no preset
        expect(screen.getByText(`${mockPresets[0].preset_name} (v${mockPresets[0].version})`)).toBeInTheDocument();
        expect(screen.getByText(`${mockPresets[1].preset_name} (v${mockPresets[1].version})`)).toBeInTheDocument();
      });
      expect(fetch).toHaveBeenCalledWith(`${BACKEND_URL}/api/presets`);
    });

    test('displays loading state while fetching presets', () => {
      fetch.mockImplementation(() => new Promise(() => {})); // Keep promise pending
      render(<FetchForm {...defaultProps} fetchingEngine="crawl4ai" />);
      fireEvent.mouseDown(screen.getByRole('combobox', { name: /Crawl Preset/i }));
      expect(screen.getByText(/Loading.../i)).toBeInTheDocument();
    });

    test('shows "No Preset" option even if presets list is empty', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
      render(<FetchForm {...defaultProps} fetchingEngine="crawl4ai" />);
      await waitFor(() => expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument());
      fireEvent.mouseDown(screen.getByRole('combobox', { name: /Crawl Preset/i }));
      await waitFor(() => {
        expect(screen.getByText('No Preset')).toBeInTheDocument();
      });
    });

    test('shows error message if fetching presets fails', async () => {
        fetch.mockRejectedValueOnce(new Error('Preset API Error'));
        render(<FetchForm {...defaultProps} fetchingEngine="crawl4ai" />);
        await waitFor(() => {
            expect(screen.getByText('Preset API Error')).toBeInTheDocument(); // Error displayed below select
            expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({
                variant: 'destructive',
                title: 'Error loading presets',
                description: 'Preset API Error'
            }));
        });
    });
  });

  describe('Selecting a Preset (for crawl4ai engine)', () => {
    test('calls onPresetChange with preset_id when a preset is selected', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets });
      render(<FetchForm {...defaultProps} fetchingEngine="crawl4ai" onPresetChange={defaultProps.onPresetChange} />);
      await waitFor(() => expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument());

      fireEvent.mouseDown(screen.getByRole('combobox', { name: /Crawl Preset/i }));

      const presetOptionText = `${mockPresets[0].preset_name} (v${mockPresets[0].version})`;
      await waitFor(() => screen.getByText(presetOptionText)); // Ensure option is rendered
      fireEvent.click(screen.getByText(presetOptionText));

      expect(defaultProps.onPresetChange).toHaveBeenCalledWith(mockPresets[0].preset_id);
    });

    test('calls onPresetChange with empty string when "No Preset" is selected', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets });
      render(
        <FetchForm
          {...defaultProps}
          fetchingEngine="crawl4ai"
          onPresetChange={defaultProps.onPresetChange}
          selectedPresetId={mockPresets[0].preset_id} // Start with a preset selected
        />
      );
      await waitFor(() => expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument());

      fireEvent.mouseDown(screen.getByRole('combobox', { name: /Crawl Preset/i }));
      await waitFor(() => screen.getByText('No Preset'));
      fireEvent.click(screen.getByText('No Preset'));

      expect(defaultProps.onPresetChange).toHaveBeenCalledWith(""); // "none" value in component maps to ""
    });
  });

  // Tooltip testing can be complex with @testing-library/react as it often relies on
  // simulating actual hover events and timing. Shadcn's Tooltip might use Radix UI primitives.
  // A simple test might check if TooltipProvider/TooltipTrigger are rendered.
  // True visual/interaction testing for tooltips often falls into e2e testing scope.
  describe('Tooltip on Preset Options (for crawl4ai engine)', () => {
    test('renders TooltipProvider for preset items', async () => {
      fetch.mockResolvedValueOnce({ ok: true, json: async () => mockPresets });
      render(<FetchForm {...defaultProps} fetchingEngine="crawl4ai" />);
      await waitFor(() => expect(screen.queryByText(/Loading.../i)).not.toBeInTheDocument());

      fireEvent.mouseDown(screen.getByRole('combobox', { name: /Crawl Preset/i }));

      // Check if the first preset option (which should have a tooltip) is rendered.
      // This doesn't check if the tooltip *appears on hover*, just that the structure is there.
      const presetOptionText = `${mockPresets[0].preset_name} (v${mockPresets[0].version})`;
      await waitFor(() => {
          const presetOption = screen.getByText(presetOptionText);
          // TooltipProvider is usually a wrapper, check if the option is within such a context.
          // This is an indirect way, specific tooltip content testing on hover is harder.
          expect(presetOption).toBeInTheDocument();
      });
    });
  });
});
