import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AudioExport, ExportAudioDTO } from '@/types'
import * as audioApi from '@/api/audio'

export const useAudioStore = defineStore('audio', () => {
  // 状态
  const currentAudio = ref<string | null>(null)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)
  const volume = ref(1)
  const generating = ref(false)
  const exporting = ref(false)
  const exportRecords = ref<AudioExport[]>([])

  // 音频控制
  const play = () => {
    isPlaying.value = true
  }

  const pause = () => {
    isPlaying.value = false
  }

  const stop = () => {
    isPlaying.value = false
    currentTime.value = 0
  }

  const seek = (time: number) => {
    currentTime.value = time
  }

  const setVolume = (vol: number) => {
    volume.value = Math.max(0, Math.min(1, vol))
  }

  const setCurrentAudio = (url: string | null) => {
    currentAudio.value = url
    currentTime.value = 0
  }

  // 生成单段音频
  const generateAudio = async (dialogueId: number) => {
    generating.value = true
    try {
      await audioApi.generateAudio(dialogueId)
    } finally {
      generating.value = false
    }
  }

  // 批量生成音频
  const batchGenerateAudio = async (dialogueIds: number[]) => {
    generating.value = true
    try {
      await audioApi.batchGenerateAudio(dialogueIds)
    } finally {
      generating.value = false
    }
  }

  // 生成章节音频
  const generateChapterAudio = async (chapterId: number) => {
    generating.value = true
    try {
      await audioApi.generateChapterAudio(chapterId)
    } finally {
      generating.value = false
    }
  }

  // 导出音频
  const exportAudio = async (data: ExportAudioDTO) => {
    exporting.value = true
    try {
      const exportRecord = await audioApi.exportAudio(data)
      exportRecords.value.unshift(exportRecord)
      return exportRecord
    } finally {
      exporting.value = false
    }
  }

  // 获取导出记录
  const fetchExportRecords = async (projectId: number) => {
    const records = await audioApi.getExportRecords(projectId)
    exportRecords.value = records
    return records
  }

  // 删除导出记录
  const deleteExport = async (id: number) => {
    await audioApi.deleteExport(id)
    exportRecords.value = exportRecords.value.filter((r) => r.id !== id)
  }

  // 重置状态
  const reset = () => {
    currentAudio.value = null
    isPlaying.value = false
    currentTime.value = 0
    duration.value = 0
    volume.value = 1
    generating.value = false
    exporting.value = false
    exportRecords.value = []
  }

  return {
    currentAudio,
    isPlaying,
    currentTime,
    duration,
    volume,
    generating,
    exporting,
    exportRecords,
    play,
    pause,
    stop,
    seek,
    setVolume,
    setCurrentAudio,
    generateAudio,
    batchGenerateAudio,
    generateChapterAudio,
    exportAudio,
    fetchExportRecords,
    deleteExport,
    reset,
  }
})

