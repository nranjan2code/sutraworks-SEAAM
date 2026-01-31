/**
 * SEAA API Client
 * Handles communication with Python backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  SystemStatus,
  Identity,
  Vitals,
  OrganInfo,
  GoalInfo,
  TimelineEntry,
  APIResponse,
} from '@types/index'

class APIClient {
  private client: AxiosInstance
  private baseURL: string

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response.data,
      (error: AxiosError) => {
        console.error('API Error:', error.message)
        throw error
      }
    )
  }

  /**
   * Get complete system status
   */
  async getStatus(): Promise<SystemStatus> {
    return this.client.get<APIResponse<SystemStatus>>('/status')
  }

  /**
   * Get system identity
   */
  async getIdentity(): Promise<Identity> {
    const response = await this.client.get<APIResponse<Identity>>('/identity')
    return response.data!
  }

  /**
   * Get system vitals
   */
  async getVitals(): Promise<Vitals> {
    const response = await this.client.get<APIResponse<Vitals>>('/vitals')
    return response.data!
  }

  /**
   * Get list of organs
   */
  async getOrgans(): Promise<OrganInfo[]> {
    const response = await this.client.get<APIResponse<OrganInfo[]>>('/organs')
    return response.data!
  }

  /**
   * Get list of goals
   */
  async getGoals(): Promise<GoalInfo[]> {
    const response = await this.client.get<APIResponse<GoalInfo[]>>('/goals')
    return response.data!
  }

  /**
   * Get evolution timeline
   */
  async getTimeline(limit: number = 20): Promise<TimelineEntry[]> {
    const response = await this.client.get<APIResponse<TimelineEntry[]>>(
      `/timeline?limit=${limit}`
    )
    return response.data!
  }

  /**
   * Get failures
   */
  async getFailures(): Promise<any[]> {
    const response = await this.client.get<APIResponse<any[]>>('/failures')
    return response.data!
  }

  /**
   * Start genesis
   */
  async startGenesis(): Promise<{ message: string }> {
    return this.client.post('/genesis/start', {})
  }

  /**
   * Stop genesis
   */
  async stopGenesis(): Promise<{ message: string }> {
    return this.client.post('/genesis/stop', {})
  }

  /**
   * Get health check
   */
  async healthCheck(): Promise<{ healthy: boolean }> {
    return this.client.get('/health')
  }
}

export const apiClient = new APIClient()
export default APIClient
