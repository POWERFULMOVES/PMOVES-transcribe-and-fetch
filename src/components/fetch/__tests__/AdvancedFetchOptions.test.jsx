import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AdvancedFetchOptions from '../../AdvancedFetchOptions';

// Mock the child ExtractionStrategyConfigurator component
jest.mock('../ExtractionStrategyConfigurator', () => {
  // eslint-disable-next-line react/display-name
  return () => <div data-testid="mocked-extraction-strategy-configurator">Mocked Extraction Strategy Configurator</div>;
});

// Mock the child DeepCrawlStrategyConfigurator component
jest.mock('../../DeepCrawlStrategyConfigurator', () => {
  // eslint-disable-next-line react/display-name
  return () => <div data-testid="mocked-deep-crawl-strategy-configurator">Mocked Deep Crawl Config</div>;
});

const defaultMockProps = {
  // General Jina.ai props (provide defaults or mocks)
  targetSelectorAdvanced: '',
  setTargetSelectorAdvanced: jest.fn(),
  excludedSelectors: '',
  setExcludedSelectors: jest.fn(),
  browserEngine: 'chromium',
  setBrowserEngine: jest.fn(),
  tokenBudget: 0,
  setTokenBudget: jest.fn(),
  viewportWidth: 1920,
  setViewportWidth: jest.fn(),
  viewportHeight: 1080,
  setViewportHeight: jest.fn(),
  markdownFlavor: 'commonmark',
  setMarkdownFlavor: jest.fn(),
  timeout: 60,
  setTimeout: jest.fn(),
  extractTextOnly: false,
  setExtractTextOnly: jest.fn(),
  extractTables: false,
  setExtractTables: jest.fn(),
  extractImages: false,
  setExtractImages: jest.fn(),
  extractLinks: false,
  setExtractLinks: jest.fn(),
  jsonResponse: false,
  setJsonResponse: jest.fn(),
  cleanFormat: false,
  setCleanFormat: jest.fn(),
  uploadToSupabase: false,
  setUploadToSupabase: jest.fn(),
  imageCaptioning: false,
  setImageCaptioning: jest.fn(),
  cacheTtl: 0,
  setCacheTtl: jest.fn(),
  browserLocale: 'en-US',
  setBrowserLocale: jest.fn(),
  extractMetadata: false,
  setExtractMetadata: jest.fn(),

  // crawl4ai specific props
  crawl4aiUserAgent: 'TestAgent/1.0',
  setCrawl4aiUserAgent: jest.fn(),
  crawl4aiViewportWidth: 1920,
  setCrawl4aiViewportWidth: jest.fn(),
  crawl4aiViewportHeight: 1080,
  setCrawl4aiViewportHeight: jest.fn(),
  crawl4aiProxyUrl: '',
  setCrawl4aiProxyUrl: jest.fn(),
  crawl4aiPageLoadWaitCondition: 'networkidle',
  setCrawl4aiPageLoadWaitCondition: jest.fn(),
  crawl4aiPageTimeout: 30000,
  setCrawl4aiPageTimeout: jest.fn(),
  crawl4aiWaitForCondition: '',
  setCrawl4aiWaitForCondition: jest.fn(),
  crawl4aiEnableJs: true,
  setCrawl4aiEnableJs: jest.fn(),
  crawl4aiIgnoreHttpsErrors: false,
  setCrawl4aiIgnoreHttpsErrors: jest.fn(),
  crawl4aiLightMode: false,
  setCrawl4aiLightMode: jest.fn(),
  crawl4aiTextMode: false,
  setCrawl4aiTextMode: jest.fn(),
  crawl4aiTargetElements: '',
  setCrawl4aiTargetElements: jest.fn(),
  crawl4aiExcludedElements: '',
  setCrawl4aiExcludedElements: jest.fn(),
  crawl4aiExcludedTags: '',
  setCrawl4aiExcludedTags: jest.fn(),
  crawl4aiExtractOnlyTextContent: false,
  setCrawl4aiExtractOnlyTextContent: jest.fn(),
  crawl4aiProcessIframes: false,
  setCrawl4aiProcessIframes: jest.fn(),
  crawl4aiWordCountThreshold: 0,
  setCrawl4aiWordCountThreshold: jest.fn(),
  crawl4aiRemoveForms: false,
  setCrawl4aiRemoveForms: jest.fn(),
  crawl4aiKeepDataAttributes: false,
  setCrawl4aiKeepDataAttributes: jest.fn(),
  crawl4aiExecuteJsOnLoad: '',
  setCrawl4aiExecuteJsOnLoad: jest.fn(),
  crawl4aiScanFullPage: false,
  setCrawl4aiScanFullPage: jest.fn(),
  crawl4aiScrollDelay: 2,
  setCrawl4aiScrollDelay: jest.fn(),
  crawl4aiRemoveOverlayElements: false,
  setCrawl4aiRemoveOverlayElements: jest.fn(),
  crawl4aiSimulateUserBehavior: false,
  setCrawl4aiSimulateUserBehavior: jest.fn(),
  crawl4aiEnableMagic: false,
  setCrawl4aiEnableMagic: jest.fn(),
  crawl4aiOverrideNavigator: false,
  setCrawl4aiOverrideNavigator: jest.fn(),
  crawl4aiCacheMode: 'enabled',
  setCrawl4aiCacheMode: jest.fn(),
  crawl4aiCaptureScreenshot: false,
  setCrawl4aiCaptureScreenshot: jest.fn(),
  crawl4aiGeneratePdf: false,
  setCrawl4aiGeneratePdf: jest.fn(),
  crawl4aiCaptureMhtml: false,
  setCrawl4aiCaptureMhtml: jest.fn(),
  crawl4aiExcludeExternalImages: false,
  setCrawl4aiExcludeExternalImages: jest.fn(),
  crawl4aiImageAltTextMinWordCount: 0,
  setCrawl4aiImageAltTextMinWordCount: jest.fn(),
  crawl4aiImageRelevanceScoreThreshold: 0.5,
  setCrawl4aiImageRelevanceScoreThreshold: jest.fn(),
  crawl4aiExcludeExternalLinks: false,
  setCrawl4aiExcludeExternalLinks: jest.fn(),
  crawl4aiExcludeSocialMediaLinks: false,
  setCrawl4aiExcludeSocialMediaLinks: jest.fn(),
  crawl4aiCustomExcludedDomains: '',
  setCrawl4aiCustomExcludedDomains: jest.fn(),
  crawl4aiRespectRobotsTxt: true,
  setCrawl4aiRespectRobotsTxt: jest.fn(),
  crawl4aiVerboseLogging: false,
  setCrawl4aiVerboseLogging: jest.fn(),
  crawl4aiLogPageConsoleOutput: false,
  setCrawl4aiLogPageConsoleOutput: jest.fn(),
  crawl4aiLlmProviderModel: '',
  setCrawl4aiLlmProviderModel: jest.fn(),
  crawl4aiLlmApiToken: '',
  setCrawl4aiLlmApiToken: jest.fn(),
  crawl4aiLlmBaseUrl: '',
  setCrawl4aiLlmBaseUrl: jest.fn(),
  crawl4aiMarkdownGenerator: 'Default',
  setCrawl4aiMarkdownGenerator: jest.fn(),
  crawl4aiBrowserCookies: '',
  setCrawl4aiBrowserCookies: jest.fn(),
  crawl4aiBrowserHeaders: '',
  setCrawl4aiBrowserHeaders: jest.fn(),
  crawl4aiBrowserUsePersistentContext: false,
  setCrawl4aiBrowserUsePersistentContext: jest.fn(),
  crawl4aiCrawlSessionId: '',
  setCrawl4aiCrawlSessionId: jest.fn(),
  crawl4aiCrawlCssSelector: '',
  setCrawl4aiCrawlCssSelector: jest.fn(),
  crawl4aiExtractionConfig: { strategy: 'auto', extractionPrompt: '', extractionModel: 'gpt-3.5-turbo' },
  onCrawl4aiExtractionConfigChange: jest.fn(),
  crawl4aiDeepCrawlConfig: { strategy: 'none', params: {} },
  onCrawl4aiDeepCrawlConfigChange: jest.fn(),
};

