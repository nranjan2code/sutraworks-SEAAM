/**
 * SEAA Frontend Types
 * Shared TypeScript types for the SEAA system
 */

export interface Identity {
  id: string
  name: string
  shortId: string
  genesis: string
  lineage: string
}

export interface Vitals {
  uptime_seconds: number
  dna_hash: string
  organ_count: number
  healthy_organs: number
  sick_organs: number
  goals_satisfied: number
  total_goals: number
}

export interface OrganInfo {
  name: string
  health: 'healthy' | 'degraded' | 'dead'
  status: 'active' | 'pending' | 'failed'
  attempts: number
  version: number
  created_at: string
  updated_at: string
}

export interface GoalInfo {
  description: string
  priority: number
  satisfied: boolean
  required_organs: string[]
  matching_organs: string[]
  created_at: string
}

export interface SystemStatus {
  identity: Identity
  vitals: Vitals
  organs: OrganInfo[]
  goals: GoalInfo[]
}

export interface Event {
  event_type: string
  timestamp: string
  data: Record<string, any>
  source?: string
}

export interface TimelineEntry {
  type: 'designed' | 'integrated' | 'failure' | 'evolution'
  timestamp: string
  organ: string
  message?: string
}

export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
  timestamp: string
}
