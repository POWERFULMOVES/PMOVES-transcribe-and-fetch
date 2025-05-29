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
    if (state.isFetching || (state.hasInitialFetch && state.count > 0 && state.count <= state.data.length)) {
      console.log('[useInfiniteQuery] fetchPage: SKIPPING fetch. isFetching:', state.isFetching, 'hasInitialFetch:', state.hasInitialFetch, 'count:', state.count, 'data.length:', state.data.length);
      return;
    }
    console.log('[useInfiniteQuery] fetchPage: Called. skip:', skip, 'current data.length:', state.data.length, 'current count:', state.count);

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
      console.error('[useInfiniteQuery] fetchPage: An unexpected error occurred:', error)
      setState({ error })
    } else {
      console.log('[useInfiniteQuery] fetchPage: Fetched data. Received count:', count, 'newData items:', newData ? newData.length : 0);
      const deduplicatedData = ((newData || [])).filter((item) => !state.data.find((old) => old.id === item.id))

      setState({
        data: [...state.data, ...deduplicatedData],
        count: count || 0, // Ensure count is updated based on Supabase response
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
    console.log('[useInfiniteQuery] initialize: Called. newProps:', newProps);
    // Update store's internal filters/sortOptions if new ones are passed
    if (newProps && newProps.filters) { // Check if newProps and filters exist
        setState({
            currentFilters: newProps.filters,
        });
    }
    if (newProps && newProps.sortOptions) { // Check if newProps and sortOptions exist
         setState({
            currentSortOptions: newProps.sortOptions,
        });
    }
    setState({ isLoading: true, isSuccess: false, data: [], count: 0, error: null, hasInitialFetch: false }) // Reset data and count
    await fetchPage(0) // Fetch first page
    setState({ isLoading: false, hasInitialFetch: true })
    console.log('[useInfiniteQuery] initialize: Finished.');
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
    
    console.log('[useInfiniteQuery] useEffect: Running. hasInitialFetch:', state.hasInitialFetch);
    console.log('[useInfiniteQuery] useEffect: Current props.filters:', JSON.stringify(propsFilters));
    console.log('[useInfiniteQuery] useEffect: Current store.currentFilters:', JSON.stringify(currentStoreState.currentFilters));
    console.log('[useInfiniteQuery] useEffect: Current props.sortOptions:', JSON.stringify(propsSortOptions));
    console.log('[useInfiniteQuery] useEffect: Current store.currentSortOptions:', JSON.stringify(currentStoreState.currentSortOptions));

    const filtersChanged = JSON.stringify(propsFilters) !== JSON.stringify(currentStoreState.currentFilters);
    const sortOptionsChanged = JSON.stringify(propsSortOptions) !== JSON.stringify(currentStoreState.currentSortOptions);

    // Check if tableName, columns, pageSize have changed or if filters/sortOptions have actually changed
    // We also need to consider if the store itself was just created and needs its internal props set.
    const fundamentalPropsChanged = props.tableName !== (currentStoreState._internalTableName || props.tableName) ||
                                 props.columns !== (currentStoreState._internalColumns || props.columns) ||
                                 props.pageSize !== (currentStoreState._internalPageSize || props.pageSize);

    if (fundamentalPropsChanged || filtersChanged || sortOptionsChanged) {
      console.log('[useInfiniteQuery] useEffect: Condition to re-create store MET. FundamentalPropsChanged:', fundamentalPropsChanged, 'FiltersChanged:', filtersChanged, 'SortOptionsChanged:', sortOptionsChanged);
      // If fundamental props like tableName change, or if filters/sort change, re-create and initialize.
      // We pass the latest props to createStore.
      storeRef.current = createStore({
        ...props, // Pass all current props through
        filters: propsFilters,
        sortOptions: propsSortOptions,
        // Store original props for comparison in the new store instance
        _internalTableName: props.tableName,
        _internalColumns: props.columns,
        _internalPageSize: props.pageSize,
      });
      // Initialize the new store with the current filters and sort options
      storeRef.current.initialize({ filters: propsFilters, sortOptions: propsSortOptions });
    } else if (!state.hasInitialFetch && typeof window !== 'undefined') {
      console.log('[useInfiniteQuery] useEffect: Condition for INITIAL fetch MET (state.hasInitialFetch is false).');
      // Initial fetch if not already done, and we are on the client side
      storeRef.current.initialize({ filters: propsFilters, sortOptions: propsSortOptions });
    } else {
      console.log('[useInfiniteQuery] useEffect: NO condition met to re-create store or perform initial fetch.');
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
