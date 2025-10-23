import { request } from '@/utils/http'
import type { ExportAudioDTO, AudioExport } from '@/types'

// 生成单段音频
export const generateAudio = (dialogueId: number) => {
  return request.post(`/audio/generate`, { dialogue_id: dialogueId })
}

// 批量生成音频
export const batchGenerateAudio = (dialogueIds: number[]) => {
  return request.post(`/audio/batch-generate`, { dialogue_ids: dialogueIds })
}

// 生成章节音频
export const generateChapterAudio = (chapterId: number) => {
  return request.post(`/audio/generate-chapter`, { chapter_id: chapterId })
}

// 导出音频
export const exportAudio = (data: ExportAudioDTO) => {
  return request.post<AudioExport>('/audio/export', data)
}

// 获取导出记录
export const getExportRecords = (projectId: number) => {
  return request.get<AudioExport[]>('/audio/exports', { params: { project_id: projectId } })
}

// 删除导出记录
export const deleteExport = (id: number) => {
  return request.delete(`/audio/exports/${id}`)
}

// 获取音频文件URL
export const getAudioUrl = (path: string) => {
  return `/api/audio/files/${encodeURIComponent(path)}`
}

