// This is the structure the Intern provided. Implement it in the new file.

import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react'; // Added waitFor and within
import userEvent from '@testing-library/user-event'; // Added userEvent
import DeepCrawlStrategyConfigurator from '../DeepCrawlStrategyConfigurator';
import { TooltipProvider } from 'components/ui/tooltip'; // Assuming jsconfig.json resolves this

// Helper function for rendering with TooltipProvider
const renderWithProvider = (ui, options) => {
  return render(<TooltipProvider>{ui}</TooltipProvider>, options);
};

describe('DeepCrawlStrategyConfigurator - Default Strategy State', () => {
  let mockOnConfigChange;

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // Test Case 1: initialConfig prop is not provided
  test('Test Case 1: defaults to "None / Default" when initialConfig prop is not provided', () => {
    renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    // Inspect the Select trigger
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('None / Default');
    
    // Assertions on callback
    expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
    expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'None', params: {} });
  });

  // Test Case 2: initialConfig.strategy is undefined
  test('Test Case 2: defaults to "None / Default" when initialConfig.strategy is undefined', () => {
    const initialConfigUndefined = { strategy: undefined, params: { someParam: 'value' } }; // Params should be ignored when defaulting
    renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigUndefined} />);
    
    // Inspect the Select trigger
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('None / Default');
    
    // Assertions on callback
    // The Intern's analysis suggests the useEffect hook handles the defaulting *before* the final onConfigChange call based on state.
    // Let's assume the component correctly defaults the state and calls back with the defaulted state.
    expect(mockOnConfigChange).toHaveBeenCalledTimes(1); 
    expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'None', params: {} }); // Params reset for 'None'
  });

  // Test Case 3: initialConfig.strategy is null
  test('Test Case 3: defaults to "None / Default" when initialConfig.strategy is null', () => {
    const initialConfigNull = { strategy: null, params: { max_depth: 3 } }; // Params should be ignored
    renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={initialConfigNull} />);
    
    // Inspect the Select trigger
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('None / Default');
    
    // Assertions on callback
    expect(mockOnConfigChange).toHaveBeenCalledTimes(1);
    expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'None', params: {} }); // Params reset for 'None'
  });
});

