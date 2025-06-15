/**
 * Application-wide constants
 */

// Backend API URL - defaults to localhost:8000 if not set in environment
// Prefer NEXT_PUBLIC_BACKEND_URL but fall back to the older NEXT_PUBLIC_API_URL
export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

// SSE connection settings
export const SSE_CONFIG = {
  // Time in ms to wait before reconnecting after a connection error
  RECONNECT_DELAY: 2000,
  // Maximum number of reconnection attempts
  MAX_RETRIES: 5,
  // Connection timeout in ms (increased to 2 minutes to handle longer transcriptions)
  TIMEOUT: 120000,
  // Time in ms to wait after transcription_complete before disconnecting
  COMPLETION_GRACE_PERIOD: 10000,
  // Whether to automatically reconnect after receiving transcription_complete
  AUTO_RECONNECT_AFTER_COMPLETE: false
};

// Search presets configuration
export const SEARCH_PRESETS = {
  default: {
    fine_grained: {
      similarity_threshold: 0.75,
      content_weight: 0.8,
      result_percentage: 0.4,
      max_results: 15
    },
    contextual: {
      similarity_threshold: 0.7,
      content_weight: 0.7,
      result_percentage: 0.35,
      max_results: 10
    },
    overview: {
      similarity_threshold: 0.65,
      content_weight: 0.5,
      result_percentage: 0.25,
      max_results: 5
    }
  },
  technical: {
    fine_grained: {
      similarity_threshold: 0.8,
      content_weight: 0.9,
      result_percentage: 0.6,
      max_results: 20
    },
    contextual: {
      similarity_threshold: 0.75,
      content_weight: 0.8,
      result_percentage: 0.3,
      max_results: 10
    },
    overview: {
      similarity_threshold: 0.7,
      content_weight: 0.7,
      result_percentage: 0.1,
      max_results: 3
    }
  },
  conceptual: {
    fine_grained: {
      similarity_threshold: 0.7,
      content_weight: 0.6,
      result_percentage: 0.2,
      max_results: 5
    },
    contextual: {
      similarity_threshold: 0.7,
      content_weight: 0.5,
      result_percentage: 0.4,
      max_results: 15
    },
    overview: {
      similarity_threshold: 0.65,
      content_weight: 0.3,
      result_percentage: 0.4,
      max_results: 15
    }
  },
  balanced: {
    fine_grained: {
      similarity_threshold: 0.7,
      content_weight: 0.6,
      result_percentage: 0.4,
      max_results: 12
    },
    contextual: {
      similarity_threshold: 0.7,
      content_weight: 0.6,
      result_percentage: 0.4,
      max_results: 12
    },
    overview: {
      similarity_threshold: 0.65,
      content_weight: 0.4,
      result_percentage: 0.2,
      max_results: 8
    }
  }
};

// Search parameter descriptions
export const SEARCH_PARAM_DESCRIPTIONS = {
  similarity_threshold: {
    title: "Similarity Threshold",
    description: "Controls how closely results must match your query (0.0-1.0). Higher values (0.8+) return only very precise matches, while lower values (<0.6) return broader matches."
  },
  content_weight: {
    title: "Content Weight",
    description: "Adjusts the balance between exact content matching and semantic matching. Higher values prioritize exact word matches, while lower values prioritize conceptual similarity."
  },
  max_results: {
    title: "Max Results",
    description: "Controls how many results to show from each search category. Higher values provide more comprehensive results but potentially more noise."
  }
};

// Search tier descriptions
export const SEARCH_TIER_DESCRIPTIONS = {
  fine_grained: {
    title: "Fine-grained (High Precision)",
    description: "For finding specific, precise information. Best for technical details, exact quotes, and specific timestamps. Searches individual segments with high similarity thresholds."
  },
  contextual: {
    title: "Contextual (Balanced)",
    description: "For finding content with surrounding context. Best for understanding topics in context and finding related content. Balances precision and recall, includes context from surrounding segments."
  },
  overview: {
    title: "Overview (Broad Insights)",
    description: "For getting broader insights across content. Best for exploratory searches and finding thematic connections. Uses lower thresholds to capture more conceptual matches."
  }
};

// Search method descriptions
export const SEARCH_METHOD_DESCRIPTIONS = {
  vector: {
    title: "Vector Search",
    description: "Uses AI embeddings to find semantically similar content, even when exact keywords don't match. Provides conceptually related results."
  },
  keyword: {
    title: "Keyword Search",
    description: "Traditional text matching to find content containing specific keywords. Useful for finding exact phrases or terms."
  },
  hybrid: {
    title: "Hybrid Search",
    description: "Combines both approaches for comprehensive results. Prioritizes based on multiple factors including similarity and content type."
  }
};
