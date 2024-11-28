export const ACTIONS = {
  SET_ERROR: 'SET_ERROR',
  SET_LOADING: 'SET_LOADING',
  ADD_STATUS_UPDATE: 'ADD_STATUS_UPDATE',
  RESET_STATUS: 'RESET_STATUS',
  SET_DOWNLOADING: 'SET_DOWNLOADING',
  UPDATE_PROGRESS: 'UPDATE_PROGRESS',
};

export const initialState = {
  statusUpdates: [],
  downloading: false,
  error: null,
  loading: false,
  currentProgress: null
};

export const downloadReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false,
        downloading: false
      };
    case ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
        error: null
      };
    case ACTIONS.ADD_STATUS_UPDATE:
      return {
        ...state,
        statusUpdates: [...state.statusUpdates, action.payload]
      };
    case ACTIONS.RESET_STATUS:
      return {
        ...state,
        statusUpdates: [],
        currentProgress: null,
        error: null
      };
    case ACTIONS.SET_DOWNLOADING:
      return {
        ...state,
        downloading: action.payload
      };
    case ACTIONS.UPDATE_PROGRESS:
      return {
        ...state,
        currentProgress: action.payload
      };
    default:
      return state;
  }
};
