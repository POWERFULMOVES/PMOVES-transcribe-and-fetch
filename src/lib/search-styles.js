/**
 * Search Styling Constants
 * 
 * This file contains styling constants for the search interface,
 * mirroring the styling used in the backend (psearchworking.py).
 */

// Icons for different search methods
export const SEARCH_ICONS = {
  'keyword': '🔍',
  'dot_product': '🎯',
  'advanced_hybrid': '🔄',
  'hybrid': '🔄',
  'fine-grained': '🔍',
  'contextual': '🎯',
  'summary-based': '🔄',
  'default': '📌'
};

// Styling for different content sources
export const SOURCE_STYLES = {
  'document_embeddings': {
    'icon': '📄️',
    'color': 'blue',
    'bgColor': 'bg-blue-100',
    'textColor': 'text-blue-700',
    'borderColor': 'border-document-embeddings',
    'title': 'Document Embeddings'
  },
  'video_transcriptions': {
    'icon': '🎬',
    'color': 'green',
    'bgColor': 'bg-green-100',
    'textColor': 'text-green-700',
    'borderColor': 'border-video-transcriptions',
    'title': 'Video Transcriptions'
  },
  'video_transcriptions_full': {
    'icon': '📽️',
    'color': 'magenta',
    'bgColor': 'bg-purple-100',
    'textColor': 'text-purple-700',
    'borderColor': 'border-video-transcriptions-full',
    'title': 'Full Transcriptions'
  },
  'webpage_content': {
    'icon': '🌐',
    'color': 'cyan',
    'bgColor': 'bg-cyan-100',
    'textColor': 'text-cyan-700',
    'borderColor': 'border-webpage-content',
    'title': 'Web Content'
  },
  'text_content': {
    'icon': '📝',
    'color': 'yellow',
    'bgColor': 'bg-yellow-100',
    'textColor': 'text-yellow-700',
    'borderColor': 'border-text-content',
    'title': 'Text Content'
  },
  'media_content': {
    'icon': '🎵',
    'color': 'red',
    'bgColor': 'bg-red-100',
    'textColor': 'text-red-700',
    'borderColor': 'border-media-content',
    'title': 'Media Content'
  },
  'default': {
    'icon': '📎',
    'color': 'gray',
    'bgColor': 'bg-gray-100',
    'textColor': 'text-gray-700',
    'borderColor': 'border-gray-300',
    'title': 'Unknown Source'
  }
};

// Score thresholds and styling
export const SCORE_STYLES = {
  'high': {
    'threshold': 0.8,
    'textColor': 'text-green-600',
    'bgColor': 'bg-green-50',
    'fontWeight': 'font-bold',
    'description': 'high relevance'
  },
  'medium': {
    'threshold': 0.6,
    'textColor': 'text-yellow-600',
    'bgColor': 'bg-yellow-50',
    'fontWeight': 'font-bold',
    'description': 'medium relevance'
  },
  'low': {
    'threshold': 0.0,
    'textColor': 'text-red-600',
    'bgColor': 'bg-red-50',
    'fontWeight': 'font-bold',
    'description': 'low relevance'
  },
  'default': {
    'textColor': 'text-gray-500',
    'bgColor': 'bg-gray-50',
    'fontWeight': 'font-normal',
    'description': 'N/A'
  }
};

// Table styling
export const TABLE_STYLES = {
  'title': {
    'textColor': 'text-cyan-700',
    'fontWeight': 'font-bold',
    'icon': '📊'
  },
  'header': {
    'bgColor': 'bg-gray-100',
    'textColor': 'text-purple-700',
    'fontWeight': 'font-semibold'
  },
  'border': {
    'color': 'border-blue-200'
  },
  'columns': {
    'score': {
      'width': 'w-20',
      'textAlign': 'text-right'
    },
    'method': {
      'width': 'w-32',
      'textColor': 'text-cyan-600'
    },
    'source': {
      'width': 'w-40',
      'textColor': 'text-yellow-600'
    },
    'content': {
      'width': 'w-96',
      'textColor': 'text-gray-800',
      'overflow': 'overflow-hidden text-ellipsis'
    },
    'video_id': {
      'width': 'w-32',
      'textColor': 'text-yellow-600'
    },
    'segment_id': {
      'width': 'w-24',
      'textColor': 'text-yellow-600'
    },
    'metadata': {
      'width': 'w-40',
      'textColor': 'text-blue-600',
      'overflow': 'overflow-hidden text-ellipsis'
    },
    'start_time': {
      'width': 'w-24',
      'textColor': 'text-cyan-600'
    },
    'end_time': {
      'width': 'w-24',
      'textColor': 'text-cyan-600'
    },
    'watch_url': {
      'width': 'w-full',
      'textColor': 'text-blue-600',
      'overflow': 'overflow-hidden text-ellipsis'
    }
  }
};

// Status and progress indicators
export const STATUS_INDICATORS = {
  'success': '✓',
  'error': '❌',
  'progress': '⏳',
  'pointer': '👉'
};

