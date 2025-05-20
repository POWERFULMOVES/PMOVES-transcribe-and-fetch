'use client';
import { createClient } from '@/lib/client';
import { useEffect, useRef, useSyncExternalStore } from 'react'

const supabase = createClient();

function createStore(props) {
  const { tableName, columns = '*', pageSize = 20, trailingQuery, filters = {}, sortOptions = { column: 'fetch_date', ascending: false } } = props

  let state = {
    data: [],
    count: 0,
    isSuccess: false,
    isLoading: false,
    isFetching: false,
    error: null,
    hasInitialFetch: false,
    // Store current filters and sortOptions to detect changes
    currentFilters: filters,
    currentSortOptions: sortOptions,
  }

  const listeners = new Set()

  const notify = () => {
    listeners.forEach((listener) => listener())
  }

  const setState = (newState) => {
    state = { ...state, ...newState }
    notify()
  }

  const fetchPage = async (skip) => {
    // Prevent fetching if already fetching, or if initial fetch done and no more items
    if (state.isFetching || (state.hasInitialFetch && state.count <= state.data.length)) {
      return;
    }

    setState({ isFetching: true })

    let query = supabase
      .from(tableName)
      .select(columns, { count: 'exact' })

    // Apply filters
    if (state.currentFilters.engine && state.currentFilters.engine !== "all_engines") {
      query = query.eq('fetching_engine', state.currentFilters.engine);
    }
    if (state.currentFilters.status && state.currentFilters.status !== "all_statuses") {
      query = query.eq('status', state.currentFilters.status);
    }
    if (state.currentFilters.searchTerm) {
      const searchTerm = `%${state.currentFilters.searchTerm}%`;
      query = query.or(`url.ilike.${searchTerm},title.ilike.${searchTerm}`);
    }

    // Apply sorting
    if (state.currentSortOptions && state.currentSortOptions.column) {
      query = query.order(state.currentSortOptions.column, { ascending: state.currentSortOptions.ascending });
    } else if (trailingQuery) { // Fallback to trailingQuery if new sortOptions not provided
      query = trailingQuery(query);
    }
    // Default sort if nothing else is specified (e.g. initial load without specific sort)
    // This was previously handled by trailingQuery in page.js, now more explicit here or via default sortOptions
    if (!(state.currentSortOptions && state.currentSortOptions.column) && !trailingQuery) {
        query = query.order('fetch_date', { ascending: false });
    }


    const { data: newData, count, error } = await query.range(skip, skip + pageSize - 1)

    if (error) {
      console.error('An unexpected error occurred:', error)
      setState({ error })
    } else {
      const deduplicatedData = ((newData || [])).filter((item) => !state.data.find((old) => old.id === item.id))

      setState({
        data: [...state.data, ...deduplicatedData],
        count: count || 0,
        isSuccess: true,
        error: null,
      })
    }
    setState({ isFetching: false })
  }

  const fetchNextPage = async () => {
    if (state.isFetching) return
    await fetchPage(state.data.length)
  }

  const initialize = async (newProps) => {
    // Update store's internal filters/sortOptions if new ones are passed
    if (newProps) {
        setState({
            currentFilters: newProps.filters || {},
            currentSortOptions: newProps.sortOptions || { column: 'fetch_date', ascending: false },
        });
    }
    setState({ isLoading: true, isSuccess: false, data: [], count: 0, error: null, hasInitialFetch: false }) // Reset data and count
    await fetchPage(0) // Fetch first page
    setState({ isLoading: false, hasInitialFetch: true })
  }
  
  // Expose a way to update filters/sort and re-fetch
  const setQueryOptions = (newFilters, newSortOptions) => {
    const currentStoreState = storeRef.current.getState();
    let filtersChanged = JSON.stringify(newFilters) !== JSON.stringify(currentStoreState.currentFilters);
    let sortOptionsChanged = JSON.stringify(newSortOptions) !== JSON.stringify(currentStoreState.currentSortOptions);

    if (filtersChanged || sortOptionsChanged) {
        storeRef.current = createStore({ ...props, filters: newFilters, sortOptions: newSortOptions });
        storeRef.current.initialize({ filters: newFilters, sortOptions: newSortOptions });
    }
  };


  return {
    getState: () => state,
    subscribe: (listener) => {
      listeners.add(listener)
      return () => listeners.delete(listener);
    },
    fetchNextPage,
    initialize,
    setQueryOptions, // Expose this
  };
}

// Empty initial state to avoid hydration errors.
const initialState = {
  data: [],
  count: 0,
  isSuccess: false,
  isLoading: false,
  isFetching: false,
  error: null,
  hasInitialFetch: false,
  currentFilters: {},
  currentSortOptions: { column: 'fetch_date', ascending: false },
}

function useInfiniteQuery(props) {
  // Initialize storeRef with props including filters and sortOptions
  const storeRef = useRef(createStore({
    ...props,
    filters: props.filters || {},
    sortOptions: props.sortOptions || { column: 'fetch_date', ascending: false }
  }));

  const state = useSyncExternalStore(
    storeRef.current.subscribe,
    () => storeRef.current.getState(),
    () => storeRef.current.getState()  // Use the store's actual initial state for server snapshot
  )

  useEffect(() => {
    const currentStoreState = storeRef.current.getState();
    const propsFilters = props.filters || {};
    const propsSortOptions = props.sortOptions || { column: 'fetch_date', ascending: false };

    // Check if tableName, columns, pageSize, filters, or sortOptions have changed
    if (
      // Basic prop changes that require full store re-creation
      props.tableName !== storeRef.current.getState()._internalTableName || // Assuming we store original props in state
      props.columns !== storeRef.current.getState()._internalColumns ||
      props.pageSize !== storeRef.current.getState()._internalPageSize ||
      // Filter or sort changes
      JSON.stringify(propsFilters) !== JSON.stringify(currentStoreState.currentFilters) ||
      JSON.stringify(propsSortOptions) !== JSON.stringify(currentStoreState.currentSortOptions)
    ) {
      // If fundamental props like tableName change, or if filters/sort change, re-create and initialize.
      // We pass the latest props to createStore.
      storeRef.current = createStore({
        ...props,
        filters: propsFilters,
        sortOptions: propsSortOptions,
        // Store original props for comparison
        _internalTableName: props.tableName,
        _internalColumns: props.columns,
        _internalPageSize: props.pageSize,
      });
      storeRef.current.initialize({ filters: propsFilters, sortOptions: propsSortOptions });
    } else if (!state.hasInitialFetch && typeof window !== 'undefined') {
      // Initial fetch if not already done
      storeRef.current.initialize({ filters: propsFilters, sortOptions: propsSortOptions });
    }
  }, [props.tableName, props.columns, props.pageSize, props.filters, props.sortOptions, state.hasInitialFetch]);


  return {
    data: state.data,
    count: state.count,
    isSuccess: state.isSuccess,
    isLoading: state.isLoading,
    isFetching: state.isFetching,
    error: state.error,
    hasMore: state.count > state.data.length,
    fetchNextPage: storeRef.current.fetchNextPage,
    initialize: (reinitProps) => storeRef.current.initialize(reinitProps || props), // Allow re-initializing with new or existing props
    // Expose setQueryOptions if direct manipulation is preferred over useEffect dependency changes
    // setQueryOptions: (filters, sortOptions) => storeRef.current.setQueryOptions(filters, sortOptions),
  }
}

export { useInfiniteQuery };
