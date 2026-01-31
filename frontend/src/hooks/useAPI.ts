/**
 * useAPI Hook
 * Handle API calls with loading and error states
 */

import { useState, useCallback, useEffect } from 'react'

interface UseAPIState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

export function useAPI<T>(
  fetchFn: () => Promise<T>,
  dependencies: React.DependencyList = []
): UseAPIState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseAPIState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  const refetch = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true }))
    try {
      const data = await fetchFn()
      setState({ data, loading: false, error: null })
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error(String(error)),
      })
    }
  }, [fetchFn])

  useEffect(() => {
    refetch()
  }, dependencies)

  return { ...state, refetch }
}
