// 项目类型定义
export interface Project {
  id: number
  name: string
  description?: string
  cover_image?: string
  status: 'draft' | 'processing' | 'completed'
  chapters_count: number
  characters_count: number
  total_duration: number
  created_at: string
  updated_at: string
}

export interface CreateProjectDTO {
  name: string
  description?: string
}

// 章节类型定义
export interface Chapter {
  id: number
  project_id: number
  title: string
  order_index: number
  content: string
  word_count: number
  status: string
  duration: number
  created_at: string
  updated_at: string
}

export interface UploadChapterDTO {
  project_id: number
  file: File
}

// 角色类型定义
export interface Character {
  id: number
  project_id: number
  name: string
  avatar?: string
  description?: string
  dialogue_count: number
  total_duration: number
  voice_config: VoiceConfig
  created_at: string
  updated_at: string
}

export interface VoiceConfig {
  engine?: string
  voice_id?: string
  speed?: number
  pitch?: number
  volume?: number
}

export interface UpdateCharacterDTO {
  name?: string
  avatar?: string
  description?: string
  voice_config?: VoiceConfig
}

// 对话类型定义
export interface Dialogue {
  id: number
  chapter_id: number
  order_index: number
  type: 'dialogue' | 'narration'
  content: string
  character_id?: number
  character?: Character
  start_time?: number
  end_time?: number
  audio_path?: string
  status?: 'pending' | 'generating' | 'completed' | 'failed'
  voice_config?: Partial<VoiceConfig>
  pause_after?: number
  created_at: string
  updated_at: string
}

export interface CreateDialogueDTO {
  chapter_id: number
  order_index: number
  type: 'dialogue' | 'narration'
  content: string
  character_id?: number
}

export interface UpdateDialogueDTO {
  content?: string
  character_id?: number
  order_index?: number
}

// 音频导出类型定义
export interface AudioExport {
  id: number
  project_id: number
  format: 'mp3' | 'wav' | 'm4a'
  quality: 'low' | 'medium' | 'high'
  file_path: string
  file_size: number
  export_range: ExportRange
  created_at: string
}

export interface ExportRange {
  chapter_ids?: number[]
  dialogue_ids?: number[]
}

export interface ExportAudioDTO {
  project_id: number
  format: 'mp3' | 'wav' | 'm4a'
  quality: 'low' | 'medium' | 'high'
  export_range: ExportRange
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginationParams {
  page?: number
  page_size?: number
  search?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

