import { request } from '@/utils/http'
import type { Project, CreateProjectDTO, PaginationParams, PaginatedResponse } from '@/types'

// 获取项目列表
export const getProjects = (params?: PaginationParams) => {
  return request.get<PaginatedResponse<Project>>('/projects', { params })
}

// 获取项目详情
export const getProject = (id: number) => {
  return request.get<Project>(`/projects/${id}`)
}

// 创建项目
export const createProject = (data: CreateProjectDTO) => {
  return request.post<Project>('/projects', data)
}

// 更新项目
export const updateProject = (id: number, data: Partial<CreateProjectDTO>) => {
  return request.put<Project>(`/projects/${id}`, data)
}

// 删除项目
export const deleteProject = (id: number) => {
  return request.delete(`/projects/${id}`)
}

// 获取项目统计信息
export const getProjectStats = (id: number) => {
  return request.get(`/projects/${id}/stats`)
}

