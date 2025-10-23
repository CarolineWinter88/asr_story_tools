<template>
  <div class="audio-player">
    <audio
      ref="audioRef"
      :src="src"
      @loadedmetadata="onLoadedMetadata"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @play="isPlaying = true"
      @pause="isPlaying = false"
    />
    
    <div class="player-controls">
      <el-button
        :icon="isPlaying ? VideoPause : VideoPlay"
        circle
        @click="togglePlay"
        :disabled="!src"
      />
      
      <div class="time-display">
        {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
      </div>
      
      <el-slider
        v-model="currentTime"
        :max="duration"
        :show-tooltip="false"
        @change="onSeek"
        class="progress-slider"
        :disabled="!src"
      />
      
      <div class="volume-control">
        <el-button
          :icon="volume === 0 ? Mute : VolumeIcon"
          circle
          size="small"
          @click="toggleMute"
        />
        <el-slider
          v-model="volume"
          :max="100"
          :show-tooltip="false"
          @change="onVolumeChange"
          class="volume-slider"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { VideoPlay, VideoPause, Mute } from '@element-plus/icons-vue'

const VolumeIcon = VideoPlay // 临时使用，实际应该用音量图标

interface Props {
  src?: string
  autoplay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: false,
})

const emit = defineEmits<{
  ended: []
}>()

const audioRef = ref<HTMLAudioElement>()
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(100)
const previousVolume = ref(100)

// 监听src变化
watch(() => props.src, (newSrc) => {
  if (newSrc && props.autoplay) {
    setTimeout(() => {
      play()
    }, 100)
  }
})

// 播放/暂停切换
const togglePlay = () => {
  if (isPlaying.value) {
    pause()
  } else {
    play()
  }
}

// 播放
const play = () => {
  audioRef.value?.play()
}

// 暂停
const pause = () => {
  audioRef.value?.pause()
}

// 停止
const stop = () => {
  pause()
  currentTime.value = 0
  if (audioRef.value) {
    audioRef.value.currentTime = 0
  }
}

// 跳转
const onSeek = (time: number) => {
  if (audioRef.value) {
    audioRef.value.currentTime = time
  }
}

// 音量变化
const onVolumeChange = (val: number) => {
  if (audioRef.value) {
    audioRef.value.volume = val / 100
  }
}

// 静音切换
const toggleMute = () => {
  if (volume.value === 0) {
    volume.value = previousVolume.value
  } else {
    previousVolume.value = volume.value
    volume.value = 0
  }
}

// 元数据加载
const onLoadedMetadata = () => {
  if (audioRef.value) {
    duration.value = audioRef.value.duration
  }
}

// 时间更新
const onTimeUpdate = () => {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime
  }
}

// 播放结束
const onEnded = () => {
  isPlaying.value = false
  currentTime.value = 0
  emit('ended')
}

// 格式化时间
const formatTime = (seconds: number) => {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 暴露方法
defineExpose({
  play,
  pause,
  stop,
})
</script>

<style scoped>
.audio-player {
  width: 100%;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.time-display {
  min-width: 100px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.progress-slider {
  flex: 1;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 150px;
}

.volume-slider {
  width: 100px;
}
</style>

