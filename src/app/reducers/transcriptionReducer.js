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
  ADD_MULTIPLE_TRANSCRIPTION_SEGMENTS: 'ADD_MULTIPLE_TRANSCRIPTION_SEGMENTS'
};

export const initialState = {
  youtubeUrl: '',
  obsidianDir: 'J:\\My Drive\\CataclysmstudiosInc\\POWERFULMOVES\\005 - Transcriptions',
  outputFolder: 'M:\\PMOVEStransciber\\output',
  loading: false,
  error: null,
  processResult: {},
  transcribing: false,
  statusUpdates: [],
  transcriptionSegments: [],
  activeStep: 0,
  transcriptionModel: 'faster-whisper',
  tabValue: 'status',
  fetchUrl: '',
  fetchResult: null,
  jsonResponse: false,
  targetSelector: '',
  completedTranscription: null,
  deviceInfo: null,
  whisperModelSize: 'large-v3',
  drawerOpen: false,
  timeout: 300,
  elapsedTime: 0,
  excludedSelector: '',
  cleanFormat: true,
  shouldDisconnect: false
};

export function transcriptionReducer(state, action) {
  switch (action.type) {
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
        transcriptionSegments: [],
        completedTranscription: null,
        statusUpdates: [],
        error: null,
        processResult: {},
        activeStep: 0,
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
        transcriptionSegments: [...state.transcriptionSegments, newSegment]
      };
    case ACTIONS.SET_COMPLETED_TRANSCRIPTION:
      return {
        ...state,
        completedTranscription: action.payload,
        transcribing: false
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
        transcriptionSegments: [...state.transcriptionSegments, ...uniqueNewSegments]
          .sort((a, b) => a.start_seconds - b.start_seconds), // Keep sorted
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
