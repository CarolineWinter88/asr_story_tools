import http from './http'
import type { Chapter } from '@/types'

// 获取章节列表
export const getChapters = async (projectId: number): Promise<Chapter[]> => {
  const response = await http.get(`/chapters?project_id=${projectId}`)
  return response.data
}

// 获取章节详情
export const getChapter = async (id: number): Promise<Chapter> => {
  const response = await http.get(`/chapters/${id}`)
  return response.data
}

// 上传章节文件
export const uploadChapter = async (projectId: number, file: File): Promise<Chapter[]> => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('project_id', String(projectId))
  
  const response = await http.post('/chapters/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// 更新章节
export const updateChapter = async (id: number, data: Partial<Chapter>): Promise<Chapter> => {
  const response = await http.put(`/chapters/${id}`, data)
  return response.data
}

// 删除章节
export const deleteChapter = async (id: number): Promise<void> => {
  await http.delete(`/chapters/${id}`)
}