describe('DeepCrawlStrategyConfigurator - Strategy Selection and Parameter Display', () => {
  let mockOnConfigChange;

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // Test Case 1: "None / Default" Strategy
  test('Test Case 1: selecting "None / Default" strategy displays no parameters', async () => {
    renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    // Select "None / Default" (even though it's default, explicit selection is good)
    const strategySelect = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelect);
    // Find the option by text content within the listbox that appears
    const listbox = await screen.findByRole('listbox'); // Wait for listbox
    const noneOption = within(listbox).getByText('None / Default'); // Find option within listbox
    await userEvent.click(noneOption);

    // Verify Parameter Display
    expect(screen.queryByLabelText(/Max Depth/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Max Pages/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('switch', { name: /Include External Links/i })).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/URL Filter Regex Patterns/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Score Threshold/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/URL Scorer/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Keywords \(comma-separated\)/i)).not.toBeInTheDocument();
    // Should not show "No specific parameters" message for deep crawl, just absence of fields
  });

  // Test Case 2: "BFSDeepCrawlStrategy"
  test('Test Case 2: selecting "BFSDeepCrawlStrategy" displays correct parameters', async () => {
    renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    const strategySelect = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelect);
    const listbox = await screen.findByRole('listbox');
    const bfsOption = within(listbox).getByText('BFS Deep Crawl Strategy');
    await userEvent.click(bfsOption);

    // Verify Parameter Display
    expect(screen.getByLabelText(/Max Depth/i)).toBeVisible();
    expect(screen.getByLabelText(/Max Pages/i)).toBeVisible();
    expect(screen.getByRole('switch', { name: /Include External Links/i })).toBeVisible();
    expect(screen.getByLabelText(/URL Filter Regex Patterns/i)).toBeVisible();
    expect(screen.getByLabelText(/Score Threshold/i)).toBeVisible();
    expect(screen.queryByLabelText(/URL Scorer/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Keywords \(comma-separated\)/i)).not.toBeInTheDocument();
  });

  // Test Case 3: "DFSDeepCrawlStrategy"
  test('Test Case 3: selecting "DFSDeepCrawlStrategy" displays correct parameters', async () => {
    renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    
    const strategySelect = screen.getByRole('combobox', { name: /Select Strategy/i });
    await userEvent.click(strategySelect);
    const listbox = await screen.findByRole('listbox');
    const dfsOption = within(listbox).getByText('DFS Deep Crawl Strategy');
    await userEvent.click(dfsOption);

    // Verify Parameter Display
    expect(screen.getByLabelText(/Max Depth/i)).toBeVisible();
    expect(screen.getByLabelText(/Max Pages/i)).toBeVisible();
    expect(screen.getByRole('switch', { name: /Include External Links/i })).toBeVisible();
    expect(screen.getByLabelText(/URL Filter Regex Patterns/i)).toBeVisible();
    expect(screen.getByLabelText(/Score Threshold/i)).toBeVisible();
    expect(screen.queryByLabelText(/URL Scorer/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Keywords \(comma-separated\)/i)).not.toBeInTheDocument();
  });

  // Test Case 4: "BestFirstCrawlingStrategy" and URL Scorer Logic
  describe('Test Case 4: BestFirstCrawlingStrategy', () => {
    // Note: The Intern's outline had a beforeEach here to select BestFirst.
    // However, to ensure clean state for each sub-test and avoid potential interference
    // if mockOnConfigChange is called multiple times due to re-renders from strategy selection,
    // it's safer to render and select the strategy within each specific test case
    // or ensure mockOnConfigChange is reset properly if using beforeEach.
    // For this implementation, I'll select it in each test for clarity and isolation.

    test('displays correct initial parameters when BestFirstCrawlingStrategy is selected', async () => {
      renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} />);
      const strategySelect = screen.getByRole('combobox', { name: /Select Strategy/i });
      await userEvent.click(strategySelect);
      const listbox = await screen.findByRole('listbox');
      const bestFirstOption = within(listbox).getByText('Best First Crawling Strategy');
      await userEvent.click(bestFirstOption);

      expect(screen.getByLabelText(/Max Depth/i)).toBeVisible();
      expect(screen.getByLabelText(/Max Pages/i)).toBeVisible();
      expect(screen.getByRole('switch', { name: /Include External Links/i })).toBeVisible();
      expect(screen.getByLabelText(/URL Filter Regex Patterns/i)).toBeVisible();
      expect(screen.getByRole('combobox', { name: /URL Scorer/i })).toBeVisible();
      expect(screen.queryByLabelText(/Score Threshold/i)).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/Keywords \(comma-separated\)/i)).not.toBeInTheDocument();
    });

    test('displays Keywords input when KeywordRelevanceScorer is selected for BestFirst', async () => {
      renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} />);
      const strategySelect = screen.getByRole('combobox', { name: /Select Strategy/i });
      await userEvent.click(strategySelect);
      let listbox = await screen.findByRole('listbox');
      const bestFirstOption = within(listbox).getByText('Best First Crawling Strategy');
      await userEvent.click(bestFirstOption);

      const urlScorerSelect = screen.getByRole('combobox', { name: /URL Scorer/i });
      await userEvent.click(urlScorerSelect);
      // Ensure we are targeting the correct listbox if multiple are open, though unlikely here.
      const scorerListbox = await screen.findByRole('listbox', { name: /URL Scorer/i }); 
      const keywordScorerOption = within(scorerListbox).getByText('Keyword Relevance Scorer');
      await userEvent.click(keywordScorerOption);

      await waitFor(() => {
        expect(screen.getByLabelText(/Keywords \(comma-separated\)/i)).toBeVisible();
      });
    });

    test('hides Keywords input when a non-keyword scorer is selected for BestFirst', async () => {
      renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} />);
      const strategySelect = screen.getByRole('combobox', { name: /Select Strategy/i });
      await userEvent.click(strategySelect);
      let listbox = await screen.findByRole('listbox');
      const bestFirstOption = within(listbox).getByText('Best First Crawling Strategy');
      await userEvent.click(bestFirstOption);

      // First select Keyword scorer to show the input
      const urlScorerSelect = screen.getByRole('combobox', { name: /URL Scorer/i });
      await userEvent.click(urlScorerSelect);
      let scorerListbox = await screen.findByRole('listbox', { name: /URL Scorer/i });
      const keywordScorerOption = within(scorerListbox).getByText('Keyword Relevance Scorer');
      await userEvent.click(keywordScorerOption);
      await waitFor(() => {
        expect(screen.getByLabelText(/Keywords \(comma-separated\)/i)).toBeVisible();
      });

      // Now select "None" scorer
      await userEvent.click(urlScorerSelect); // Re-open the scorer dropdown
      scorerListbox = await screen.findByRole('listbox', { name: /URL Scorer/i }); // Find listbox again
      const noneScorerOption = within(scorerListbox).getByText(/^None$/); // Use regex for exact match "None"
      await userEvent.click(noneScorerOption);

      await waitFor(() => {
        expect(screen.queryByLabelText(/Keywords \(comma-separated\)/i)).not.toBeInTheDocument();
      });
    });
  });
});

