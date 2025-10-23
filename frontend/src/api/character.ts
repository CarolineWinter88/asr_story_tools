import { request } from '@/utils/http'
import type { Character, UpdateCharacterDTO } from '@/types'

// 获取角色列表
export const getCharacters = (projectId: number) => {
  return request.get<Character[]>('/characters', { params: { project_id: projectId } })
}

// 获取角色详情
export const getCharacter = (id: number) => {
  return request.get<Character>(`/characters/${id}`)
}

// 从章节提取角色
export const extractCharacters = (projectId: number) => {
  return request.post<{ characters: Character[] }>('/characters/extract', { project_id: projectId })
}

// 更新角色
export const updateCharacter = (id: number, data: UpdateCharacterDTO) => {
  return request.put<Character>(`/characters/${id}`, data)
}

// 删除角色
export const deleteCharacter = (id: number) => {
  return request.delete(`/characters/${id}`)
}

// 获取角色统计
export const getCharacterStats = (id: number) => {
  return request.get(`/characters/${id}/stats`)
}

