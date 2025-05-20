import React from 'react';
import { render, screen, rerender, within } from '@testing-library/react'; // Added 'within'
import userEvent from '@testing-library/user-event';
import ExtractionStrategyConfigurator from '../ExtractionStrategyConfigurator';
import { TooltipProvider } from 'components/ui/tooltip'; // Assuming jsconfig.json resolves this from src/

// We don't need to import Label, Select etc. here if they are correctly encapsulated
// within ExtractionStrategyConfigurator and it renders the necessary ARIA roles and text.
// If ExtractionStrategyConfigurator itself is responsible for rendering the Label and Select structure
// that results in `getByRole('combobox', { name: /Select Strategy/i })` finding the element
// and `toHaveTextContent` working, then direct imports here are not strictly needed for the test file itself,
// as long as Jest can resolve them for the component being tested.

const mockOnConfigChangeGlobal = jest.fn(); // Renamed to avoid conflict if any test uses it globally

describe('ExtractionStrategyConfigurator - Default Strategy State', () => {
  let mockOnConfigChange; // Local to this describe block

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('Test Case 1: initialConfig prop is not provided', () => {
    render(
      <TooltipProvider>
        <ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />
      </TooltipProvider>
    );
    
    // The component should display "None / Default" in its strategy selector
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('None / Default');
    
    // onConfigChange should be called once with the default 'none' strategy
    expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'none', params: {} });
  });

  test('Test Case 2: initialConfig prop is provided but initialConfig.strategy is undefined', () => {
    const initialConfigUndefined = { strategy: undefined, params: { customParam: 'value1' } };
    render(
      <TooltipProvider>
        <ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigUndefined} />
      </TooltipProvider>
    );
    
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('None / Default');
    
    // As per analysis, onConfigChange might be called twice:
    // 1. With the initial (undefined) strategy.
    // 2. After the useEffect normalizes the strategy to 'none'.
    expect(mockOnConfigChange).toHaveBeenCalledTimes(2); 
    expect(mockOnConfigChange).toHaveBeenNthCalledWith(1, { strategy: undefined, params: { customParam: 'value1' } });
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'none', params: { customParam: 'value1' } });
  });

  test('Test Case 3: initialConfig prop is provided but initialConfig.strategy is null', () => {
    const initialConfigNull = { strategy: null, params: { anotherParam: 'value2' } };
    render(
      <TooltipProvider>
        <ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigNull} />
      </TooltipProvider>
    );
    
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('None / Default');
    
    // Similar to the 'undefined' case, two calls are expected.
    expect(mockOnConfigChange).toHaveBeenCalledTimes(2);
    expect(mockOnConfigChange).toHaveBeenNthCalledWith(1, { strategy: null, params: { anotherParam: 'value2' } });
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'none', params: { anotherParam: 'value2' } });
  });
});

// Helper function for rendering with TooltipProvider for the new test suite
const renderWithProvider = (ui, options) => {
  return render(<TooltipProvider>{ui}</TooltipProvider>, options);
};

