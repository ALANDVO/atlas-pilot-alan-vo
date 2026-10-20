import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

const API_BASE = '/api/v1'

class ApiClient {
  private client: AxiosInstance
  private accessToken: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    })

    this.client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      if (this.accessToken) {
        config.headers.Authorization = `Bearer ${this.accessToken}`
      }
      return config
    })
  }

  setAccessToken(token: string | null) {
    this.accessToken = token
  }

  get accessTokenValue() {
    return this.accessToken
  }

  async get(url: string, params?: object) {
    return this.client.get(url, { params })
  }

  async post(url: string, data?: object) {
    return this.client.post(url, data)
  }

  async put(url: string, data?: object) {
    return this.client.put(url, data)
  }

  async delete(url: string) {
    return this.client.delete(url)
  }
}

export const apiClient = new ApiClient()