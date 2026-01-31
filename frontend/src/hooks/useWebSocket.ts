/**
 * useWebSocket Hook
 * Manage WebSocket connection and event listening
 */

import { useEffect, useState, useCallback } from 'react'
import { wsClient } from '@services/websocket'
import type { Event } from '@types/index'

export function useWebSocket(eventType?: string) {
  const [connected, setConnected] = useState(false)
  const [events, setEvents] = useState<Event[]>([])

  useEffect(() => {
    // Connect if not already connected
    if (!wsClient.isConnected()) {
      wsClient.connect().catch((error) => {
        console.error('Failed to connect WebSocket:', error)
      })
    }

    // Subscribe to connection changes
    const unsubscribeConnection = wsClient.onConnectionChange((connected) => {
      setConnected(connected)
    })

    // Subscribe to events
    const unsubscribeEvents = wsClient.on(eventType || '*', (event) => {
      setEvents((prev) => [event, ...prev].slice(0, 100)) // Keep last 100 events
    })

    // Set initial connection state
    setConnected(wsClient.isConnected())

    return () => {
      unsubscribeConnection()
      unsubscribeEvents()
    }
  }, [eventType])

  const clearEvents = useCallback(() => {
    setEvents([])
  }, [])

  return { connected, events, clearEvents }
}
