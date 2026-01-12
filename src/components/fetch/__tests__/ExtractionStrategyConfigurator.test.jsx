import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ExtractionStrategyConfigurator from '../ExtractionStrategyConfigurator';
import { TooltipProvider } from '@/components/ui/tooltip';

// Mock the UI Select component (Radix/ShadCN)
jest.mock('@/components/ui/select', () => ({
  Select: ({ value, onValueChange, children }) => (
    <div data-testid="select-container">
        <select
          data-testid="strategy-select"
          value={value}
          onChange={(e) => onValueChange(e.target.value)}
        >
          {children}
        </select>
    </div>
  ),
  SelectTrigger: ({ children }) => null, // Do not render trigger in select
  SelectValue: ({ children }) => null, // Do not render value
  SelectContent: ({ children }) => <>{children}</>, // Render options directly
  SelectItem: ({ value, children }) => <option value={value}>{children}</option>,
  SelectGroup: ({ children }) => <>{children}</>,
  SelectLabel: ({ children }) => <optgroup label={children} />,
}));

// Helper to render with required providers and state management
const renderWithProvider = (ui, initialConfig = { strategy: 'none', params: {} }, onConfigChange = jest.fn()) => {
  const Wrapper = () => {
    const [config, setConfig] = React.useState(initialConfig);
    const handleChange = (newConfig) => {
      setConfig(newConfig);
      onConfigChange(newConfig);
    };
    // return cloneElement(ui, { onConfigChange: handleChange, initialConfig: config });
    // Better to render component directly
    return (
        <TooltipProvider>
            <ExtractionStrategyConfigurator onConfigChange={handleChange} initialConfig={config} />
        </TooltipProvider>
    );
  };
  return render(<Wrapper />);
};

describe('ExtractionStrategyConfigurator with Mocked Select', () => {
  let mockOnConfigChange;

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
    jest.clearAllMocks();
  });

  describe('Default Strategy State', () => {
    test('renders with default strategy "none" when initialConfig is default', () => {
        renderWithProvider(<ExtractionStrategyConfigurator initialConfig={{ strategy: 'none', params: {} }} onConfigChange={mockOnConfigChange} />);
        expect(screen.getByText(/No specific parameters required for this strategy/i)).toBeVisible();
        // Should NOT call callback just for rendering
        expect(mockOnConfigChange).not.toHaveBeenCalled();
    });
  });

  describe('Strategy Selection', () => {
    test('selecting "LLMExtractionStrategy" displays inputs', async () => {
        const user = userEvent.setup();
        renderWithProvider(null, { strategy: 'none', params: {} }, mockOnConfigChange);
        
        // Initial call
        // expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'none', params: {} }); 
        // Wrapper init calls callback? No. Only change.
        mockOnConfigChange.mockClear();

        // Select LLM
        fireEvent.change(screen.getByTestId('strategy-select'), { target: { value: 'llm' } });

        // Should see inputs
        expect(await screen.findByLabelText(/LLM Instructions/i)).toBeVisible();
        expect(screen.getByLabelText(/LLM Provider\/Model/i)).toBeVisible();
        expect(screen.getByLabelText(/LLM API Token/i)).toBeVisible();

        // Verify callback
        expect(mockOnConfigChange).toHaveBeenCalledWith(expect.objectContaining({ strategy: 'llm' }));
    });

    test('selecting "JsonCssExtractionStrategy" displays schema input', async () => {
        renderWithProvider(null, { strategy: 'none', params: {} }, mockOnConfigChange);
        mockOnConfigChange.mockClear();

        fireEvent.change(screen.getByTestId('strategy-select'), { target: { value: 'json_css' } });

        expect(await screen.findByLabelText(/Schema \(JSON\)/i)).toBeVisible();
        expect(mockOnConfigChange).toHaveBeenCalledWith(expect.objectContaining({ strategy: 'json_css' }));
    });

    test('selecting "CosineStrategy" displays no params', async () => {
        renderWithProvider(null, { strategy: 'none', params: {} }, mockOnConfigChange);
        mockOnConfigChange.mockClear();

        fireEvent.change(screen.getByTestId('strategy-select'), { target: { value: 'cosine' } });

        expect(await screen.findByText(/No specific parameters required/i)).toBeVisible();
        expect(mockOnConfigChange).toHaveBeenCalledWith(expect.objectContaining({ strategy: 'cosine' }));
    });

    test('selecting "Table Extraction" displays filter input', async () => {
        renderWithProvider(null, { strategy: 'none', params: {} }, mockOnConfigChange);
        mockOnConfigChange.mockClear();

        fireEvent.change(screen.getByTestId('strategy-select'), { target: { value: 'table' } });

        expect(await screen.findByLabelText(/Filter Description/i)).toBeVisible();
        expect(mockOnConfigChange).toHaveBeenCalledWith(expect.objectContaining({ strategy: 'table' }));
    });
  });

  describe('Parameter Inputs', () => {
      test('updating LLM params calls onConfigChange', async () => {
          const user = userEvent.setup();
          renderWithProvider(null, { strategy: 'none', params: {} }, mockOnConfigChange);
          
          // Select LLM
          fireEvent.change(screen.getByTestId('strategy-select'), { target: { value: 'llm' } });
          mockOnConfigChange.mockClear();

          // Update Instructions
          const instructionsInput = await screen.findByLabelText(/LLM Instructions/i);
          await user.type(instructionsInput, 'New Prompt');

          // Check if callback called with updated params
          expect(mockOnConfigChange).toHaveBeenLastCalledWith(expect.objectContaining({
              strategy: 'llm',
              params: expect.objectContaining({ llm_instructions: 'New Prompt' })
          }));

          // Update Provider
          const providerInput = screen.getByLabelText(/LLM Provider\/Model/i);
          await user.clear(providerInput);
          await user.type(providerInput, 'openai/gpt-4');
          
          expect(mockOnConfigChange).toHaveBeenLastCalledWith(expect.objectContaining({
            params: expect.objectContaining({ llm_provider_model: 'openai/gpt-4' })
          }));
      });

      test('updating JsonCss schema calls onConfigChange', async () => {
        const user = userEvent.setup();
        renderWithProvider(null, { strategy: 'none', params: {} }, mockOnConfigChange);
        
        fireEvent.change(screen.getByTestId('strategy-select'), { target: { value: 'json_css' } });
        mockOnConfigChange.mockClear();

        const schemaInput = await screen.findByLabelText(/Schema \(JSON\)/i);
        // await user.type(schemaInput, '{foo}');
        fireEvent.change(schemaInput, { target: { value: '{foo}' } });

        expect(mockOnConfigChange).toHaveBeenLastCalledWith(expect.objectContaining({
            strategy: 'json_css',
            params: expect.objectContaining({ schema: '{foo}' })
        }));
      });
  });
});