describe('ExtractionStrategyConfigurator - Strategy Selection, Parameters, and Callbacks', () => {
  let mockOnConfigChange;

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks(); // Clear mocks after each test in this suite too
  });

  // Test Case 1: "None / Default" Strategy
  test('selecting "None / Default" strategy displays no specific parameters and calls onConfigChange', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    // For ShadCN/Radix Select, options might be found by text within a listbox/option role after trigger
    const noneOption = await screen.findByRole('option', { name: 'None / Default' });
    await userEvent.click(noneOption);

    expect(screen.getByText(/No specific parameters required for this strategy/i)).toBeVisible();
    // The first call is initial 'none', second is explicit selection of 'none'
    expect(mockOnConfigChange).toHaveBeenCalledTimes(2); 
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'none', params: {} });
  });

  // Test Case 2: "LLMExtractionStrategy"
  test('selecting "LLMExtractionStrategy" displays LLM parameters and calls onConfigChange with empty defaults', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    const llmOption = await screen.findByRole('option', { name: 'LLMExtractionStrategy' });
    await userEvent.click(llmOption);

    expect(screen.getByLabelText(/LLM Instructions\/Prompt/i)).toBeVisible();
    expect(screen.getByLabelText(/LLM Provider\/Model/i)).toBeVisible();
    expect(screen.getByLabelText(/LLM API Token/i)).toBeVisible();
    expect(screen.getByLabelText(/LLM Base URL \(Custom Endpoint\)/i)).toBeVisible();
    // The first call is initial 'none', second is selection of 'llm'
    expect(mockOnConfigChange).toHaveBeenCalledTimes(2);
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'llm', params: {} });
  });

  // Test Case 3: "JsonCssExtractionStrategy"
  test('selecting "JsonCssExtractionStrategy" displays Schema parameter and calls onConfigChange with empty defaults', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    const jsonCssOption = await screen.findByRole('option', { name: 'JsonCssExtractionStrategy' });
    await userEvent.click(jsonCssOption);

    expect(screen.getByLabelText(/Schema \(JSON\)/i)).toBeVisible();
    // The first call is initial 'none', second is selection of 'json_css'
    expect(mockOnConfigChange).toHaveBeenCalledTimes(2);
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'json_css', params: {} });
  });

  // Test Case 4: "CosineStrategy"
  test('selecting "CosineStrategy" displays no specific parameters and calls onConfigChange', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    const cosineOption = await screen.findByRole('option', { name: 'CosineStrategy' });
    await userEvent.click(cosineOption);

    expect(screen.getByText(/No specific parameters required for this strategy/i)).toBeVisible();
    // The first call is initial 'none', second is selection of 'cosine'
    expect(mockOnConfigChange).toHaveBeenCalledTimes(2);
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'cosine', params: {} });
  });

  // Test: Initial render with default "none" strategy
  test('initially renders with "None / Default" strategy selected and correct params when no initialConfig', () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('None / Default');
    expect(screen.getByText(/No specific parameters required for this strategy/i)).toBeVisible();
    // This call happens due to initial setup.
    expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'none', params: {} });
  });

  // Test: initialConfig prop
   test('initializes with a given strategy and params from initialConfig prop and calls onConfigChange', () => {
    const initialConfig = {
      strategy: 'llm',
      params: {
        llm_instructions: 'Initial instructions',
        llm_provider_model: 'openai/gpt-test',
        llm_api_token: 'test_token',
        llm_base_url: 'http://localhost:8080'
      }
    };
    renderWithProvider(
      <ExtractionStrategyConfigurator 
        onConfigChange={mockOnConfigChange} 
        initialConfig={initialConfig} 
      />
    );
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('LLMExtractionStrategy');
    expect(screen.getByLabelText(/LLM Instructions\/Prompt/i)).toHaveValue('Initial instructions');
    expect(screen.getByLabelText(/LLM Provider\/Model/i)).toHaveValue('openai/gpt-test');
    expect(screen.getByLabelText(/LLM API Token/i)).toHaveValue('test_token');
    expect(screen.getByLabelText(/LLM Base URL \(Custom Endpoint\)/i)).toHaveValue('http://localhost:8080');
    // This call happens due to initial setup with initialConfig.
    expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
    expect(mockOnConfigChange).toHaveBeenLastCalledWith(initialConfig);
  });
});

