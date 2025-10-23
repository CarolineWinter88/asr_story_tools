import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as chapterApi from '@/api/chapter'
import type { Chapter } from '@/types'

export const useChapterStore = defineStore('chapter', () => {
  // 状态
  const chapters = ref<Chapter[]>([])
  const currentChapter = ref<Chapter | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const hasChapters = computed(() => chapters.value.length > 0)

  // 获取章节列表
  const fetchChapters = async (projectId: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await chapterApi.getChapters(projectId)
      chapters.value = data
      return data
    } catch (err: any) {
      error.value = err.message || '获取章节列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取章节详情
  const fetchChapter = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await chapterApi.getChapter(id)
      currentChapter.value = data
      return data
    } catch (err: any) {
      error.value = err.message || '获取章节详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新章节
  const updateChapter = async (id: number, updates: Partial<Chapter>) => {
    loading.value = true
    error.value = null
    try {
      const data = await chapterApi.updateChapter(id, updates)
      
      // 更新列表中的章节
      const index = chapters.value.findIndex(c => c.id === id)
      if (index !== -1) {
        chapters.value[index] = data
      }
      
      // 更新当前章节
      if (currentChapter.value?.id === id) {
        currentChapter.value = data
      }
      
      return data
    } catch (err: any) {
      error.value = err.message || '更新章节失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除章节
  const deleteChapter = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await chapterApi.deleteChapter(id)
      
      // 从列表中移除
      chapters.value = chapters.value.filter(c => c.id !== id)
      
      // 清空当前章节
      if (currentChapter.value?.id === id) {
        currentChapter.value = null
      }
    } catch (err: any) {
      error.value = err.message || '删除章节失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 重置状态
  const reset = () => {
    chapters.value = []
    currentChapter.value = null
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    chapters,
    currentChapter,
    loading,
    error,
    
    // 计算属性
    hasChapters,
    
    // 方法
    fetchChapters,
    fetchChapter,
    updateChapter,
    deleteChapter,
    reset,
  }
})

