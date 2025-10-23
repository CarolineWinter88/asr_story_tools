import http from './http'
import type { Dialogue, CreateDialogueDTO, UpdateDialogueDTO } from '@/types'

// 获取对话列表
export const getDialogues = async (chapterId: number): Promise<Dialogue[]> => {
  const response = await http.get(`/dialogues?chapter_id=${chapterId}`)
  return response.data
}

// 创建对话
export const createDialogue = async (data: CreateDialogueDTO): Promise<Dialogue> => {
  const response = await http.post('/dialogues', data)
  return response.data
}

// 更新对话
export const updateDialogue = async (id: number, data: UpdateDialogueDTO | Dialogue): Promise<Dialogue> => {
  const response = await http.put(`/dialogues/${id}`, data)
  return response.data
}

// 删除对话
export const deleteDialogue = async (id: number): Promise<void> => {
  await http.delete(`/dialogues/${id}`)
}

// 解析章节对话
export const parseChapter = async (chapterId: number): Promise<any> => {
  const response = await http.post(`/dialogues/parse`, { chapter_id: chapterId })
  return response.data
}

// 生成音频
export const generateAudio = async (dialogueId: number): Promise<Dialogue> => {
  const response = await http.post(`/audio/generate`, { dialogue_id: dialogueId })
  return response.data
}

// 批量生成音频
export const batchGenerateAudio = async (dialogueIds: number[]): Promise<any> => {
  const response = await http.post(`/audio/batch-generate`, { dialogue_ids: dialogueIds })
  return response.data
}