describe('DeepCrawlStrategyConfigurator - Dynamic Prop Updates, Resets, and Tooltips', () => {
  let mockOnConfigChange;

  beforeEach(() => {
    mockOnConfigChange = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // Test 3.6: Dynamic updates when initialConfig prop changes.
  test('Test 3.6: updates UI and calls onConfigChange when initialConfig prop changes', async () => {
    const initialProps = {
      onConfigChange: mockOnConfigChange,
      initialConfig: { strategy: 'None', params: {} },
    };
    const { rerender } = renderWithProvider(<DeepCrawlStrategyConfigurator {...initialProps} />);

    // Verify initial state
    expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('None / Default');
    expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'None', params: {} });
    mockOnConfigChange.mockClear(); // Clear mock for the next check

    // New props
    const newInitialConfig = {
      strategy: 'BFSDeepCrawlStrategy',
      params: { max_depth: 5, max_pages: 100, include_external: true, url_filter_patterns: "test.com\nanother.com", score_threshold: 0.7 },
    };
    // The component's onConfigChange will be called due to initialConfig change effect.
    // The output params will be processed, e.g. url_filter_patterns to filter_chain
    const expectedConfigOutput = {
      strategy: 'BFSDeepCrawlStrategy',
      params: {
        max_depth: 5,
        max_pages: 100,
        include_external: true,
        filter_chain: { URLPatternFilter: ["test.com", "another.com"] },
        score_threshold: 0.7
      },
    };

    rerender(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={newInitialConfig} />);
    
    // Wait for UI to update based on new props
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: /Select Strategy/i })).toHaveTextContent('BFS Deep Crawl Strategy');
    });
    expect(screen.getByLabelText(/Max Depth/i)).toHaveValue(5);
    expect(screen.getByLabelText(/Max Pages/i)).toHaveValue(100);
    expect(screen.getByRole('switch', { name: /Include External Links/i })).toBeChecked();
    expect(screen.getByLabelText(/URL Filter Regex Patterns/i)).toHaveValue("test.com\nanother.com");
    expect(screen.getByLabelText(/Score Threshold/i)).toHaveValue(0.7);

    // Check if onConfigChange was called with the new config
    // The component's useEffect for initialConfig changes state, which then triggers the onConfigChange effect.
    await waitFor(() => {
        expect(mockOnConfigChange).toHaveBeenCalledWith(expectedConfigOutput);
    });
  });

  // Test 3.7: Parameter reset when switching strategies.
  test('Test 3.7: resets parameters when switching strategies', async () => {
    renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} />);
    const user = userEvent.setup();

    // 1. Select BFS and set params
    const strategySelect = screen.getByRole('combobox', { name: /Select Strategy/i });
    await user.click(strategySelect);
    let listbox = await screen.findByRole('listbox');
    await user.click(within(listbox).getByText('BFS Deep Crawl Strategy'));

    await user.type(screen.getByLabelText(/Max Depth/i), '3');
    await user.type(screen.getByLabelText(/Score Threshold/i), '0.8');
    await user.type(screen.getByLabelText(/URL Filter Regex Patterns/i), 'bfs-pattern');
    
    // Check onConfigChange for BFS
    await waitFor(() => {
      expect(mockOnConfigChange).toHaveBeenCalledWith(expect.objectContaining({
        strategy: 'BFSDeepCrawlStrategy',
        params: expect.objectContaining({ max_depth: 3, score_threshold: 0.8, filter_chain: { URLPatternFilter: ["bfs-pattern"] } }),
      }));
    });
    mockOnConfigChange.mockClear();

    // 2. Switch to BestFirstCrawlingStrategy and select KeywordRelevanceScorer
    await user.click(strategySelect);
    listbox = await screen.findByRole('listbox');
    await user.click(within(listbox).getByText('Best First Crawling Strategy'));
    
    // Params from BFS (like score_threshold) should be cleared or not present for BestFirst
    // Max Depth is common, so it might persist or be reset to default (empty)
    // URL Filter Patterns is common, might persist or be reset
    
    await waitFor(() => {
        expect(screen.queryByLabelText(/Score Threshold/i)).not.toBeInTheDocument();
    });
    // Max Depth and URL Filter should still be visible for BestFirst
    expect(screen.getByLabelText(/Max Depth/i)).toBeVisible();
    // Check if Max Depth was reset (empty) or kept its value. The component logic resets specific params.
    // The component's reset logic (lines 120-135) only clears score_threshold, url_scorer, and scorer_keywords.
    // So max_depth and url_filter_patterns should retain their values if not explicitly cleared by a new strategy's defaults.
    // However, the initial state for params is empty strings. When switching, if a field is common, it keeps its value.
    // Let's assume for this test that common fields like max_depth are NOT reset unless the new strategy doesn't use them.
    // The component's reset logic is specific:
    // - score_threshold is cleared if not BFS/DFS
    // - url_scorer & scorer_keywords are cleared if not BestFirst
    // So, switching from BFS to BestFirst, score_threshold should be gone.
    expect(screen.getByLabelText(/Max Depth/i)).toHaveValue(3); // Should persist
    expect(screen.getByLabelText(/URL Filter Regex Patterns/i)).toHaveValue('bfs-pattern'); // Should persist

    const urlScorerSelect = screen.getByRole('combobox', { name: /URL Scorer/i });
    await user.click(urlScorerSelect);
    const scorerListbox = await screen.findByRole('listbox', { name: /URL Scorer/i });
    await user.click(within(scorerListbox).getByText('Keyword Relevance Scorer'));
    await user.type(screen.getByLabelText(/Keywords \(comma-separated\)/i), 'ai, ml');

    await waitFor(() => {
      expect(mockOnConfigChange).toHaveBeenCalledWith(expect.objectContaining({
        strategy: 'BestFirstCrawlingStrategy',
        params: expect.objectContaining({
          max_depth: 3, // Persisted
          filter_chain: { URLPatternFilter: ["bfs-pattern"] }, // Persisted
          url_scorer: { KeywordRelevanceScorer: { keywords: ['ai', 'ml'] } },
        }),
      }));
    });
    mockOnConfigChange.mockClear();

    // 3. Switch to "None / Default" strategy
    await user.click(strategySelect);
    listbox = await screen.findByRole('listbox');
    await user.click(within(listbox).getByText('None / Default'));

    // All specific params should be gone
    await waitFor(() => {
      expect(screen.queryByLabelText(/Max Depth/i)).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/Max Pages/i)).not.toBeInTheDocument();
      expect(screen.queryByRole('switch', { name: /Include External Links/i })).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/URL Filter Regex Patterns/i)).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/Score Threshold/i)).not.toBeInTheDocument();
      expect(screen.queryByRole('combobox', { name: /URL Scorer/i })).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/Keywords \(comma-separated\)/i)).not.toBeInTheDocument();
    });
    
    await waitFor(() => {
      expect(mockOnConfigChange).toHaveBeenCalledWith({ strategy: 'None', params: {} });
    });
  });

  // Test 3.8: Tooltip presence and content.
  describe('Test 3.8: Tooltip Presence and Content', () => {
    const testTooltip = async (labelOrTitle, expectedTextContent) => {
      const user = userEvent.setup();
      // Tooltips are associated with the InfoCircledIcon next to the label.
      // The icon is a sibling of the label text or part of the label structure.
      // We find the label, then its associated icon (TooltipTrigger).
      let triggerElement;
      if (labelOrTitle === 'Select Strategy') { // Special case for the main strategy select
        const label = screen.getByText(labelOrTitle).closest('label');
        triggerElement = within(label).getByRole('button'); // InfoCircledIcon is a button in TooltipTrigger
      } else if (labelOrTitle === 'URL Scorer') { // Special case for URL Scorer select
        const label = screen.getByRole('combobox', {name: labelOrTitle}).closest('div').querySelector('label');
        triggerElement = within(label).getByRole('button');
      }
      else if (labelOrTitle === 'Include External Links') { // Special case for switch
         const label = screen.getByLabelText(labelOrTitle).closest('div').querySelector('label');
         triggerElement = within(label).getByRole('button');
      }
      else { // For regular inputs/textareas
        triggerElement = screen.getByLabelText(labelOrTitle).closest('div').querySelector('button[aria-describedby]');
         if (!triggerElement) { // Fallback if the above doesn't work, look for icon near label
            const labelElement = screen.getByLabelText(labelOrTitle);
            const parentDiv = labelElement.closest('.space-y-2'); // Common parent class
            if (parentDiv) {
                 triggerElement = within(parentDiv).getByRole('button'); // InfoCircledIcon
            }
         }
      }
      
      expect(triggerElement).toBeInTheDocument();
      await user.hover(triggerElement);
      const tooltip = await screen.findByText(new RegExp(expectedTextContent, 'i'));
      expect(tooltip).toBeInTheDocument();
      await user.unhover(triggerElement); // Clean up
      await waitFor(() => expect(screen.queryByText(new RegExp(expectedTextContent, 'i'))).not.toBeInTheDocument());
    };

    test('displays tooltips for strategy selection and common parameters', async () => {
      renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={{ strategy: 'BFSDeepCrawlStrategy', params: {} }} />);
      
      await testTooltip('Select Strategy', 'Choose the algorithm for discovering');
      await testTooltip('Max Depth', 'Maximum depth of links to follow');
      await testTooltip('Max Pages', 'Maximum total number of pages to crawl');
      await testTooltip('Include External Links', 'crawler will follow links pointing to different domains');
      await testTooltip('URL Filter Regex Patterns (one per line)', 'Provide regular expressions');
    });

    test('displays tooltips for BFS/DFS specific parameters', async () => {
      renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={{ strategy: 'BFSDeepCrawlStrategy', params: {} }} />);
      await userEvent.click(screen.getByRole('combobox', { name: /Select Strategy/i }));
      const listbox = await screen.findByRole('listbox');
      await userEvent.click(within(listbox).getByText('BFS Deep Crawl Strategy')); // Ensure BFS is selected

      await testTooltip('Score Threshold', 'Minimum score a URL must have');
    });

    test('displays tooltips for BestFirstCrawlingStrategy specific parameters', async () => {
      renderWithProvider(<DeepCrawlStrategyConfigurator onConfigChange={mockOnConfigChange} initialConfig={{ strategy: 'BestFirstCrawlingStrategy', params: { url_scorer: 'KeywordRelevanceScorer' } }} />);
      const user = userEvent.setup();
      
      // Ensure BestFirst is selected
      const strategySelect = screen.getByRole('combobox', { name: /Select Strategy/i });
      // It should be pre-selected by initialConfig, but good to be explicit if needed
      // await user.click(strategySelect);
      // let listbox = await screen.findByRole('listbox');
      // await user.click(within(listbox).getByText('Best First Crawling Strategy'));

      await testTooltip('URL Scorer', 'Select a strategy to score URLs');
      
      // Ensure KeywordRelevanceScorer is selected to show Keywords input
      // const urlScorerSelect = screen.getByRole('combobox', { name: /URL Scorer/i });
      // await user.click(urlScorerSelect);
      // const scorerListbox = await screen.findByRole('listbox', { name: /URL Scorer/i });
      // await user.click(within(scorerListbox).getByText('Keyword Relevance Scorer'));
      
      await waitFor(() => expect(screen.getByLabelText(/Keywords \(comma-separated\)/i)).toBeVisible());
      await testTooltip('Keywords (comma-separated)', 'Comma-separated keywords used by the');
    });
  });
});