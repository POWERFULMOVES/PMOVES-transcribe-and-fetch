import { transcriptionReducer, initialState, ACTIONS } from '../reducers/transcriptionReducer';

describe('transcriptionReducer', () => {
  it('should add a new transcription segment', () => {
    const segment = { id: 1, text: 'hello', start_time: 0, end_time: 1 };
    const state = transcriptionReducer(initialState, {
      type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT,
      payload: segment,
    });
    expect(state.transcriptionSegments).toHaveLength(1);
    expect(state.transcriptionSegments[0].text).toBe('hello');
  });

  it('should not add a duplicate segment', () => {
    const segment = { id: 1, text: 'hello', start_time: 0, end_time: 1 };
    let state = transcriptionReducer(initialState, {
      type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT,
      payload: segment,
    });
    state = transcriptionReducer(state, {
      type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT,
      payload: segment,
    });
    expect(state.transcriptionSegments).toHaveLength(1);
  });

  it('should skip empty segment', () => {
    const segment = { id: 2, text: '', start_time: 0, end_time: 1 };
    const state = transcriptionReducer(initialState, {
      type: ACTIONS.ADD_TRANSCRIPTION_SEGMENT,
      payload: segment,
    });
    expect(state.transcriptionSegments).toHaveLength(0);
  });
});