// const mockSetFormState = jest.fn(); // No longer needed as we pass individual props
const mockOnCrawl4aiExtractionConfigChange = defaultMockProps.onCrawl4aiExtractionConfigChange;
// const mockOnDeepCrawlConfigChange = jest.fn(); // This prop is not on AdvancedFetchOptions
const mockOnCrawl4aiDeepCrawlConfigChange = defaultMockProps.onCrawl4aiDeepCrawlConfigChange;
const mockSetCrawl4aiMarkdownGenerator = defaultMockProps.setCrawl4aiMarkdownGenerator;


describe('AdvancedFetchOptions', () => {
  const renderComponent = (customProps = {}) => {
    const props = {
      ...defaultMockProps,
      ...customProps, // Override defaults with test-specific props
    };
    return render(<AdvancedFetchOptions {...props} />);
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('when fetchingEngine is "crawl4ai"', () => {
    beforeEach(() => {
      renderComponent({ fetchingEngine: 'crawl4ai' });
    });

    it('should display the "crawl4ai - Extraction Strategy" accordion trigger', () => {
      expect(screen.getByText('crawl4ai - Extraction Strategy')).toBeInTheDocument();
    });

    it('should display the mocked ExtractionStrategyConfigurator when accordion is opened', () => {
      const trigger = screen.getByText('crawl4ai - Extraction Strategy');
      fireEvent.click(trigger); // Open the accordion
      expect(screen.getByTestId('mocked-extraction-strategy-configurator')).toBeInTheDocument();
      expect(screen.getByText('Mocked Extraction Strategy Configurator')).toBeInTheDocument();
    });
  });

  describe('when fetchingEngine is "default"', () => {
    beforeEach(() => {
      renderComponent({ fetchingEngine: 'default' });
    });

    it('should not display the "crawl4ai - Extraction Strategy" accordion trigger', () => {
      expect(screen.queryByText('crawl4ai - Extraction Strategy')).not.toBeInTheDocument();
    });

    it('should not display the mocked ExtractionStrategyConfigurator', () => {
      expect(screen.queryByTestId('mocked-extraction-strategy-configurator')).not.toBeInTheDocument();
    });
  });

  describe('when fetchingEngine is "jina_reader"', () => {
    beforeEach(() => {
      renderComponent({ fetchingEngine: 'jina_reader' });
    });

    it('should not display the "crawl4ai - Extraction Strategy" accordion trigger', () => {
      expect(screen.queryByText('crawl4ai - Extraction Strategy')).not.toBeInTheDocument();
    });

    it('should not display the mocked ExtractionStrategyConfigurator', () => {
      expect(screen.queryByTestId('mocked-extraction-strategy-configurator')).not.toBeInTheDocument();
    });
  });

  // New describe block for Deep Crawl Strategy Conditional Rendering
  describe('AdvancedFetchOptions - Deep Crawl Strategy Conditional Rendering', () => {
    test('should render the "crawl4ai - Deep Crawl Strategy" accordion and configurator when fetchingEngine is "crawl4ai"', () => {
      renderComponent({ fetchingEngine: 'crawl4ai' });
      
      expect(screen.getByRole('button', { name: /crawl4ai - Deep Crawl Strategy/i })).toBeInTheDocument();
      
      // Accordion items are open by default due to defaultValue in component
      // fireEvent.click(screen.getByRole('button', { name: /crawl4ai - Deep Crawl Strategy/i }));
      expect(screen.getByTestId('mocked-deep-crawl-strategy-configurator')).toBeInTheDocument();
    });

    test('should NOT render the "crawl4ai - Deep Crawl Strategy" section when fetchingEngine is "default"', () => {
      renderComponent({ fetchingEngine: 'default' });
      
      expect(screen.queryByRole('button', { name: /crawl4ai - Deep Crawl Strategy/i })).not.toBeInTheDocument();
      expect(screen.queryByTestId('mocked-deep-crawl-strategy-configurator')).not.toBeInTheDocument();
    });

    test('should NOT render the "crawl4ai - Deep Crawl Strategy" section when fetchingEngine is "jina_reader"', () => {
      renderComponent({ fetchingEngine: 'jina_reader' });

      expect(screen.queryByRole('button', { name: /crawl4ai - Deep Crawl Strategy/i })).not.toBeInTheDocument();
      expect(screen.queryByTestId('mocked-deep-crawl-strategy-configurator')).not.toBeInTheDocument();
    });
  });

  // New describe block for Configurable Markdown Generation
  describe('AdvancedFetchOptions - Configurable Markdown Generation', () => {
    beforeEach(() => {
      // Ensure the component is rendered with crawl4ai engine for these tests
      renderComponent({
        fetchingEngine: 'crawl4ai',
        crawl4aiMarkdownGenerator: 'Default', // Ensure this prop is passed for the test
        // setCrawl4aiMarkdownGenerator is part of defaultMockProps
      });
      // Accordions are open by default, so no need to click to open "Content Extraction & Processing"
      // unless specifically testing the click action itself.
      // For these tests, we assume it's open or controls are findable.
    });

    // Test 5.1: Verify that the "Markdown Generator" dropdown exists and is visible when fetchingEngine is crawl4ai.
    it('should display the "Markdown Generator" dropdown when fetchingEngine is "crawl4ai"', () => {
      expect(screen.getByLabelText('Markdown Generator')).toBeInTheDocument();
      // Check for the SelectTrigger specifically, as the label might be associated with the input part of the Select
      expect(screen.getByRole('combobox', { name: 'Markdown Generator' })).toBeInTheDocument();
    });

    // Test 5.2: Verify that a "Default" option is present within this "Markdown Generator" dropdown.
    it('should have a "Default" option in the "Markdown Generator" dropdown', () => {
      const dropdownTrigger = screen.getByRole('combobox', { name: 'Markdown Generator' });
      fireEvent.mouseDown(dropdownTrigger); // Open the dropdown
      
      // Check for the "Default" option. The role 'option' is typically used for items in a listbox/combobox.
      // Ensure the option is visible after opening the dropdown.
      expect(screen.getByRole('option', { name: 'Default' })).toBeInTheDocument();
    });

    // Test 5.3: Verify that selecting an option from the "Markdown Generator" dropdown correctly updates the relevant state.
    it('should call setCrawl4aiMarkdownGenerator with the selected value when an option is chosen', () => {
      const dropdownTrigger = screen.getByRole('combobox', { name: 'Markdown Generator' });
      fireEvent.mouseDown(dropdownTrigger); // Open the dropdown
      
      const defaultOption = screen.getByRole('option', { name: 'Default' });
      fireEvent.click(defaultOption); // Select the "Default" option
      
      expect(mockSetCrawl4aiMarkdownGenerator).toHaveBeenCalledTimes(1);
      expect(mockSetCrawl4aiMarkdownGenerator).toHaveBeenCalledWith('Default');
    });

    it('should not display the "Markdown Generator" dropdown when fetchingEngine is not "crawl4ai"', () => {
      // Clear previous render
      // jest.clearAllMocks(); // Done in afterEach
      renderComponent({ fetchingEngine: 'default' }); // Re-render with a different engine

      expect(screen.queryByLabelText('Markdown Generator')).not.toBeInTheDocument();
      expect(screen.queryByRole('combobox', { name: 'Markdown Generator' })).not.toBeInTheDocument();
    });
  });

  // New Test Suite for Item 6: General and Expert crawl4ai Options
  describe('Item 6 (UI Part): UI - General and Expert crawl4ai Options', () => {
    describe('Test 6.1: Accordion and Control Existence', () => {
      beforeEach(() => {
        renderComponent({ fetchingEngine: 'crawl4ai' });
      });

      it('should display all crawl4ai specific accordion sections', () => {
        expect(screen.getByRole('button', { name: 'crawl4ai - Browser & Navigation Settings' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - Content Extraction & Processing' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - Page Interaction & Automation' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - Caching Settings' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - Media Handling Settings' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - Link & Domain Filtering' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - Compliance Settings' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - Debugging & Logging' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - Expert Options' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'crawl4ai - LLM Configuration (Advanced/Future)' })).toBeInTheDocument();
      });

      it('should display key controls within their respective accordion sections', () => {
        // Accordions are open by default due to `accordionDefaultValues` in the component
        // "Browser & Navigation Settings"
        expect(screen.getByLabelText('User Agent')).toBeInTheDocument();
        expect(screen.getByLabelText('Enable JavaScript')).toBeInTheDocument();

        // "Content Extraction & Processing"
        expect(screen.getByLabelText('Target Elements (CSS Selectors)')).toBeInTheDocument();

        // "Expert Options"
        expect(screen.getByLabelText('Browser Cookies (JSON)')).toBeInTheDocument();
        expect(screen.getByLabelText('Browser Headers (JSON)')).toBeInTheDocument();
      });

      it('should NOT display crawl4ai specific accordion sections if fetchingEngine is not "crawl4ai"', () => {
        renderComponent({ fetchingEngine: 'default' });
        expect(screen.queryByRole('button', { name: 'crawl4ai - Browser & Navigation Settings' })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'crawl4ai - Content Extraction & Processing' })).not.toBeInTheDocument();
        // ... (can add more checks for other sections if desired)
        expect(screen.queryByLabelText('User Agent')).not.toBeInTheDocument(); // A control from within
      });
    });

    describe('Test 6.2: Control State and Prop Updates', () => {
      const initialUserAgent = "Initial Test User Agent";
      const initialEnableJs = false;
      const initialTargetElements = "div.initial-target";
      const initialBrowserCookies = '[{"name":"initial","value":"cookie"}]';

      beforeEach(() => {
        // Clear mocks for each test in this suite
        Object.values(defaultMockProps).forEach(prop => {
          if (jest.isMockFunction(prop)) {
            prop.mockClear();
          }
        });

        renderComponent({
          fetchingEngine: 'crawl4ai',
          crawl4aiUserAgent: initialUserAgent,
          crawl4aiEnableJs: initialEnableJs,
          crawl4aiTargetElements: initialTargetElements,
          crawl4aiBrowserCookies: initialBrowserCookies,
          // Pass the mock setters again, as they are part of defaultMockProps which is spread
          setCrawl4aiUserAgent: defaultMockProps.setCrawl4aiUserAgent,
          setCrawl4aiEnableJs: defaultMockProps.setCrawl4aiEnableJs,
          setCrawl4aiTargetElements: defaultMockProps.setCrawl4aiTargetElements,
          setCrawl4aiBrowserCookies: defaultMockProps.setCrawl4aiBrowserCookies,
        });
      });

      // User Agent Input
      it('User Agent input should display initial value and call setter on change', () => {
        const userAgentInput = screen.getByLabelText('User Agent');
        expect(userAgentInput.value).toBe(initialUserAgent);

        fireEvent.change(userAgentInput, { target: { value: 'New User Agent' } });
        expect(defaultMockProps.setCrawl4aiUserAgent).toHaveBeenCalledTimes(1);
        expect(defaultMockProps.setCrawl4aiUserAgent).toHaveBeenCalledWith('New User Agent');
      });

      // Enable JavaScript Switch
      it('Enable JavaScript switch should reflect initial value and call setter on change', () => {
        const enableJsSwitch = screen.getByLabelText('Enable JavaScript');
        expect(enableJsSwitch.checked).toBe(initialEnableJs);

        fireEvent.click(enableJsSwitch);
        expect(defaultMockProps.setCrawl4aiEnableJs).toHaveBeenCalledTimes(1);
        expect(defaultMockProps.setCrawl4aiEnableJs).toHaveBeenCalledWith(!initialEnableJs);
      });

      // Target Elements Input
      it('Target Elements input should display initial value and call setter on change', () => {
        const targetElementsInput = screen.getByLabelText('Target Elements (CSS Selectors)');
        expect(targetElementsInput.value).toBe(initialTargetElements);

        fireEvent.change(targetElementsInput, { target: { value: 'article.new-target' } });
        expect(defaultMockProps.setCrawl4aiTargetElements).toHaveBeenCalledTimes(1);
        expect(defaultMockProps.setCrawl4aiTargetElements).toHaveBeenCalledWith('article.new-target');
      });

      // Browser Cookies Textarea
      it('Browser Cookies textarea should display initial value and call setter on change', () => {
        const browserCookiesTextarea = screen.getByLabelText('Browser Cookies (JSON)');
        expect(browserCookiesTextarea.value).toBe(initialBrowserCookies);

        fireEvent.change(browserCookiesTextarea, { target: { value: '[{"name":"new","value":"cookieVal"}]' } });
        expect(defaultMockProps.setCrawl4aiBrowserCookies).toHaveBeenCalledTimes(1);
        expect(defaultMockProps.setCrawl4aiBrowserCookies).toHaveBeenCalledWith('[{"name":"new","value":"cookieVal"}]');
      });
    });
  });
});