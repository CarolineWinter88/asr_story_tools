<template>
  <div class="export-page">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <el-button @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1 class="page-title">试听与导出</h1>
      </div>
    </div>

    <div class="main-container">
      <!-- Project Info Card -->
      <el-card class="project-info-card" shadow="hover">
        <div class="project-header">
          <img :src="project?.cover_image || '/default-cover.png'" alt="项目封面" class="project-cover" />
          <div class="project-details">
            <h2>{{ project?.name }}</h2>
            <p class="project-desc">{{ project?.description }}</p>
            <div class="project-stats">
              <el-tag>{{ project?.chapters_count || 0 }} 章节</el-tag>
              <el-tag type="success">{{ project?.characters_count || 0 }} 角色</el-tag>
              <el-tag type="warning">{{ formatDuration(project?.total_duration || 0) }}</el-tag>
            </div>
          </div>
        </div>
      </el-card>

      <div class="content-grid">
        <!-- Left Column: Audio Player & Chapter List -->
        <div class="left-column">
          <!-- Audio Player Card -->
          <el-card class="player-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">音频播放器</span>
                <el-button size="small" @click="refreshPlayer">
                  <el-icon><RefreshRight /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>

            <div class="audio-player">
              <div class="player-info">
                <div class="now-playing-label">正在播放</div>
                <div class="now-playing-title">{{ currentChapter?.title || '请选择章节' }}</div>
              </div>

              <div class="waveform-preview">
                <!-- Simplified waveform visualization -->
                <div v-if="currentChapter" class="wave-bars">
                  <div 
                    v-for="i in 30" 
                    :key="i" 
                    class="wave-bar"
                    :style="{ height: (Math.random() * 60 + 20) + '%' }"
                  ></div>
                </div>
                <div v-else class="empty-state">
                  <el-icon size="48"><Headset /></el-icon>
                  <p>选择章节开始播放</p>
                </div>
              </div>

              <div class="progress-section">
                <div class="time-display">
                  <span>{{ currentTime }}</span>
                  <span>{{ totalTime }}</span>
                </div>
                <el-slider v-model="progress" :show-tooltip="false" @change="seekTo" />
              </div>

              <div class="player-controls">
                <el-button-group>
                  <el-button @click="previousChapter">
                    <el-icon><DArrowLeft /></el-icon>
                  </el-button>
                  <el-button @click="skipBackward">
                    <el-icon><CaretLeft /></el-icon>
                    -10s
                  </el-button>
                  <el-button type="primary" size="large" @click="togglePlay">
                    <el-icon><component :is="isPlaying ? VideoPause : VideoPlay" /></el-icon>
                  </el-button>
                  <el-button @click="skipForward">
                    +10s
                    <el-icon><CaretRight /></el-icon>
                  </el-button>
                  <el-button @click="nextChapter">
                    <el-icon><DArrowRight /></el-icon>
                  </el-button>
                </el-button-group>

                <div class="volume-control">
                  <el-icon><MagicStick /></el-icon>
                  <el-slider v-model="volume" :show-tooltip="false" style="width: 120px; margin: 0 12px;" />
                  <span class="volume-text">{{ volume }}%</span>
                </div>

                <el-select v-model="playbackSpeed" size="small" style="width: 90px;">
                  <el-option 
                    v-for="speed in playbackSpeeds" 
                    :key="speed" 
                    :label="`${speed}x`" 
                    :value="speed"
                  />
                </el-select>
              </div>
            </div>
          </el-card>

          <!-- Chapter Timeline Card -->
          <el-card class="timeline-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">章节时间线</span>
                <el-tag>{{ chapters.length }} 章</el-tag>
              </div>
            </template>

            <div class="chapter-timeline">
              <div 
                v-for="(chapter, index) in chapters" 
                :key="chapter.id"
                class="timeline-item"
                :class="{ active: currentChapterId === chapter.id }"
                @click="selectChapter(chapter)"
              >
                <div class="timeline-marker">
                  <div class="marker-dot"></div>
                  <div v-if="index < chapters.length - 1" class="marker-line"></div>
                </div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="chapter-title">{{ chapter.title }}</span>
                    <el-tag :type="getChapterStatusType(chapter.status)" size="small">
                      {{ getChapterStatusText(chapter.status) }}
                    </el-tag>
                  </div>
                  <div class="timeline-meta">
                    <span>{{ chapter.word_count || 0 }} 字</span>
                    <span>•</span>
                    <span>{{ formatDuration(chapter.duration || 0) }}</span>
                  </div>
                  <div class="timeline-actions">
                    <el-button size="small" text @click.stop="playChapter(chapter)">
                      <el-icon><VideoPlay /></el-icon>
                      播放
                    </el-button>
                    <el-button size="small" text @click.stop="previewChapter(chapter)">
                      <el-icon><View /></el-icon>
                      预览
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Right Column: Export Settings -->
        <div class="right-column">
          <!-- Export Settings Card -->
          <el-card class="export-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">导出设置</span>
                <el-icon size="20"><Setting /></el-icon>
              </div>
            </template>

            <el-form :model="exportForm" label-width="100px" label-position="left">
              <!-- Export Range -->
              <el-form-item label="导出范围">
                <el-radio-group v-model="exportForm.range">
                  <el-radio value="all">全部章节</el-radio>
                  <el-radio value="current">当前章节</el-radio>
                  <el-radio value="custom">自定义</el-radio>
                </el-radio-group>
              </el-form-item>

              <!-- Custom Range Selection -->
              <el-form-item v-if="exportForm.range === 'custom'" label="选择章节">
                <el-select 
                  v-model="exportForm.chapterIds" 
                  multiple 
                  placeholder="请选择章节"
                  style="width: 100%;"
                >
                  <el-option 
                    v-for="chapter in chapters" 
                    :key="chapter.id"
                    :label="chapter.title"
                    :value="chapter.id"
                  />
                </el-select>
              </el-form-item>

              <!-- Audio Format -->
              <el-form-item label="音频格式">
                <el-select v-model="exportForm.format" placeholder="选择格式">
                  <el-option label="MP3 (推荐)" value="mp3">
                    <span>MP3 (推荐)</span>
                    <el-tag size="small" style="margin-left: 8px;">通用</el-tag>
                  </el-option>
                  <el-option label="WAV (无损)" value="wav">
                    <span>WAV (无损)</span>
                    <el-tag size="small" type="success" style="margin-left: 8px;">高质量</el-tag>
                  </el-option>
                  <el-option label="M4A (AAC)" value="m4a">
                    <span>M4A (AAC)</span>
                    <el-tag size="small" type="info" style="margin-left: 8px;">Apple</el-tag>
                  </el-option>
                  <el-option label="OGG" value="ogg">
                    <span>OGG</span>
                  </el-option>
                </el-select>
              </el-form-item>

              <!-- Quality -->
              <el-form-item label="音质">
                <el-select v-model="exportForm.quality" placeholder="选择音质">
                  <el-option label="标准 (128kbps)" value="standard" />
                  <el-option label="高质量 (192kbps)" value="high" />
                  <el-option label="超高质量 (320kbps)" value="ultra" />
                </el-select>
              </el-form-item>

              <!-- Sample Rate -->
              <el-form-item label="采样率">
                <el-select v-model="exportForm.sampleRate">
                  <el-option label="44.1 kHz (CD质量)" :value="44100" />
                  <el-option label="48 kHz (专业)" :value="48000" />
                </el-select>
              </el-form-item>

              <!-- Merge Options -->
              <el-form-item label="合并选项">
                <el-checkbox v-model="exportForm.mergeChapters">合并所有章节为单个文件</el-checkbox>
              </el-form-item>

              <el-form-item v-if="!exportForm.mergeChapters" label="文件命名">
                <el-input v-model="exportForm.namingPattern" placeholder="例如: 第{chapter}章">
                  <template #prepend>模板</template>
                </el-input>
                <div class="form-tip">可用变量: {project}, {chapter}, {index}</div>
              </el-form-item>

              <!-- Advanced Options -->
              <el-divider>高级选项</el-divider>

              <el-form-item label="添加静音">
                <el-checkbox v-model="exportForm.addSilence">章节间添加静音</el-checkbox>
              </el-form-item>

              <el-form-item v-if="exportForm.addSilence" label="静音时长">
                <el-slider 
                  v-model="exportForm.silenceDuration" 
                  :min="0.5" 
                  :max="5" 
                  :step="0.5"
                  :marks="{ 0.5: '0.5s', 2.5: '2.5s', 5: '5s' }"
                  show-stops
                />
              </el-form-item>

              <el-form-item label="音量标准化">
                <el-checkbox v-model="exportForm.normalize">启用音量标准化</el-checkbox>
              </el-form-item>

              <el-form-item label="添加元数据">
                <el-checkbox v-model="exportForm.addMetadata">添加标题、作者等信息</el-checkbox>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- Export Info Card -->
          <el-card class="info-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">导出信息</span>
                <el-icon><InfoFilled /></el-icon>
              </div>
            </template>

            <div class="export-info">
              <div class="info-item">
                <span class="info-label">预计文件数</span>
                <span class="info-value">{{ estimatedFileCount }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">预计大小</span>
                <span class="info-value">{{ estimatedSize }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">总时长</span>
                <span class="info-value">{{ estimatedDuration }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">导出格式</span>
                <span class="info-value">{{ exportForm.format.toUpperCase() }}</span>
              </div>
            </div>

            <el-divider />

            <el-button type="primary" size="large" :loading="isExporting" @click="handleExport" style="width: 100%;">
              <el-icon><Download /></el-icon>
              {{ isExporting ? '导出中...' : '开始导出' }}
            </el-button>

            <div v-if="exportHistory.length > 0" class="export-history">
              <el-divider>导出历史</el-divider>
              <div 
                v-for="record in exportHistory" 
                :key="record.id"
                class="history-item"
              >
                <div class="history-info">
                  <div class="history-name">{{ record.format.toUpperCase() }} • {{ record.quality }}</div>
                  <div class="history-meta">{{ formatFileSize(record.file_size) }} • {{ formatDate(record.created_at) }}</div>
                </div>
                <el-button size="small" text @click="downloadExport(record)">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- Audio Element -->
    <audio ref="audioRef" @timeupdate="updateProgress" @ended="onAudioEnded"></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Download, RefreshRight, Setting, InfoFilled,
  DArrowLeft, DArrowRight, CaretLeft, CaretRight,
  VideoPlay, VideoPause, MagicStick, Headset, View
} from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import { useChapterStore } from '@/stores/chapter'
import type { Project, Chapter } from '@/types'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const chapterStore = useChapterStore()

// Refs
const audioRef = ref<HTMLAudioElement>()

// State
const projectId = ref(Number(route.params.id))
const project = ref<Project>()
const chapters = ref<Chapter[]>([])
const currentChapterId = ref<number>()
const isPlaying = ref(false)
const progress = ref(0)
const volume = ref(75)
const playbackSpeed = ref(1.0)
const playbackSpeeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
const currentTime = ref('00:00')
const totalTime = ref('00:00')
const isExporting = ref(false)
const exportHistory = ref<any[]>([])

// Export Form
const exportForm = ref({
  range: 'all',
  chapterIds: [] as number[],
  format: 'mp3',
  quality: 'high',
  sampleRate: 48000,
  mergeChapters: false,
  namingPattern: '第{chapter}章',
  addSilence: true,
  silenceDuration: 1,
  normalize: true,
  addMetadata: true
})

// Computed
const currentChapter = computed(() => 
  chapters.value.find(c => c.id === currentChapterId.value)
)

const estimatedFileCount = computed(() => {
  if (exportForm.value.range === 'all') {
    return exportForm.value.mergeChapters ? 1 : chapters.value.length
  } else if (exportForm.value.range === 'current') {
    return 1
  } else {
    return exportForm.value.mergeChapters ? 1 : exportForm.value.chapterIds.length
  }
})

const estimatedSize = computed(() => {
  const bitrates = { standard: 128, high: 192, ultra: 320 }
  const bitrate = bitrates[exportForm.value.quality as keyof typeof bitrates]
  
  let totalDuration = 0
  if (exportForm.value.range === 'all') {
    totalDuration = chapters.value.reduce((sum, c) => sum + (c.duration || 0), 0)
  } else if (exportForm.value.range === 'current' && currentChapter.value) {
    totalDuration = currentChapter.value.duration || 0
  } else {
    totalDuration = chapters.value
      .filter(c => exportForm.value.chapterIds.includes(c.id))
      .reduce((sum, c) => sum + (c.duration || 0), 0)
  }
  
  const sizeKB = (totalDuration * bitrate) / 8
  return formatFileSize(sizeKB * 1024)
})

const estimatedDuration = computed(() => {
  let totalDuration = 0
  if (exportForm.value.range === 'all') {
    totalDuration = chapters.value.reduce((sum, c) => sum + (c.duration || 0), 0)
  } else if (exportForm.value.range === 'current' && currentChapter.value) {
    totalDuration = currentChapter.value.duration || 0
  } else {
    totalDuration = chapters.value
      .filter(c => exportForm.value.chapterIds.includes(c.id))
      .reduce((sum, c) => sum + (c.duration || 0), 0)
  }
  return formatDuration(totalDuration)
})

// Methods
const loadData = async () => {
  try {
    project.value = await projectStore.fetchProject(projectId.value)
    chapters.value = await chapterStore.fetchChapters(projectId.value)
    
    if (chapters.value.length > 0) {
      currentChapterId.value = chapters.value[0].id
    }
    
    // Load export history (mock)
    exportHistory.value = []
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const formatDuration = (seconds: number): string => {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const getChapterStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getChapterStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || status
}

const selectChapter = (chapter: Chapter) => {
  currentChapterId.value = chapter.id
}

const playChapter = (chapter: Chapter) => {
  currentChapterId.value = chapter.id
  // Load and play chapter audio
  if (audioRef.value) {
    // audioRef.value.src = `/api/audio/chapters/${chapter.id}/merged`
    audioRef.value.play()
    isPlaying.value = true
  }
}

const previewChapter = (chapter: Chapter) => {
  router.push(`/projects/${projectId.value}/audio-preview/${chapter.id}`)
}

const togglePlay = () => {
  if (!audioRef.value) return
  
  if (isPlaying.value) {
    audioRef.value.pause()
  } else {
    audioRef.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const seekTo = (value: number) => {
  if (!audioRef.value) return
  const duration = audioRef.value.duration || 0
  audioRef.value.currentTime = (value / 100) * duration
}

const updateProgress = () => {
  if (!audioRef.value) return
  const current = audioRef.value.currentTime
  const duration = audioRef.value.duration || 0
  progress.value = (current / duration) * 100
  currentTime.value = formatDuration(current)
  totalTime.value = formatDuration(duration)
}

const onAudioEnded = () => {
  isPlaying.value = false
  // Auto play next chapter
  nextChapter()
}

const skipForward = () => {
  if (audioRef.value) {
    audioRef.value.currentTime += 10
  }
}

const skipBackward = () => {
  if (audioRef.value) {
    audioRef.value.currentTime -= 10
  }
}

const previousChapter = () => {
  const currentIndex = chapters.value.findIndex(c => c.id === currentChapterId.value)
  if (currentIndex > 0) {
    playChapter(chapters.value[currentIndex - 1])
  }
}

const nextChapter = () => {
  const currentIndex = chapters.value.findIndex(c => c.id === currentChapterId.value)
  if (currentIndex < chapters.value.length - 1) {
    playChapter(chapters.value[currentIndex + 1])
  }
}

const refreshPlayer = () => {
  if (audioRef.value) {
    audioRef.value.load()
  }
  ElMessage.success('播放器已刷新')
}

const handleExport = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要导出 ${estimatedFileCount.value} 个文件吗？预计大小: ${estimatedSize.value}`,
      '确认导出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    isExporting.value = true
    
    // Call export API
    // await audioStore.exportProject({
    //   projectId: projectId.value,
    //   ...exportForm.value
    // })
    
    // Simulate export process
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('导出成功！')
    
    // Refresh export history
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('导出失败')
    }
  } finally {
    isExporting.value = false
  }
}

const downloadExport = (record: any) => {
  // Download exported file
  window.open(record.file_path, '_blank')
  ElMessage.success('开始下载')
}

const goBack = () => {
  router.back()
}

// Lifecycle
onMounted(() => {
  loadData()
  
  if (audioRef.value) {
    audioRef.value.volume = volume.value / 100
  }
})
</script>

<style scoped lang="scss">
.export-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  height: 60px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #e4e7ed;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.main-container {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.project-info-card {
  margin-bottom: 24px;
}

.project-header {
  display: flex;
  gap: 20px;
}

.project-cover {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.project-details {
  flex: 1;
  
  h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
  }
}

.project-desc {
  color: #606266;
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.project-stats {
  display: flex;
  gap: 8px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.player-card {
  .audio-player {
    padding: 16px 0;
  }
}

.player-info {
  margin-bottom: 20px;
}

.now-playing-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.now-playing-title {
  font-size: 18px;
  font-weight: 600;
}

.waveform-preview {
  height: 120px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  overflow: hidden;
}

.wave-bars {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 100%;
  padding: 16px;
}

.wave-bar {
  width: 3px;
  background: linear-gradient(180deg, #409eff 0%, #67c23a 100%);
  border-radius: 2px;
  opacity: 0.6;
}

.empty-state {
  text-align: center;
  color: #909399;
  
  p {
    margin: 12px 0 0 0;
  }
}

.progress-section {
  margin-bottom: 20px;
}

.time-display {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #909399;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: space-between;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.volume-text {
  font-size: 12px;
  color: #909399;
  min-width: 40px;
}

.timeline-card {
  flex: 1;
  overflow: hidden;
  
  :deep(.el-card__body) {
    max-height: 500px;
    overflow-y: auto;
  }
}

.chapter-timeline {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
  
  &:hover {
    background: #f5f7fa;
  }
  
  &.active {
    background: #ecf5ff;
    
    .marker-dot {
      background: #409eff;
    }
  }
}

.timeline-marker {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.marker-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #dcdfe6;
  transition: all 0.3s;
}

.marker-line {
  width: 2px;
  flex: 1;
  min-height: 40px;
  background: #dcdfe6;
  margin-top: 4px;
}

.timeline-content {
  flex: 1;
  min-width: 0;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.chapter-title {
  font-weight: 600;
  font-size: 14px;
}

.timeline-meta {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.timeline-actions {
  display: flex;
  gap: 8px;
}

.export-card,
.info-card {
  :deep(.el-form-item__label) {
    font-size: 13px;
    color: #606266;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.export-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.info-label {
  font-size: 13px;
  color: #909399;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.export-history {
  margin-top: 16px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-name {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 4px;
}

.history-meta {
  font-size: 12px;
  color: #909399;
}
</style>

