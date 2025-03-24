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
  SET_CLEAN_FORMAT: 'SET_CLEAN_FORMAT'
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
  cleanFormat: true
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
      return {
        ...state,
        statusUpdates: [...state.statusUpdates, action.payload]
      };
    case ACTIONS.SET_ACTIVE_STEP:
      return {
        ...state,
        activeStep: action.payload
      };
    case ACTIONS.RESET_TRANSCRIPTION:
      return { 
        ...state, 
        transcriptionSegments: [], 
        completedTranscription: null,
        statusUpdates: [],
        error: null 
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
      // Skip empty segments
      if (!action.payload || action.payload.trim() === '') {
        return state;
      }
      
      // Get the cleaned segment text
      const formattedSegment = action.payload.trim();
      
      // First check for exact duplicates to prevent redundancy
      if (state.transcriptionSegments.some(segment => segment === formattedSegment)) {
        return state;
      }
      
      // Handle continuous speech with partial updates
      if (state.transcriptionSegments.length > 0) {
        const lastSegment = state.transcriptionSegments[state.transcriptionSegments.length - 1];
        
        // If the new segment completely contains the previous one (incremental update)
        if (formattedSegment.includes(lastSegment)) {
          return {
            ...state,
            transcriptionSegments: [
              ...state.transcriptionSegments.slice(0, -1),
              formattedSegment
            ]
          };
        }
        
        // If this is clearly a new sentence starting (previous ends with ending punctuation)
        const lastChar = lastSegment.trim().slice(-1);
        if (['.', '!', '?', '...'].includes(lastChar)) {
          return {
            ...state,
            transcriptionSegments: [...state.transcriptionSegments, formattedSegment]
          };
        }
        
        // Check for overlaps - the last few words of the previous segment match the first few of the new one
        const lastWords = lastSegment.split(' ').slice(-3).join(' '); // Get last 3 words
        if (formattedSegment.startsWith(lastWords) && lastWords.length > 10) { // Only if meaningful overlap
          const combinedSegment = lastSegment + formattedSegment.substring(lastWords.length);
          return {
            ...state,
            transcriptionSegments: [
              ...state.transcriptionSegments.slice(0, -1),
              combinedSegment
            ]
          };
        }
      }
      
      // Add as a new segment for other cases
      return {
        ...state,
        transcriptionSegments: [...state.transcriptionSegments, formattedSegment]
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