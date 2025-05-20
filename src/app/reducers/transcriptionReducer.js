export const ACTIONS = {
  SET_YOUTUBE_URL: 'SET_YOUTUBE_URL',
  SET_OBSIDIAN_DIR: 'SET_OBSIDIAN_DIR',
  SET_OUTPUT_FOLDER: 'SET_OUTPUT_FOLDER',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_PROCESS_RESULT: 'SET_PROCESS_RESULT',
  SET_TRANSCRIBING: 'SET_TRANSCRIBING',
  ADD_STATUS_UPDATE: 'ADD_STATUS_UPDATE',
  SET_ACTIVE_STEP: 'SET_ACTIVE_STEP',
  RESET_TRANSCRIPTION: 'RESET_TRANSCRIPTION',
  SET_TRANSCRIPTION_MODEL: 'SET_TRANSCRIPTION_MODEL',
  SET_TAB_VALUE: 'SET_TAB_VALUE',
  SET_FETCH_URL: 'SET_FETCH_URL',
  SET_FETCH_RESULT: 'SET_FETCH_RESULT',
  SET_JSON_RESPONSE: 'SET_JSON_RESPONSE',
  SET_TARGET_SELECTOR: 'SET_TARGET_SELECTOR',
  ADD_TRANSCRIPTION_SEGMENT: 'ADD_TRANSCRIPTION_SEGMENT',
  SET_COMPLETED_TRANSCRIPTION: 'SET_COMPLETED_TRANSCRIPTION',
  SET_DEVICE_INFO: 'SET_DEVICE_INFO',
  SET_WHISPER_MODEL_SIZE: 'SET_WHISPER_MODEL_SIZE',
  SET_DRAWER_OPEN: 'SET_DRAWER_OPEN',
  SET_TIMEOUT: 'SET_TIMEOUT',
  SET_EXCLUDED_SELECTOR: 'SET_EXCLUDED_SELECTOR',
  SET_CLEAN_FORMAT: 'SET_CLEAN_FORMAT',
  SET_SHOULD_DISCONNECT: 'SET_SHOULD_DISCONNECT',
  ADD_MULTIPLE_TRANSCRIPTION_SEGMENTS: 'ADD_MULTIPLE_TRANSCRIPTION_SEGMENTS',
  SET_VIDEO_METADATA: 'SET_VIDEO_METADATA', // Added action
  SET_FULL_TRANSCRIPTION_DATA: 'SET_FULL_TRANSCRIPTION_DATA', // For completed view
  FINALIZE_TRANSCRIPTION: 'FINALIZE_TRANSCRIPTION' // To construct fullText from existing segments
};
 
// Helper to get config from window if available (for SSR/CSR compatibility)
function getInitialConfigValue(key, fallback) {
  if (typeof window !== 'undefined' && window.__APP_CONFIG__ && window.__APP_CONFIG__[key]) {
    return window.__APP_CONFIG__[key];
  }
  return fallback;
}

export const initialState = {
  videoMetadata: null,
  youtubeUrl: '',
  obsidianDir: getInitialConfigValue('DEFAULT_OBSIDIAN_DIR', 'J:\\My Drive\\CataclysmstudiosInc\\POWERFULMOVES\\005 - Transcriptions'),
  outputFolder: getInitialConfigValue('DEFAULT_OUTPUT_FOLDER', 'M:\\PMOVEStransciber\\output'),
  loading: false,
  error: null,
  processResult: {},
  transcribing: false,
  statusUpdates: [],
  transcriptionSegments: [], // Live segments during transcription
  transcriptionData: { // For completed transcription view
    segments: [],
    fullText: "",
    // Potentially other metadata like speaker map later
  },
  activeStep: 0,
  transcriptionModel: 'faster-whisper',
  tabValue: 'status',
  fetchUrl: '',
  fetchResult: null,
  jsonResponse: false,
  targetSelector: '',
  // completedTranscription: null, // Replaced by transcriptionData
  deviceInfo: null,
  whisperModelSize: 'large-v3',
  drawerOpen: false,
  timeout: 300,
  elapsedTime: 0,
  excludedSelector: '',
  cleanFormat: true,
  shouldDisconnect: false,
};

