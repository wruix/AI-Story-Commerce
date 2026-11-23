// AI Story Commerce — API Client

import { 
  Project,
  Customer,
  Product,
  Character,
  StoryIdea,
  Script,
  Storyboard,
  ProductionTask,
  MediaAsset,
  Advertisement,
  ComplianceReview,
  PublishingRecord,
  PerformanceMetric,
  PromptTemplate,
  AuditLog,
  PaginationParams,
} from "@/types"
import type {
  ProjectCreate, ProjectUpdate,
  CustomerCreate, CustomerUpdate,
  ProductCreate, ProductUpdate,
  CharacterCreate, CharacterUpdate,
  StoryIdeaCreate, StoryIdeaUpdate,
  ScriptCreate, ScriptUpdate,
  StoryboardCreate, StoryboardUpdate,
  ProductionTaskCreate, ProductionTaskUpdate,
  MediaAssetCreate, MediaAssetUpdate,
  AdvertisementCreate, AdvertisementUpdate,
  ComplianceReviewCreate, ComplianceReviewUpdate,
  PublishingRecordCreate, PublishingRecordUpdate,
  PerformanceMetricCreate, PerformanceMetricUpdate,
  PromptTemplateCreate, PromptTemplateUpdate,
  AuditLogCreate,
} from "@/types/api"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api/v1"

async function request<T>(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${input.toString().replace(API_BASE, "")}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    ...init,
  })

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "")
    throw new Error(`API error ${res.status}: ${errorBody || res.statusText}`)
  }

  if (res.status === 204) {
    return null as T
  }

  return res.json()
}

// Helper to build query string
function buildQuery(params: Record<string, string | number | boolean | undefined>): string {
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value))
    }
  })
  return searchParams.toString()
}

// Generic CRUD factory
function createCRUD<T, TCreate, TUpdate>(resource: string) {
  return {
    list: (params?: PaginationParams & Record<string, string>) => {
      const query = buildQuery({ skip: 0, limit: 100, ...params })
      return request<T[]>(`/${resource}?${query}`)
    },
    get: (id: string) => request<T>(`/${resource}/${id}`),
    create: (data: TCreate) => request<T>(`/${resource}`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
    update: (id: string, data: TUpdate) => request<T>(`/${resource}/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<{ message: string }>(`/${resource}/${id}`, {
      method: "DELETE",
    }),
  }
}

// Project API
export const projectApi = {
  ...createCRUD<Project, ProjectCreate, ProjectUpdate>("/projects"),
}

// Customer API
export const customerApi = {
  ...createCRUD<Customer, CustomerCreate, CustomerUpdate>("/customers"),
}

// Product API
export const productApi = {
  ...createCRUD<Product, ProductCreate, ProductUpdate>("/products"),
  listByProject: (projectId: string, params?: PaginationParams) => {
    const query = buildQuery({ project_id: projectId, ...params })
    return request<Product[]>(`/products?${query}`)
  },
}

// Character API
export const characterApi = {
  ...createCRUD<Character, CharacterCreate, CharacterUpdate>("/characters"),
  getCoreIP: () => request<Character | null>("/characters/core-ip"),
}

// Story Idea API
export const storyIdeaApi = {
  ...createCRUD<StoryIdea, StoryIdeaCreate, StoryIdeaUpdate>("/story-ideas"),
  listByProduct: (productId: string, params?: PaginationParams) => {
    const query = buildQuery({ product_id: productId, ...params })
    return request<StoryIdea[]>(`/story-ideas?${query}`)
  },
}

// Script API
export const scriptApi = {
  ...createCRUD<Script, ScriptCreate, ScriptUpdate>("/scripts"),
  listByStoryIdea: (storyIdeaId: string, params?: PaginationParams) => {
    const query = buildQuery({ story_idea_id: storyIdeaId, ...params })
    return request<Script[]>(`/scripts?${query}`)
  },
  getCurrent: (storyIdeaId: string) => request<Script | null>(`/scripts/${storyIdeaId}/current`),
}

// Storyboard API
export const storyboardApi = {
  ...createCRUD<Storyboard, StoryboardCreate, StoryboardUpdate>("/storyboards"),
  listByScript: (scriptId: string, params?: PaginationParams) => {
    const query = buildQuery({ script_id: scriptId, ...params })
    return request<Storyboard[]>(`/storyboards?${query}`)
  },
}

// Production Task API
export const productionTaskApi = {
  ...createCRUD<ProductionTask, ProductionTaskCreate, ProductionTaskUpdate>("/production-tasks"),
  listByStoryboard: (storyboardId: string, params?: PaginationParams) => {
    const query = buildQuery({ storyboard_id: storyboardId, ...params })
    return request<ProductionTask[]>(`/production-tasks?${query}`)
  },
}

// Media Asset API
export const mediaAssetApi = {
  ...createCRUD<MediaAsset, MediaAssetCreate, MediaAssetUpdate>("/media-assets"),
  listByStoryboard: (storyboardId: string, params?: PaginationParams) => {
    const query = buildQuery({ storyboard_id: storyboardId, ...params })
    return request<MediaAsset[]>(`/media-assets?${query}`)
  },
}

// Advertisement API
export const advertisementApi = {
  ...createCRUD<Advertisement, AdvertisementCreate, AdvertisementUpdate>("/advertisements"),
  listByProject: (projectId: string, params?: PaginationParams) => {
    const query = buildQuery({ project_id: projectId, ...params })
    return request<Advertisement[]>(`/advertisements?${query}`)
  },
}

// Compliance Review API
export const complianceReviewApi = {
  ...createCRUD<ComplianceReview, ComplianceReviewCreate, ComplianceReviewUpdate>("/compliance-reviews"),
  listByAdvertisement: (advertisementId: string, params?: PaginationParams) => {
    const query = buildQuery({ advertisement_id: advertisementId, ...params })
    return request<ComplianceReview[]>(`/compliance-reviews?${query}`)
  },
}

// Publishing Record API
export const publishingRecordApi = {
  ...createCRUD<PublishingRecord, PublishingRecordCreate, PublishingRecordUpdate>("/publishing-records"),
  listByAdvertisement: (advertisementId: string, params?: PaginationParams) => {
    const query = buildQuery({ advertisement_id: advertisementId, ...params })
    return request<PublishingRecord[]>(`/publishing-records?${query}`)
  },
}

// Performance Metric API
export const performanceMetricApi = {
  ...createCRUD<PerformanceMetric, PerformanceMetricCreate, PerformanceMetricUpdate>("/performance-metrics"),
  listByPublishingRecord: (publishingRecordId: string, params?: PaginationParams) => {
    const query = buildQuery({ publishing_record_id: publishingRecordId, ...params })
    return request<PerformanceMetric[]>(`/performance-metrics?${query}`)
  },
}

// Prompt Template API
export const promptTemplateApi = {
  ...createCRUD<PromptTemplate, PromptTemplateCreate, PromptTemplateUpdate>("/prompt-templates"),
  listByAgentType: (agentType: string, params?: PaginationParams) => {
    const query = buildQuery({ agent_type: agentType, ...params })
    return request<PromptTemplate[]>(`/prompt-templates?${query}`)
  },
}

// Audit Log API
export const auditLogApi = {
  ...createCRUD<AuditLog, AuditLogCreate, never>("/audit-logs"),
}

// Health check
export const healthApi = {
  check: () => request<{ status: string; service: string; version: string }>("/health"),
}
