<template>
  <div 
    class="dialogue-edit-block"
    :class="{ selected, 'is-narration': dialogue.type === 'narration' }"
    @click="$emit('select', dialogue)"
  >
    <div class="block-header">
      <div class="left-info">
        <span class="index-badge">{{ index + 1 }}</span>
        
        <el-tag :type="dialogue.type === 'dialogue' ? 'primary' : ''" size="small">
          {{ dialogue.type === 'dialogue' ? '对话' : '旁白' }}
        </el-tag>
        
        <span v-if="dialogue.character_id && character" class="character-name">
          <img v-if="character.avatar" :src="character.avatar" class="char-avatar" />
          {{ character.name }}
        </span>
        
        <el-tag
          v-if="dialogue.status"
          :type="getStatusType(dialogue.status)"
          size="small"
        >
          {{ getStatusText(dialogue.status) }}
        </el-tag>
      </div>
      
      <div class="actions">
        <el-button-group size="small">
          <el-button :icon="Top" @click.stop="$emit('move-up', dialogue)">上移</el-button>
          <el-button :icon="Bottom" @click.stop="$emit('move-down', dialogue)">下移</el-button>
        </el-button-group>
        
        <el-button
          v-if="dialogue.audio_path"
          size="small"
          :icon="VideoPlay"
          @click.stop="$emit('play', dialogue)"
        >
          播放
        </el-button>
        
        <el-button
          size="small"
          type="primary"
          :icon="VideoPlay"
          :loading="generating"
          @click.stop="handleGenerate"
        >
          生成
        </el-button>
        
        <el-button
          size="small"
          type="danger"
          :icon="Delete"
          @click.stop="handleDelete"
        >
          删除
        </el-button>
      </div>
    </div>
    
    <div class="block-content">
      <el-input
        v-model="localContent"
        type="textarea"
        :rows="3"
        resize="vertical"
        placeholder="请输入对话内容..."
        @blur="handleContentChange"
        @click.stop
      />
      
      <div class="content-meta">
        <span class="char-count">{{ localContent.length }} 字符</span>
        <span v-if="dialogue.audio_path" class="duration">
          时长: {{ formatDuration(dialogue.end_time - dialogue.start_time) }}
        </span>
      </div>
    </div>
    
    <div v-if="dialogue.audio_path" class="audio-info">
      <div class="waveform-placeholder">
        <el-icon><SwitchButton /></el-icon>
        <span>音频波形</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessageBox } from 'element-plus'
import { VideoPlay, Delete, Top, Bottom, SwitchButton } from '@element-plus/icons-vue'
import type { Dialogue, Character } from '@/types'

interface Props {
  dialogue: Dialogue
  index: number
  characters: Character[]
  selected?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [dialogue: Dialogue]
  update: [dialogue: Dialogue]
  delete: [dialogue: Dialogue]
  generate: [dialogue: Dialogue]
  play: [dialogue: Dialogue]
  moveUp: [dialogue: Dialogue]
  moveDown: [dialogue: Dialogue]
}>()

const generating = ref(false)
const localContent = ref(props.dialogue.content || '')

// 当前角色
const character = computed(() => 
  props.characters.find(c => c.id === props.dialogue.character_id)
)

// 监听对话变化
watch(() => props.dialogue.content, (newContent) => {
  localContent.value = newContent || ''
})

// 内容变更
const handleContentChange = () => {
  if (localContent.value !== props.dialogue.content) {
    emit('update', {
      ...props.dialogue,
      content: localContent.value,
    })
  }
}

// 生成音频
const handleGenerate = async () => {
  generating.value = true
  try {
    emit('generate', props.dialogue)
  } finally {
    setTimeout(() => {
      generating.value = false
    }, 1000)
  }
}

// 删除
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这段对话吗？',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    emit('delete', props.dialogue)
  } catch (error) {
    // 取消操作
  }
}

// 状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    pending: '',
    generating: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status] || ''
}

// 状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '未生成',
    generating: '生成中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

// 格式化时长
const formatDuration = (seconds?: number) => {
  if (!seconds) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}
</script>

<style scoped>
.dialogue-edit-block {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: white;
  transition: all 0.3s;
  cursor: pointer;
}

.dialogue-edit-block:hover {
  border-color: #c6e2ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.dialogue-edit-block.selected {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.dialogue-edit-block.is-narration {
  background: #f9fafb;
}

.block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.left-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.index-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
}

.character-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.char-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.actions {
  display: flex;
  gap: 8px;
}

.block-content {
  margin-bottom: 12px;
}

.content-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.audio-info {
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.waveform-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 60px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #909399;
  font-size: 14px;
}

:deep(.el-textarea__inner) {
  font-family: inherit;
  line-height: 1.6;
}
</style>

