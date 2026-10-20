export interface Agent {
  id: number
  name: string
  slug: string
  description: string
  category: string
  color?: string
  content: string
  source_format: string
  created_at: string
  updated_at: string
}

export interface AgentCreate {
  name: string
  description: string
  category: string
  color?: string
  content: string
  source_format: string
}

export interface AgentUpdate {
  name?: string
  description?: string
  category?: string
  color?: string
  content?: string
}

export interface Evaluation {
  id: number
  agent_id: number
  criteria_name: string
  criteria_description?: string
  score: number
  details?: string
  created_at: string
}

export interface EvaluationCreate {
  agent_id: number
  criteria_name: string
  criteria_description?: string
  score: number
  details?: string
}

export interface AuditLog {
  id: number
  entity_type: string
  entity_id: number
  action: string
  user_id?: string
  changes?: string
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface HealthResponse {
  status: string
  service: string
}