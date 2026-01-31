/**
 * OrganList Component
 * Display all organs and their health status
 */

import React from 'react'
import type { OrganInfo } from '@types/index'
import './OrganList.css'

interface OrganListProps {
  organs: OrganInfo[]
  loading?: boolean
}

export const OrganList: React.FC<OrganListProps> = ({ organs, loading = false }) => {
  if (loading) {
    return <div className="loading">Loading organs...</div>
  }

  if (organs.length === 0) {
    return <div className="empty-state">No organs yet</div>
  }

  return (
    <div className="organ-list">
      <h2>Organs</h2>
      <table className="organ-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Health</th>
            <th>Version</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {organs.map((organ) => (
            <tr key={organ.name} className={`organ-row organ-${organ.health}`}>
              <td className="organ-name">
                <span className={`status-dot status-${organ.status}`} />
                {organ.name}
              </td>
              <td className="organ-status">{organ.status}</td>
              <td className={`organ-health health-${organ.health}`}>{organ.health}</td>
              <td className="organ-version">v{organ.version}</td>
              <td className="organ-created">{formatDate(organ.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days > 0) return `${days}d ago`

  const hours = Math.floor(diff / (1000 * 60 * 60))
  if (hours > 0) return `${hours}h ago`

  const minutes = Math.floor(diff / (1000 * 60))
  return `${minutes}m ago`
}