// Analysis process steps
export const ANALYSIS_STEPS = {
  'start': {
    'icon': '🔍',
    'text': 'Starting Search Results Analysis...',
    'textColor': 'text-cyan-700',
    'fontWeight': 'font-bold'
  },
  'filtering': {
    'icon': '🔎',
    'text': 'Filtering results...',
    'textColor': 'text-cyan-600',
    'fontWeight': 'font-normal'
  },
  'prioritizing': {
    'icon': '⚖️',
    'text': 'Prioritizing results...',
    'textColor': 'text-cyan-600',
    'fontWeight': 'font-normal'
  },
  'preparing': {
    'icon': '📋',
    'text': 'Preparing analysis text...',
    'textColor': 'text-cyan-600',
    'fontWeight': 'font-normal'
  },
  'generating': {
    'icon': '🤖',
    'text': 'Generating AI Analysis...',
    'textColor': 'text-cyan-700',
    'fontWeight': 'font-bold'
  },
  'complete': {
    'icon': '✅',
    'text': 'AI analysis completed',
    'textColor': 'text-green-600',
    'fontWeight': 'font-normal'
  }
};

// Error message templates
export const ERROR_TEMPLATES = {
  'no_results': {
    'icon': STATUS_INDICATORS.error,
    'textColor': 'text-yellow-600',
    'template': "{icon} No results found for {search_type}"
  },
  'search_error': {
    'icon': STATUS_INDICATORS.error,
    'textColor': 'text-red-600',
    'template': "{icon} {search_type} error: {error}"
  },
  'analysis_error': {
    'icon': STATUS_INDICATORS.error,
    'textColor': 'text-red-600',
    'template': "{icon} Analysis error: {error}"
  }
};

// Success message templates
export const SUCCESS_TEMPLATES = {
  'results_found': {
    'icon': STATUS_INDICATORS.success,
    'textColor': 'text-green-600',
    'template': "{icon} Found {count} results"
  },
  'analysis_ready': {
    'icon': STATUS_INDICATORS.success,
    'textColor': 'text-green-600',
    'template': "{icon} Combined results ready for analysis"
  },
  'analysis_complete': {
    'icon': STATUS_INDICATORS.success,
    'textColor': 'text-green-600',
    'template': "{icon} Analysis completed successfully"
  }
};

// Progress stage icons and messages
export const PROGRESS_STAGES = {
  'start': {
    'icon': '🚀',
    'textColor': 'text-cyan-700',
    'fontWeight': 'font-bold',
    'message': 'Starting Search Operation'
  },
  'search': {
    'icon': '🔍',
    'textColor': 'text-yellow-600',
    'fontWeight': 'font-bold',
    'message': 'Executing Search'
  },
  'filter': {
    'icon': '🔍',
    'textColor': 'text-blue-600',
    'fontWeight': 'font-bold',
    'message': 'Filtering Results'
  },
  'combine': {
    'icon': '📊',
    'textColor': 'text-purple-600',
    'fontWeight': 'font-bold',
    'message': 'Combining Results'
  },
  'analyze': {
    'icon': '🤖',
    'textColor': 'text-green-600',
    'fontWeight': 'font-bold',
    'message': 'Analyzing Results'
  },
  'complete': {
    'icon': '✅',
    'textColor': 'text-green-600',
    'fontWeight': 'font-bold',
    'message': 'Operation Complete'
  }
};

// Search method styling
export const SEARCH_METHOD_STYLES = {
  'keyword': {
    'icon': '🔍',
    'bgColor': 'bg-cyan-100',
    'textColor': 'text-cyan-700',
    'borderColor': 'border-cyan-300',
    'title': 'Keyword Search'
  },
  'dot_product': {
    'icon': '🎯',
    'bgColor': 'bg-blue-100',
    'textColor': 'text-blue-700',
    'borderColor': 'border-blue-300',
    'title': 'Dot Product Search'
  },
  'hybrid': {
    'icon': '🔄',
    'bgColor': 'bg-green-100',
    'textColor': 'text-green-700',
    'borderColor': 'border-green-300',
    'title': 'Hybrid Search'
  },
  'default': {
    'icon': '📌',
    'bgColor': 'bg-gray-100',
    'textColor': 'text-gray-700',
    'borderColor': 'border-gray-300',
    'title': 'Unknown Search'
  }
};

/**
 * Get the appropriate score style based on a similarity score
 * @param {number} score - The similarity score (0.0 to 1.0)
 * @returns {Object} - The style object for the score
 */
export function getScoreStyle(score) {
  if (score >= SCORE_STYLES.high.threshold) {
    return SCORE_STYLES.high;
  } else if (score >= SCORE_STYLES.medium.threshold) {
    return SCORE_STYLES.medium;
  } else if (score >= SCORE_STYLES.low.threshold) {
    return SCORE_STYLES.low;
  } else {
    return SCORE_STYLES.default;
  }
}

/**
 * Get the appropriate source style based on a source type
 * @param {string} source - The source type
 * @returns {Object} - The style object for the source
 */
export function getSourceStyle(source) {
  return SOURCE_STYLES[source] || SOURCE_STYLES.default;
}

/**
 * Get the appropriate search method style based on a method type
 * @param {string} method - The search method type
 * @returns {Object} - The style object for the method
 */
export function getMethodStyle(method) {
  return SEARCH_METHOD_STYLES[method] || SEARCH_METHOD_STYLES.default;
}
