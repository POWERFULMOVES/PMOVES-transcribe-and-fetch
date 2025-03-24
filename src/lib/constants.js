export const BACKEND_URL = 'http://127.0.0.1:8000';

// Action types for the reducer
export const ACTIONS = {
  SET_QUERY: 'SET_QUERY',
  SET_TRANSCRIBING: 'SET_TRANSCRIBING',
  ADD_TRANSCRIPTION_SEGMENT: 'ADD_TRANSCRIPTION_SEGMENT',
  CLEAR_TRANSCRIPTION: 'CLEAR_TRANSCRIPTION',
  SET_FILE: 'SET_FILE',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  ADD_STATUS_UPDATE: 'ADD_STATUS_UPDATE',
  CLEAR_STATUS_UPDATES: 'CLEAR_STATUS_UPDATES',
  SET_LOADING: 'SET_LOADING'
};

// Transcription status types
export const TRANSCRIPTION_STATUS = {
  IDLE: 'idle',
  RECORDING: 'recording',
  TRANSCRIBING: 'transcribing',
  COMPLETED: 'completed',
  ERROR: 'error'
};

// Alert types
export const ALERT_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error'
};