describe('ExtractionStrategyConfigurator - Parameter Input and State Update', () => {
  let mockOnConfigChange;

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // Scenario 1: JsonCssExtractionStrategy - Schema Input
  test('JsonCssExtractionStrategy: updates schema and calls onConfigChange', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    await userEvent.click(await screen.findByRole('option', { name: 'JsonCssExtractionStrategy' }));
    
    // Verify initial callback (post-strategy selection)
    // The first call is for initial render (default 'none'), second for strategy change.
    expect(mockOnConfigChange).toHaveBeenCalledTimes(2); // Initial 'none', then 'json_css'
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'json_css', params: {} });

    // Simulate Input:
    const schemaTextarea = screen.getByLabelText(/Schema \(JSON\)/i);
    const testSchema = '{"key":"value"}';
    await userEvent.type(schemaTextarea, testSchema);
    
    // Verify Callback (post-schema input):
    expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'json_css', params: { schema: testSchema } });
    expect(mockOnConfigChange).toHaveBeenCalledTimes(2 + testSchema.length); // Called for each char typed + 2 initial
  });

  // Scenario 2: LLMExtractionStrategy - Parameter Inputs (Sequential)
  describe('LLMExtractionStrategy: Parameter Inputs', () => {
    test('updates llm_instructions and calls onConfigChange', async () => {
      renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
      
      const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
      await userEvent.click(strategySelectTrigger);
      await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));
      
      // Initial calls: 1 for 'none' (default), 1 for 'llm' selection
      expect(mockOnConfigChange).toHaveBeenCalledTimes(2);
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'llm', params: {} });

      const instructionsInput = screen.getByLabelText(/LLM Instructions\/Prompt/i);
      const testInstructions = 'Extract summary';
      await userEvent.type(instructionsInput, testInstructions);
      
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ 
        strategy: 'llm', 
        params: { 
          llm_instructions: testInstructions, 
          llm_provider_model: '', 
          llm_api_token: '', 
          llm_base_url: '' 
        } 
      });
      expect(mockOnConfigChange).toHaveBeenCalledTimes(2 + testInstructions.length);
    });

    test('updates llm_provider_model and calls onConfigChange', async () => {
      renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
      
      const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
      await userEvent.click(strategySelectTrigger);
      await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));
      // mockOnConfigChange called for 'none', then 'llm' (2 calls)

      const providerModelInput = screen.getByLabelText(/LLM Provider\/Model/i);
      const testProviderModel = 'openai/gpt-4o';
      await userEvent.type(providerModelInput, testProviderModel);
      
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ 
        strategy: 'llm', 
        params: { 
          llm_instructions: '', 
          llm_provider_model: testProviderModel, 
          llm_api_token: '', 
          llm_base_url: '' 
        } 
      });
      expect(mockOnConfigChange).toHaveBeenCalledTimes(2 + testProviderModel.length);
    });

    test('updates llm_api_token and calls onConfigChange', async () => {
      renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
      
      const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
      await userEvent.click(strategySelectTrigger);
      await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));
      // mockOnConfigChange called for 'none', then 'llm' (2 calls)

      const apiTokenInput = screen.getByLabelText(/LLM API Token/i);
      const testApiToken = 'test-api-key';
      await userEvent.type(apiTokenInput, testApiToken);
      
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ 
        strategy: 'llm', 
        params: { 
          llm_instructions: '', 
          llm_provider_model: '', 
          llm_api_token: testApiToken, 
          llm_base_url: '' 
        } 
      });
      expect(mockOnConfigChange).toHaveBeenCalledTimes(2 + testApiToken.length);
    });

    test('updates llm_base_url and calls onConfigChange', async () => {
      renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
      
      const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
      await userEvent.click(strategySelectTrigger);
      await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));
      // mockOnConfigChange called for 'none', then 'llm' (2 calls)

      const baseUrlInput = screen.getByLabelText(/LLM Base URL \(Custom Endpoint\)/i);
      const testBaseUrl = 'http://localhost:8000';
      await userEvent.type(baseUrlInput, testBaseUrl);
      
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ 
        strategy: 'llm', 
        params: { 
          llm_instructions: '', 
          llm_provider_model: '', 
          llm_api_token: '', 
          llm_base_url: testBaseUrl 
        } 
      });
      expect(mockOnConfigChange).toHaveBeenCalledTimes(2 + testBaseUrl.length);
    });

    test('updates all LLM parameters sequentially and calls onConfigChange correctly', async () => {
      renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);

      const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
      await userEvent.click(strategySelectTrigger);
      await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));
      // Call 1 (default 'none'), Call 2 (select 'llm')
      expect(mockOnConfigChange).toHaveBeenCalledTimes(2);
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ strategy: 'llm', params: {} });
      let expectedCallCount = 2;

      const instructionsInput = screen.getByLabelText(/LLM Instructions\/Prompt/i);
      const testInstructions = 'Extract summary';
      await userEvent.type(instructionsInput, testInstructions);
      expectedCallCount += testInstructions.length;
      expect(mockOnConfigChange).toHaveBeenCalledTimes(expectedCallCount);
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ 
        strategy: 'llm', 
        params: { 
          llm_instructions: testInstructions, 
          llm_provider_model: '', 
          llm_api_token: '', 
          llm_base_url: '' 
        } 
      });

      const providerModelInput = screen.getByLabelText(/LLM Provider\/Model/i);
      const testProviderModel = 'openai/gpt-4o';
      await userEvent.type(providerModelInput, testProviderModel);
      expectedCallCount += testProviderModel.length;
      expect(mockOnConfigChange).toHaveBeenCalledTimes(expectedCallCount);
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ 
        strategy: 'llm', 
        params: { 
          llm_instructions: testInstructions, 
          llm_provider_model: testProviderModel, 
          llm_api_token: '', 
          llm_base_url: '' 
        } 
      });

      const apiTokenInput = screen.getByLabelText(/LLM API Token/i);
      const testApiToken = 'test-api-key';
      await userEvent.type(apiTokenInput, testApiToken);
      expectedCallCount += testApiToken.length;
      expect(mockOnConfigChange).toHaveBeenCalledTimes(expectedCallCount);
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ 
        strategy: 'llm', 
        params: { 
          llm_instructions: testInstructions, 
          llm_provider_model: testProviderModel, 
          llm_api_token: testApiToken, 
          llm_base_url: '' 
        } 
      });

      const baseUrlInput = screen.getByLabelText(/LLM Base URL \(Custom Endpoint\)/i);
      const testBaseUrl = 'http://localhost:8000';
      await userEvent.type(baseUrlInput, testBaseUrl);
      expectedCallCount += testBaseUrl.length;
      expect(mockOnConfigChange).toHaveBeenCalledTimes(expectedCallCount);
      expect(mockOnConfigChange).toHaveBeenLastCalledWith({ 
        strategy: 'llm', 
        params: { 
          llm_instructions: testInstructions, 
          llm_provider_model: testProviderModel, 
          llm_api_token: testApiToken, 
          llm_base_url: testBaseUrl 
        } 
      });
    });
  });
});

