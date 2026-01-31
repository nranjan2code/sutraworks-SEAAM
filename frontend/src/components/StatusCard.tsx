/**
 * StatusCard Component
 * Display system status overview
 */

import React from 'react'
import type { Vitals, Identity } from '@types/index'
import './StatusCard.css'

interface StatusCardProps {
  identity: Identity
  vitals: Vitals
}

export const StatusCard: React.FC<StatusCardProps> = ({ identity, vitals }) => {
  const healthStatus = vitals.sick_organs > 0 ? 'degraded' : 'healthy'
  const healthClass = healthStatus === 'healthy' ? 'status-healthy' : 'status-degraded'

  return (
    <div className="status-card">
      <div className="status-header">
        <h1 className="instance-name">{identity.name}</h1>
        <div className={`health-badge ${healthClass}`}>{healthStatus.toUpperCase()}</div>
      </div>

      <div className="status-grid">
        <div className="status-item">
          <label>ID</label>
          <code>{identity.shortId}</code>
        </div>
        <div className="status-item">
          <label>DNA</label>
          <code>{vitals.dna_hash.substring(0, 12)}...</code>
        </div>
        <div className="status-item">
          <label>Organs</label>
          <span>
            {vitals.healthy_organs}/{vitals.organ_count}
          </span>
        </div>
        <div className="status-item">
          <label>Goals</label>
          <span>
            {vitals.goals_satisfied}/{vitals.total_goals}
          </span>
        </div>
        <div className="status-item">
          <label>Uptime</label>
          <span>{formatUptime(vitals.uptime_seconds)}</span>
        </div>
      </div>
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
