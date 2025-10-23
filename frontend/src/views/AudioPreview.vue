<template>
  <div class="audio-preview">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <el-button @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1 class="page-title">音频预览 - {{ chapterTitle }}</h1>
      </div>
      <div class="header-actions">
        <el-button @click="regenerateAudio">
          <el-icon><RefreshRight /></el-icon>
          重新生成
        </el-button>
        <el-button type="primary" @click="exportAudio">
          <el-icon><Download /></el-icon>
          导出音频
        </el-button>
      </div>
    </div>

    <!-- Main Container -->
    <div class="main-container">
      <!-- Waveform Section -->
      <div class="waveform-section">
        <div class="waveform-header">
          <div class="chapter-info">
            <h2>{{ chapterTitle }}</h2>
            <div class="chapter-meta">
              共 {{ dialogues.length }} 段 · {{ totalDuration }} · {{ chapterStatus }}
            </div>
          </div>
          <div class="waveform-tools">
            <el-button-group>
              <el-button :type="waveformMode === 'wave' ? 'primary' : ''" size="small" @click="waveformMode = 'wave'">
                波形
              </el-button>
              <el-button :type="waveformMode === 'spectrum' ? 'primary' : ''" size="small" @click="waveformMode = 'spectrum'">
                频谱
              </el-button>
            </el-button-group>
            <el-button size="small" @click="zoomIn">
              <el-icon><ZoomIn /></el-icon>
            </el-button>
            <el-button size="small" @click="zoomOut">
              <el-icon><ZoomOut /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- Waveform Canvas -->
        <div class="waveform-canvas" ref="waveformRef">
          <div v-if="!audioUrl" class="waveform-placeholder">
            <div class="placeholder-icon">🎵</div>
            <div>暂无音频数据</div>
          </div>
          <div v-else class="waveform-visual">
            <!-- 简化的波形可视化 -->
            <div class="wave-bars">
              <div 
                v-for="(bar, index) in waveformBars" 
                :key="index" 
                class="wave-bar"
                :style="{ height: bar.height + '%', animationDelay: bar.delay + 's' }"
              ></div>
            </div>
          </div>

          <!-- Timeline Markers -->
          <div class="timeline-markers" v-if="audioUrl">
            <div 
              v-for="marker in timelineMarkers" 
              :key="marker.position"
              class="marker"
              :style="{ left: marker.position + '%' }"
            >
              <div class="marker-line"></div>
              <div class="marker-label">{{ marker.time }}</div>
            </div>
          </div>
        </div>

        <!-- Playback Controls -->
        <div class="playback-controls">
          <div class="progress-bar">
            <div class="time-display">
              <span>{{ currentTime }}</span>
              <span>{{ totalDuration }}</span>
            </div>
            <el-slider 
              v-model="progress" 
              :show-tooltip="false"
              @change="seekTo"
            />
          </div>

          <div class="controls-main">
            <div class="play-controls">
              <el-button circle @click="previousSegment" title="上一段">
                <el-icon><DArrowLeft /></el-icon>
              </el-button>
              <el-button circle @click="skipBackward" title="快退10秒">
                <el-icon><CaretLeft /></el-icon>
              </el-button>
              <el-button 
                circle 
                type="primary" 
                size="large" 
                @click="togglePlay"
                class="play-btn"
              >
                <el-icon><component :is="isPlaying ? VideoPause : VideoPlay" /></el-icon>
              </el-button>
              <el-button circle @click="skipForward" title="快进10秒">
                <el-icon><CaretRight /></el-icon>
              </el-button>
              <el-button circle @click="nextSegment" title="下一段">
                <el-icon><DArrowRight /></el-icon>
              </el-button>
            </div>

            <div class="volume-control">
              <el-icon class="volume-icon"><MagicStick /></el-icon>
              <el-slider v-model="volume" :show-tooltip="false" style="width: 150px; margin: 0 12px;" />
              <span class="volume-text">{{ volume }}%</span>
            </div>

            <div class="speed-control">
              <el-button-group>
                <el-button 
                  v-for="speed in playbackSpeeds" 
                  :key="speed"
                  :type="playbackSpeed === speed ? 'primary' : ''"
                  size="small"
                  @click="setPlaybackSpeed(speed)"
                >
                  {{ speed }}x
                </el-button>
              </el-button-group>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Panel -->
      <div class="bottom-panel">
        <!-- Segments List -->
        <div class="segments-list">
          <div 
            v-for="(dialogue, index) in dialogues" 
            :key="dialogue.id"
            class="segment-item"
            :class="{ active: currentSegmentIndex === index }"
            @click="selectSegment(index)"
          >
            <div class="segment-number">{{ index + 1 }}</div>
            <div class="segment-content">
              <div class="segment-speaker">
                {{ dialogue.type === 'narration' ? '🎭 旁白' : '👤 ' + (dialogue.character?.name || '未知') }}
              </div>
              <div class="segment-text">{{ dialogue.content }}</div>
              <div class="segment-time">
                {{ formatTime(dialogue.start_time) }} - {{ formatTime(dialogue.end_time) }}
              </div>
            </div>
            <div class="segment-actions">
              <el-button circle size="small" @click.stop="playSegment(index)" title="播放">
                <el-icon><VideoPlay /></el-icon>
              </el-button>
              <el-button circle size="small" @click.stop="editSegment(dialogue)" title="编辑">
                <el-icon><Edit /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- Inspector Panel -->
        <div class="inspector-panel">
          <div v-if="currentDialogue" class="panel-sections">
            <!-- Current Segment Info -->
            <div class="panel-section">
              <div class="panel-title">当前段落</div>
              <div class="property-item">
                <span class="property-label">序号</span>
                <span class="property-value">#{{ currentSegmentIndex + 1 }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">说话人</span>
                <span class="property-value">
                  {{ currentDialogue.type === 'narration' ? '旁白' : currentDialogue.character?.name }}
                </span>
              </div>
              <div class="property-item">
                <span class="property-label">时长</span>
                <span class="property-value">
                  {{ ((currentDialogue.end_time || 0) - (currentDialogue.start_time || 0)).toFixed(1) }}秒
                </span>
              </div>
              <div class="property-item">
                <span class="property-label">状态</span>
                <el-tag :type="currentDialogue.status === 'generated' ? 'success' : 'info'" size="small">
                  {{ getStatusText(currentDialogue.status) }}
                </el-tag>
              </div>
            </div>

            <!-- Audio Properties -->
            <div class="panel-section">
              <div class="panel-title">音频属性</div>
              <div class="property-item">
                <span class="property-label">采样率</span>
                <span class="property-value">48 kHz</span>
              </div>
              <div class="property-item">
                <span class="property-label">比特率</span>
                <span class="property-value">320 kbps</span>
              </div>
              <div class="property-item">
                <span class="property-label">声道</span>
                <span class="property-value">立体声</span>
              </div>
              <div class="property-item">
                <span class="property-label">文件大小</span>
                <span class="property-value">{{ audioFileSize }}</span>
              </div>
            </div>

            <!-- Voice Parameters -->
            <div class="panel-section">
              <div class="panel-title">语音参数</div>
              <div class="property-item">
                <span class="property-label">语速</span>
                <span class="property-value">{{ currentDialogue.voice_config?.speed || 1.0 }}x</span>
              </div>
              <div class="property-item">
                <span class="property-label">音调</span>
                <span class="property-value">{{ currentDialogue.voice_config?.pitch || 0 }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">音量</span>
                <span class="property-value">{{ currentDialogue.voice_config?.volume || 85 }}%</span>
              </div>
            </div>

            <!-- TTS Engine -->
            <div class="panel-section" v-if="currentDialogue.character">
              <div class="panel-title">TTS引擎</div>
              <div class="property-item">
                <span class="property-label">服务商</span>
                <span class="property-value">
                  {{ currentDialogue.character.voice_config?.engine || 'Azure' }}
                </span>
              </div>
              <div class="property-item">
                <span class="property-label">声音模型</span>
                <span class="property-value">
                  {{ currentDialogue.character.voice_config?.voice_id || '未配置' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Audio Element -->
    <audio ref="audioRef" :src="audioUrl" @timeupdate="updateProgress" @ended="onAudioEnded"></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, Download, RefreshRight, ZoomIn, ZoomOut,
  DArrowLeft, DArrowRight, CaretLeft, CaretRight,
  VideoPlay, VideoPause, MagicStick, Edit
} from '@element-plus/icons-vue'
import { useDialogueStore } from '@/stores/dialogue'
import { useChapterStore } from '@/stores/chapter'
import type { Dialogue } from '@/types'

const route = useRoute()
const router = useRouter()
const dialogueStore = useDialogueStore()
const chapterStore = useChapterStore()

// Refs
const audioRef = ref<HTMLAudioElement>()
const waveformRef = ref<HTMLElement>()

// State
const chapterId = ref(Number(route.params.chapterId))
const dialogues = ref<Dialogue[]>([])
const currentSegmentIndex = ref(0)
const isPlaying = ref(false)
const progress = ref(0)
const volume = ref(75)
const playbackSpeed = ref(1.0)
const playbackSpeeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
const waveformMode = ref<'wave' | 'spectrum'>('wave')
const currentTime = ref('00:00')
const audioUrl = ref('')

// Computed
const currentDialogue = computed(() => dialogues.value[currentSegmentIndex.value])
const chapterTitle = computed(() => chapterStore.currentChapter?.title || '章节')
const chapterStatus = computed(() => {
  const generated = dialogues.value.filter(d => d.status === 'generated').length
  const total = dialogues.value.length
  return total === generated ? '已生成' : `${generated}/${total} 已生成`
})

const totalDuration = computed(() => {
  const total = dialogues.value.reduce((sum, d) => sum + ((d.end_time || 0) - (d.start_time || 0)), 0)
  return formatTime(total)
})

const audioFileSize = computed(() => {
  // Mock file size calculation
  const duration = (currentDialogue.value?.end_time || 0) - (currentDialogue.value?.start_time || 0)
  const sizeKB = Math.round(duration * 40) // Approximate 320kbps
  return sizeKB > 1024 ? `${(sizeKB / 1024).toFixed(1)} MB` : `${sizeKB} KB`
})

const waveformBars = computed(() => {
  // Generate random waveform bars for visualization
  return Array.from({ length: 50 }, (_, i) => ({
    height: Math.random() * 80 + 20,
    delay: i * 0.1
  }))
})

const timelineMarkers = computed(() => {
  const duration = dialogues.value.reduce((sum, d) => sum + ((d.end_time || 0) - (d.start_time || 0)), 0)
  return [
    { position: 0, time: '0:00' },
    { position: 25, time: formatTime(duration * 0.25) },
    { position: 50, time: formatTime(duration * 0.5) },
    { position: 75, time: formatTime(duration * 0.75) },
    { position: 100, time: formatTime(duration) }
  ]
})

// Methods
const loadChapterData = async () => {
  try {
    await chapterStore.fetchChapter(chapterId.value)
    const result = await dialogueStore.fetchDialogues(chapterId.value)
    dialogues.value = result
    
    // Load merged audio if available
    // audioUrl.value = `/api/audio/chapters/${chapterId.value}/merged`
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待生成',
    generating: '生成中',
    generated: '已生成',
    failed: '失败'
  }
  return statusMap[status] || status
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
  currentTime.value = formatTime(current)
}

const onAudioEnded = () => {
  isPlaying.value = false
  progress.value = 0
}

const setPlaybackSpeed = (speed: number) => {
  playbackSpeed.value = speed
  if (audioRef.value) {
    audioRef.value.playbackRate = speed
  }
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

const previousSegment = () => {
  if (currentSegmentIndex.value > 0) {
    currentSegmentIndex.value--
    playSegment(currentSegmentIndex.value)
  }
}

const nextSegment = () => {
  if (currentSegmentIndex.value < dialogues.value.length - 1) {
    currentSegmentIndex.value++
    playSegment(currentSegmentIndex.value)
  }
}

const selectSegment = (index: number) => {
  currentSegmentIndex.value = index
}

const playSegment = (index: number) => {
  currentSegmentIndex.value = index
  // Load and play individual segment audio
  const dialogue = dialogues.value[index]
  if (dialogue.audio_path) {
    audioUrl.value = dialogue.audio_path
    setTimeout(() => {
      audioRef.value?.play()
      isPlaying.value = true
    }, 100)
  } else {
    ElMessage.warning('该段落尚未生成音频')
  }
}

const editSegment = (dialogue: Dialogue) => {
  router.push(`/projects/${route.params.id}/editor?dialogue=${dialogue.id}`)
}

const zoomIn = () => {
  ElMessage.info('放大功能开发中')
}

const zoomOut = () => {
  ElMessage.info('缩小功能开发中')
}

const regenerateAudio = () => {
  ElMessage.info('重新生成功能开发中')
}

const exportAudio = () => {
  ElMessage.info('导出音频功能开发中')
}

const goBack = () => {
  router.back()
}

// Lifecycle
onMounted(() => {
  loadChapterData()
  
  // Set volume
  if (audioRef.value) {
    audioRef.value.volume = volume.value / 100
  }
})

onUnmounted(() => {
  if (audioRef.value) {
    audioRef.value.pause()
  }
})
</script>

<style scoped lang="scss">
.audio-preview {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
  color: #e0e0e0;
}

.header {
  height: 60px;
  background: #252525;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #333;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  background: #2a2a2a;
  border: none;
  color: #e0e0e0;
  
  &:hover {
    background: #3a3a3a;
  }
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.waveform-section {
  flex: 1;
  background: #202020;
  padding: 32px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.waveform-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.chapter-info h2 {
  font-size: 24px;
  margin: 0 0 8px 0;
}

.chapter-meta {
  font-size: 14px;
  color: #999;
}

.waveform-tools {
  display: flex;
  gap: 8px;
}

.waveform-canvas {
  flex: 1;
  background: #1a1a1a;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
  margin-bottom: 24px;
  min-height: 300px;
}

.waveform-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #666;
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.waveform-visual {
  position: absolute;
  bottom: 30px;
  left: 0;
  right: 0;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.wave-bars {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 100%;
}

.wave-bar {
  width: 4px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  opacity: 0.3;
  animation: wave 1.5s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { height: 20%; }
  50% { height: 100%; }
}

.timeline-markers {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30px;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  padding: 0 12px;
  font-size: 11px;
  color: #999;
}

.marker {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.marker-line {
  width: 1px;
  height: 20px;
  background: #667eea;
}

.marker-label {
  margin-top: 4px;
  font-size: 10px;
}

.playback-controls {
  background: #2a2a2a;
  border-radius: 16px;
  padding: 24px;
}

.progress-bar {
  margin-bottom: 16px;
}

.time-display {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #999;
}

.controls-main {
  display: flex;
  align-items: center;
  gap: 24px;
}

.play-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.play-btn {
  width: 64px;
  height: 64px;
  font-size: 24px;
}

.volume-control {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.volume-icon {
  font-size: 20px;
}

.volume-text {
  font-size: 12px;
  color: #999;
  min-width: 40px;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bottom-panel {
  height: 280px;
  background: #202020;
  border-top: 1px solid #333;
  display: flex;
}

.segments-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.segment-item {
  background: #2a2a2a;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 16px;
  
  &:hover {
    background: #353535;
  }
  
  &.active {
    background: rgba(102, 126, 234, 0.1);
    border-left: 3px solid #667eea;
  }
}

.segment-number {
  width: 40px;
  height: 40px;
  background: #3a3a3a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.segment-content {
  flex: 1;
  min-width: 0;
}

.segment-speaker {
  font-size: 12px;
  color: #667eea;
  margin-bottom: 4px;
}

.segment-text {
  font-size: 13px;
  color: #e0e0e0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.segment-time {
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.segment-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.inspector-panel {
  width: 320px;
  border-left: 1px solid #333;
  padding: 16px;
  overflow-y: auto;
}

.panel-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.panel-section {
  &:not(:last-child) {
    padding-bottom: 24px;
    border-bottom: 1px solid #333;
  }
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #999;
  text-transform: uppercase;
}

.property-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.property-label {
  color: #999;
}

.property-value {
  color: #e0e0e0;
  font-weight: 600;
}
</style>

