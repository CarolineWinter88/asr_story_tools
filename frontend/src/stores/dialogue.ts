import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as dialogueApi from '@/api/dialogue'
import type { Dialogue, CreateDialogueDTO, UpdateDialogueDTO } from '@/types'

export const useDialogueStore = defineStore('dialogue', () => {
  // 状态
  const dialogues = ref<Dialogue[]>([])
  const currentDialogue = ref<Dialogue | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const hasDialogues = computed(() => dialogues.value.length > 0)
  
  const generatedCount = computed(() => 
    dialogues.value.filter(d => d.status === 'completed').length
  )

  // 获取对话列表
  const fetchDialogues = async (chapterId: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await dialogueApi.getDialogues(chapterId)
      dialogues.value = data
      return data
    } catch (err: any) {
      error.value = err.message || '获取对话列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 创建对话
  const createDialogue = async (dialogue: CreateDialogueDTO) => {
    loading.value = true
    error.value = null
    try {
      const data = await dialogueApi.createDialogue(dialogue)
      dialogues.value.push(data)
      return data
    } catch (err: any) {
      error.value = err.message || '创建对话失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新对话
  const updateDialogue = async (id: number, updates: UpdateDialogueDTO | Dialogue) => {
    loading.value = true
    error.value = null
    try {
      const data = await dialogueApi.updateDialogue(id, updates)
      
      // 更新列表中的对话
      const index = dialogues.value.findIndex(d => d.id === id)
      if (index !== -1) {
        dialogues.value[index] = data
      }
      
      // 更新当前对话
      if (currentDialogue.value?.id === id) {
        currentDialogue.value = data
      }
      
      return data
    } catch (err: any) {
      error.value = err.message || '更新对话失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除对话
  const deleteDialogue = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await dialogueApi.deleteDialogue(id)
      
      // 从列表中移除
      dialogues.value = dialogues.value.filter(d => d.id !== id)
      
      // 清空当前对话
      if (currentDialogue.value?.id === id) {
        currentDialogue.value = null
      }
    } catch (err: any) {
      error.value = err.message || '删除对话失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 解析章节对话
  const parseChapter = async (chapterId: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await dialogueApi.parseChapter(chapterId)
      return data
    } catch (err: any) {
      error.value = err.message || '解析章节失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 生成音频
  const generateAudio = async (dialogueId: number) => {
    error.value = null
    try {
      const data = await dialogueApi.generateAudio(dialogueId)
      
      // 更新对话状态
      const index = dialogues.value.findIndex(d => d.id === dialogueId)
      if (index !== -1) {
        dialogues.value[index] = { ...dialogues.value[index], ...data }
      }
      
      return data
    } catch (err: any) {
      error.value = err.message || '生成音频失败'
      throw err
    }
  }

  // 批量生成音频
  const batchGenerateAudio = async (dialogueIds: number[]) => {
    error.value = null
    try {
      const data = await dialogueApi.batchGenerateAudio(dialogueIds)
      return data
    } catch (err: any) {
      error.value = err.message || '批量生成失败'
      throw err
    }
  }

  // 重置状态
  const reset = () => {
    dialogues.value = []
    currentDialogue.value = null
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    dialogues,
    currentDialogue,
    loading,
    error,
    
    // 计算属性
    hasDialogues,
    generatedCount,
    
    // 方法
    fetchDialogues,
    createDialogue,
    updateDialogue,
    deleteDialogue,
    parseChapter,
    generateAudio,
    batchGenerateAudio,
    reset,
  }
})

