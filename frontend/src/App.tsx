/**
 * SEAA Main Application
 */

import React, { useEffect, useState } from 'react'
import { apiClient } from '@services/api'
import { useAPI } from '@hooks/useAPI'
import { useWebSocket } from '@hooks/useWebSocket'
import { StatusCard } from '@components/StatusCard'
import { OrganList } from '@components/OrganList'
import type { SystemStatus } from '@types/index'
import './App.css'

export function App() {
  const [statusRefreshInterval, setStatusRefreshInterval] = useState<NodeJS.Timeout | null>(null)
  const statusQuery = useAPI(() => apiClient.getStatus(), [])
  const { connected: wsConnected } = useWebSocket()

  // Auto-refresh status every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      statusQuery.refetch()
    }, 5000)
    setStatusRefreshInterval(interval)

    return () => clearInterval(interval)
  }, [statusQuery])

  const status = statusQuery.data as SystemStatus | null

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">SEAA</h1>
          <p className="app-subtitle">Self-Evolving Autonomous Agent</p>
        </div>
        <div className="header-status">
          <div className={`ws-indicator ${wsConnected ? 'connected' : 'disconnected'}`}>
            {wsConnected ? '● Connected' : '● Disconnected'}
          </div>
        </div>
      </header>

      <main className="app-main">
        {statusQuery.loading ? (
          <div className="loading-container">
            <div className="spinner" />
            <p>Loading system status...</p>
          </div>
        ) : statusQuery.error ? (
          <div className="error-container">
            <h2>Error</h2>
            <p>{statusQuery.error.message}</p>
            <button onClick={() => statusQuery.refetch()}>Retry</button>
          </div>
        ) : status ? (
          <>
            <StatusCard identity={status.identity} vitals={status.vitals} />
            <OrganList organs={status.organs} />

            <div className="metrics-grid">
              <div className="metric-card">
                <h3>Goals</h3>
                <div className="metric-value">
                  {status.vitals.goals_satisfied}/{status.vitals.total_goals}
                </div>
                <div className="metric-label">Satisfied</div>
              </div>

              <div className="metric-card">
                <h3>Uptime</h3>
                <div className="metric-value">{formatUptime(status.vitals.uptime_seconds)}</div>
              </div>

              <div className="metric-card">
                <h3>System Health</h3>
                <div className={`metric-value ${status.vitals.sick_organs === 0 ? 'healthy' : 'degraded'}`}>
                  {status.vitals.sick_organs === 0 ? 'HEALTHY' : 'DEGRADED'}
                </div>
              </div>
            </div>
          </>
        ) : null}
      </main>
    </div>
  )
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (days > 0) return `${days}d ${hours}h`
  if (hours > 0) return `${hours}h ${minutes}m`
  if (minutes > 0) return `${minutes}m ${secs}s`
  return `${secs}s`
}

export default App