describe('ExtractionStrategyConfigurator - Dynamic initialConfig Update', () => {
  let mockOnConfigChange;

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
  });
  
  // Scenario 1: Changing strategy and params
  test('Scenario 1: updates UI and calls onConfigChange when initialConfig changes strategy and params', async () => {
    const initialConfigNone = { strategy: 'none', params: {} };
    const { rerender } = renderWithProvider(
      <ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigNone} />
    );
    // Initial render calls onConfigChange once with initialConfigNone
    expect(mockOnConfigChange).toHaveBeenCalledWith(initialConfigNone);
    mockOnConfigChange.mockClear(); // Clear calls from initial render

    const newConfigLlm = { 
      strategy: 'llm', 
      params: { 
        llm_instructions: 'Extract topics', 
        llm_provider_model: 'openai/gpt-4o',
        llm_api_token: '', 
        llm_base_url: '' 
      } 
    };
    rerender(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={newConfigLlm} />);

    // UI Verification
    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    expect(strategySelectTrigger).toHaveTextContent('LLMExtractionStrategy'); 
    expect(screen.getByLabelText(/LLM Instructions\/Prompt/i)).toHaveValue('Extract topics');
    expect(screen.getByLabelText(/LLM Provider\/Model/i)).toHaveValue('openai/gpt-4o');
    expect(screen.queryByText(/No specific parameters required/i)).not.toBeInTheDocument();

    // Callback Verification
    expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
    expect(mockOnConfigChange).toHaveBeenCalledWith(newConfigLlm);
  });

  // Scenario 2: Changing only params for the same strategy
  test('Scenario 2: updates UI and calls onConfigChange when initialConfig changes only params for the same strategy', async () => {
    const initialConfigLlmOld = { 
      strategy: 'llm', 
      params: { 
        llm_instructions: 'Old prompt', 
        llm_provider_model: 'ollama/mistral',
        llm_api_token: 'old_token',
        llm_base_url: 'http://old.url'
      } 
    };
    const { rerender } = renderWithProvider(
      <ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigLlmOld} />
    );
    expect(mockOnConfigChange).toHaveBeenCalledWith(initialConfigLlmOld);
    mockOnConfigChange.mockClear();

    const newConfigLlmNewParams = { 
      strategy: 'llm', 
      params: { 
        llm_instructions: 'New prompt', 
        llm_provider_model: 'ollama/llama3', 
        llm_api_token: 'secret',
        llm_base_url: 'http://new.url'
      } 
    };
    rerender(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={newConfigLlmNewParams} />);

    // UI Verification
    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    expect(strategySelectTrigger).toHaveTextContent('LLMExtractionStrategy');
    expect(screen.getByLabelText(/LLM Instructions\/Prompt/i)).toHaveValue('New prompt');
    expect(screen.getByLabelText(/LLM Provider\/Model/i)).toHaveValue('ollama/llama3');
    expect(screen.getByLabelText(/LLM API Token/i)).toHaveValue('secret');
    expect(screen.getByLabelText(/LLM Base URL \(Custom Endpoint\)/i)).toHaveValue('http://new.url');

    // Callback Verification
    expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
    expect(mockOnConfigChange).toHaveBeenCalledWith(newConfigLlmNewParams);
  });

  // Scenario 3: Changing initialConfig to default to 'none'
  describe('Scenario 3: initialConfig changes to default to "none"', () => {
    const initialConfigJsonCss = { 
      strategy: 'json_css', 
      params: { schema: '{"key":"val"}' } 
    };

    test('when new initialConfig is undefined', async () => {
      const { rerender } = renderWithProvider(
        <ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigJsonCss} />
      );
      expect(mockOnConfigChange).toHaveBeenCalledWith(initialConfigJsonCss);
      mockOnConfigChange.mockClear();

      rerender(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={undefined} />);

      // UI Verification
      const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
      expect(strategySelectTrigger).toHaveTextContent('None / Default');
      expect(screen.queryByLabelText(/Schema \(JSON\)/i)).not.toBeInTheDocument();
      expect(screen.getByText(/No specific parameters required for this strategy/i)).toBeInTheDocument();

      // Callback Verification
      expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
      expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'none', params: {} });
    });

    test('when new initialConfig.strategy is undefined', async () => {
      const { rerender } = renderWithProvider(
        <ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigJsonCss} />
      );
      expect(mockOnConfigChange).toHaveBeenCalledWith(initialConfigJsonCss);
      mockOnConfigChange.mockClear();

      const newConfigStrategyUndefined = { strategy: undefined, params: { other: 'data' } };
      rerender(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={newConfigStrategyUndefined} />);
      
      // UI Verification
      const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
      expect(strategySelectTrigger).toHaveTextContent('None / Default');
      expect(screen.queryByLabelText(/Schema \(JSON\)/i)).not.toBeInTheDocument();
      expect(screen.getByText(/No specific parameters required for this strategy/i)).toBeInTheDocument();

      // Callback Verification
      expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
      // The component defaults strategy to 'none' but should preserve other params if present in the new initialConfig
      expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'none', params: { other: 'data' } });
    });

     test('when new initialConfig.strategy is null', async () => {
      const { rerender } = renderWithProvider(
        <ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigJsonCss} />
      );
      expect(mockOnConfigChange).toHaveBeenCalledWith(initialConfigJsonCss);
      mockOnConfigChange.mockClear();

      const newConfigStrategyNull = { strategy: null, params: { another: 'info' } };
      rerender(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={newConfigStrategyNull} />);
      
      // UI Verification
      const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
      expect(strategySelectTrigger).toHaveTextContent('None / Default');
      expect(screen.queryByLabelText(/Schema \(JSON\)/i)).not.toBeInTheDocument();
      expect(screen.getByText(/No specific parameters required for this strategy/i)).toBeInTheDocument();
      
      // Callback Verification
      expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
      expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'none', params: { another: 'info' } });
    });
  });
});