export function transcriptionReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_VIDEO_METADATA: // Added case
      return { ...state, videoMetadata: action.payload };
    case ACTIONS.SET_YOUTUBE_URL:
      return { ...state, youtubeUrl: action.payload };
    case ACTIONS.SET_OBSIDIAN_DIR:
      return { ...state, obsidianDir: action.payload };
    case ACTIONS.SET_OUTPUT_FOLDER:
      return { ...state, outputFolder: action.payload };
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload };
    case ACTIONS.SET_PROCESS_RESULT:
      return { ...state, processResult: action.payload };
    case ACTIONS.SET_TRANSCRIBING:
      return { ...state, transcribing: action.payload };
    case ACTIONS.ADD_STATUS_UPDATE:
      // Check if this is a transcription segment status update
      if (typeof action.payload === 'string' && action.payload.includes('Transcribing segment')) {
        // For transcription segment updates, only keep the latest one
        const filteredUpdates = state.statusUpdates.filter(update =>
          typeof update !== 'string' || !update.includes('Transcribing segment')
        );
        return {
          ...state,
          statusUpdates: [...filteredUpdates, action.payload]
        };
      }

      // For other updates, check for exact duplicates
      if (state.statusUpdates.includes(action.payload)) {
        return state; // Don't add duplicate
      }

      // Limit the number of status updates to prevent performance issues
      const maxStatusUpdates = 100;
      const newStatusUpdates = [...state.statusUpdates, action.payload];
      return {
        ...state,
        statusUpdates: newStatusUpdates.length > maxStatusUpdates
          ? newStatusUpdates.slice(-maxStatusUpdates)
          : newStatusUpdates
      };
    case ACTIONS.SET_ACTIVE_STEP:
      return {
        ...state,
        activeStep: action.payload
      };
    case ACTIONS.RESET_TRANSCRIPTION:
      console.log('[transcriptionReducer] RESET_TRANSCRIPTION action called');
      return {
        ...state,
        transcriptionSegments: [], // For live updates
        transcriptionData: { // For completed view
          segments: [],
          fullText: "",
        },
        statusUpdates: [],
        error: null,
        processResult: {},
        activeStep: 0,
        videoMetadata: null, // Reset video metadata
        // Don't reset transcribing here - it should be managed separately
        // Don't reset loading here - it should be managed separately
      };
    case ACTIONS.SET_TRANSCRIPTION_MODEL:
      return { ...state, transcriptionModel: action.payload };
    case ACTIONS.SET_TAB_VALUE:
      return { ...state, tabValue: action.payload };
    case ACTIONS.SET_FETCH_URL:
      return { ...state, fetchUrl: action.payload };
    case ACTIONS.SET_FETCH_RESULT:
      return { ...state, fetchResult: action.payload };
    case ACTIONS.SET_JSON_RESPONSE:
      return { ...state, jsonResponse: action.payload };
    case ACTIONS.SET_TARGET_SELECTOR:
      return { ...state, targetSelector: action.payload };
    case ACTIONS.ADD_TRANSCRIPTION_SEGMENT:
      // Ensure we're not adding duplicate segments
      const newSegment = action.payload;

      // Skip empty segments
      if (!newSegment || !newSegment.text) {
        return state;
      }

      // Use ID-based duplicate checking for better performance
      const isDuplicate = state.transcriptionSegments.some(
        segment => segment.id === newSegment.id
      );

      if (isDuplicate) {
        return state;
      }

      // Add the new segment (without sorting)
      return {
        ...state,
        transcriptionSegments: [...state.transcriptionSegments, newSegment],
        // Also update transcriptionData.segments if the job is already considered complete,
        // though ideally segments arrive before completion signal.
        transcriptionData: {
          ...state.transcriptionData,
          segments: state.activeStep === 3 ? [...state.transcriptionData.segments, newSegment].sort((a, b) => a.start_time - b.start_time) : state.transcriptionData.segments,
        }
      };
    // This action might be deprecated in favor of SET_FULL_TRANSCRIPTION_DATA
    // For now, it can set the fullText part of transcriptionData
    case ACTIONS.SET_COMPLETED_TRANSCRIPTION: // Legacy or for full text only
      return {
        ...state,
        transcriptionData: {
          ...state.transcriptionData,
          fullText: action.payload, // Assuming payload is the full text string
          // Segments would be populated by ADD_MULTIPLE_TRANSCRIPTION_SEGMENTS or SET_FULL_TRANSCRIPTION_DATA
        },
        transcribing: false // Mark as not transcribing
      };
    case ACTIONS.SET_DEVICE_INFO:
      return { ...state, deviceInfo: action.payload };
    case ACTIONS.SET_WHISPER_MODEL_SIZE:
      return { ...state, whisperModelSize: action.payload };
    case ACTIONS.SET_DRAWER_OPEN:
      return { ...state, drawerOpen: action.payload };
    case ACTIONS.SET_TIMEOUT:
      return { ...state, timeout: action.payload };
    case ACTIONS.SET_EXCLUDED_SELECTOR:
      return { ...state, excludedSelector: action.payload };
    case ACTIONS.SET_CLEAN_FORMAT:
      return { ...state, cleanFormat: action.payload };
    case ACTIONS.SET_SHOULD_DISCONNECT:
      return { ...state, shouldDisconnect: action.payload };
    case ACTIONS.ADD_MULTIPLE_TRANSCRIPTION_SEGMENTS: {
      const newSegments = action.payload || [];
      // Filter out potential duplicates from the incoming batch and compared to existing state
      const existingIds = new Set(state.transcriptionSegments.map(s => s.id));
      const uniqueNewSegments = newSegments.filter(segment => segment && segment.id !== undefined && !existingIds.has(segment.id));

      if (uniqueNewSegments.length === 0) {
        return state; // No new unique segments to add
      }

      return {
        ...state,
        // Update live segments
        transcriptionSegments: [...state.transcriptionSegments, ...uniqueNewSegments]
          .sort((a, b) => (a.start_time || a.start_seconds || 0) - (b.start_time || b.start_seconds || 0)),
        // Also update transcriptionData.segments if the job is already considered complete,
        // or if these are the final segments.
        transcriptionData: {
          ...state.transcriptionData,
          segments: state.activeStep === 3
            ? [...state.transcriptionData.segments, ...uniqueNewSegments].sort((a, b) => (a.start_time || a.start_seconds || 0) - (b.start_time || b.start_seconds || 0))
            : state.transcriptionData.segments,
        }
      };
    }
    case ACTIONS.SET_FULL_TRANSCRIPTION_DATA:
      // This action receives the complete data package.
      // It should set both the segments and fullText for the completed view.
      // It also implies transcription is complete.
      const { segments: finalSegments, fullText: finalFullText } = action.payload;
      const sortedFinalSegments = finalSegments
        ? [...finalSegments].sort((a, b) => (a.start_time || a.start_seconds || 0) - (b.start_time || b.start_seconds || 0))
        : [];

      return {
        ...state,
        transcriptionData: {
          segments: sortedFinalSegments,
          fullText: finalFullText || state.transcriptionData.fullText || "", // Use provided, or existing, or empty
        },
        // Optionally, update live transcriptionSegments to match the final ones
        // This ensures consistency if live updates were slightly different or incomplete.
        transcriptionSegments: sortedFinalSegments,
        transcribing: false, // Mark as not transcribing
        loading: false, // Ensure loading is false
        activeStep: 3, // Ensure step is 'Transcription Complete'
      };
    case ACTIONS.FINALIZE_TRANSCRIPTION: {
      // This action is called when 'transcription_complete' is received from SSE,
      // and the frontend needs to construct the fullText from the accumulated segments.
      const sortedSegments = [...state.transcriptionSegments].sort(
        (a, b) => (a.start_time || a.start_seconds || 0) - (b.start_time || b.start_seconds || 0)
      );
      const constructedFullText = sortedSegments.map(segment => segment.text).join(' '); // Join with space, or newline if preferred

      return {
        ...state,
        transcriptionData: {
          segments: sortedSegments,
          fullText: constructedFullText,
        },
        transcriptionSegments: sortedSegments, // Ensure live segments also reflect the final sorted list
        transcribing: false,
        loading: false,
        activeStep: 3, // Ensure step is 'Transcription Complete'
      };
    }
    default:
      return state;
  }
}
 
// Helper functions
export const validateYoutubeUrl = (url) => {
  const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;
  return pattern.test(url);
};

export const validateObsidianDir = (dir) => {
  return dir && dir.trim().length > 0;
};

export const sanitizeInput = (input) => {
  return input.trim();
};