describe('ExtractionStrategyConfigurator - Tooltip Accessibility', () => {
  let mockOnConfigChange;

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
  });

  afterEach(() => {
    mockOnConfigChange.mockClear();
  });

  // Test Case 1: Tooltip for "Select Strategy" Dropdown
  test('Test Case 1: displays tooltip for "Select Strategy" dropdown', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    // Assuming the tooltip trigger is an icon button within the label's container
    // The label itself might not be the trigger for ShadCN tooltips.
    // Often, it's an <InfoCircledIcon /> wrapped in <TooltipTrigger asChild><Button variant="ghost" size="icon">...</Button></TooltipTrigger>
    // We need to find this button. It might be best to add a data-testid to such triggers in the component.
    // For now, let's try to find it by proximity or a generic role if possible.
    // A more robust selector would be `screen.getByTestId('select-strategy-tooltip-trigger')` if that existed.
    const strategyLabelContainer = screen.getByText(/Select Strategy/i).closest('div'); // Find a common parent
    const tooltipTriggerIcon = within(strategyLabelContainer).getByRole('button'); // Assuming the icon is a button
    
    await userEvent.hover(tooltipTriggerIcon);

    const tooltip = await screen.findByRole('tooltip');
    expect(tooltip).toBeVisible();
    expect(within(tooltip).getByText(/Choose the method `crawl4ai` will use to extract structured data/i)).toBeVisible();
    
    await userEvent.unhover(tooltipTriggerIcon);
    // Check if Radix UI removes it from DOM or just hides. queryByRole is good for non-existence.
    // For Radix, it's usually removed from DOM when not open.
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  // Test Case 2: Tooltip for "Schema (JSON)" input (JsonCssExtractionStrategy)
  test('Test Case 2: displays tooltip for "Schema (JSON)" input when JsonCssExtractionStrategy is selected', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    await userEvent.click(await screen.findByRole('option', { name: 'JsonCssExtractionStrategy' }));

    const schemaLabelContainer = (await screen.findByText(/Schema \(JSON\)/i)).closest('div');
    const tooltipTriggerIcon = within(schemaLabelContainer).getByRole('button');
    
    await userEvent.hover(tooltipTriggerIcon);

    const tooltip = await screen.findByRole('tooltip');
    expect(tooltip).toBeVisible();
    expect(within(tooltip).getByText(/JSON schema defining the structure of the data to be extracted using CSS selectors/i)).toBeVisible();
    
    await userEvent.unhover(tooltipTriggerIcon);
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  // Test Case 3: Tooltip for "LLM Instructions/Prompt" input (LLMExtractionStrategy)
  test('Test Case 3: displays tooltip for "LLM Instructions/Prompt" input when LLMExtractionStrategy is selected', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);

    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));

    const instructionsLabelContainer = (await screen.findByText(/LLM Instructions\/Prompt/i)).closest('div');
    const tooltipTriggerIcon = within(instructionsLabelContainer).getByRole('button');

    await userEvent.hover(tooltipTriggerIcon);

    const tooltip = await screen.findByRole('tooltip');
    expect(tooltip).toBeVisible();
    expect(within(tooltip).getByText(/Detailed instructions or prompt for the LLM to guide content extraction/i)).toBeVisible();

    await userEvent.unhover(tooltipTriggerIcon);
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  // Test Case 4: Tooltip for "LLM Provider/Model" input (LLMExtractionStrategy)
  test('Test Case 4: displays tooltip for "LLM Provider/Model" input when LLMExtractionStrategy is selected', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);

    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));

    const providerLabelContainer = (await screen.findByText(/LLM Provider\/Model/i)).closest('div');
    const tooltipTriggerIcon = within(providerLabelContainer).getByRole('button');
    
    await userEvent.hover(tooltipTriggerIcon);

    const tooltip = await screen.findByRole('tooltip');
    expect(tooltip).toBeVisible();
    expect(within(tooltip).getByText(/Specify the LLM provider and model name/i)).toBeVisible();
    
    await userEvent.unhover(tooltipTriggerIcon);
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  // Test Case 5: Tooltip for "LLM API Token" input (LLMExtractionStrategy)
  test('Test Case 5: displays tooltip for "LLM API Token" input when LLMExtractionStrategy is selected', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);

    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));

    const apiTokenLabelContainer = (await screen.findByText(/LLM API Token/i)).closest('div');
    const tooltipTriggerIcon = within(apiTokenLabelContainer).getByRole('button');

    await userEvent.hover(tooltipTriggerIcon);

    const tooltip = await screen.findByRole('tooltip');
    expect(tooltip).toBeVisible();
    expect(within(tooltip).getByText(/API token for the selected LLM provider/i)).toBeVisible();

    await userEvent.unhover(tooltipTriggerIcon);
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  // Test Case 6: Tooltip for "LLM Base URL (Custom Endpoint)" input (LLMExtractionStrategy)
  test('Test Case 6: displays tooltip for "LLM Base URL (Custom Endpoint)" input when LLMExtractionStrategy is selected', async () => {
    renderWithProvider(<ExtractionStrategyConfigurator onConfigChange={mockOnConfigChange} />);

    const strategySelectTrigger = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelectTrigger);
    await userEvent.click(await screen.findByRole('option', { name: 'LLMExtractionStrategy' }));

    const baseUrlLabelContainer = (await screen.findByText(/LLM Base URL \(Custom Endpoint\)/i)).closest('div');
    const tooltipTriggerIcon = within(baseUrlLabelContainer).getByRole('button');
    
    await userEvent.hover(tooltipTriggerIcon);

    const tooltip = await screen.findByRole('tooltip');
    expect(tooltip).toBeVisible();
    expect(within(tooltip).getByText(/Optional custom base URL for self-hosted or alternative LLM API endpoints/i)).toBeVisible();

    await userEvent.unhover(tooltipTriggerIcon);
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });
});