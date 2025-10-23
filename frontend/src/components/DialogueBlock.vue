<template>
  <div class="dialogue-block" :class="{ selected, 'is-narration': dialogue.type === 'narration' }">
    <div class="dialogue-header">
      <div class="dialogue-info">
        <el-tag :type="dialogue.type === 'dialogue' ? 'primary' : 'info'" size="small">
          {{ dialogue.type === 'dialogue' ? '对话' : '旁白' }}
        </el-tag>
        <span v-if="dialogue.character" class="character-name">
          {{ dialogue.character.name }}
        </span>
        <span class="dialogue-order">#{{ dialogue.order_index }}</span>
      </div>
      
      <div class="dialogue-actions">
        <el-tag
          v-if="dialogue.status"
          :type="statusType"
          size="small"
        >
          {{ statusText }}
        </el-tag>
        
        <el-button-group size="small">
          <el-button
            v-if="dialogue.audio_path"
            :icon="VideoPlay"
            @click="emit('play', dialogue)"
            title="播放"
          />
          <el-button
            :icon="RefreshRight"
            @click="emit('generate', dialogue)"
            :loading="generating"
            title="生成音频"
          />
          <el-button
            :icon="Edit"
            @click="emit('edit', dialogue)"
            title="编辑"
          />
          <el-button
            :icon="Delete"
            @click="emit('delete', dialogue)"
            type="danger"
            title="删除"
          />
        </el-button-group>
      </div>
    </div>
    
    <div class="dialogue-content" @click="emit('select', dialogue)">
      <el-input
        v-if="editing"
        v-model="editContent"
        type="textarea"
        :autosize="{ minRows: 2, maxRows: 10 }"
        @blur="onSave"
        @keydown.ctrl.enter="onSave"
      />
      <p v-else>{{ dialogue.content }}</p>
    </div>
    
    <div v-if="dialogue.audio_path" class="dialogue-waveform">
      <div class="waveform-placeholder">
        <span>音频时长: {{ formatDuration(dialogue.start_time, dialogue.end_time) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { VideoPlay, Edit, Delete, RefreshRight } from '@element-plus/icons-vue'
import type { Dialogue } from '@/types'

interface Props {
  dialogue: Dialogue
  selected?: boolean
  generating?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  generating: false,
})

const emit = defineEmits<{
  play: [dialogue: Dialogue]
  generate: [dialogue: Dialogue]
  edit: [dialogue: Dialogue]
  delete: [dialogue: Dialogue]
  select: [dialogue: Dialogue]
  update: [dialogue: Dialogue, content: string]
}>()

const editing = ref(false)
const editContent = ref(props.dialogue.content)

// 状态类型
const statusType = computed(() => {
  const statusMap: Record<string, any> = {
    pending: 'info',
    generating: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return statusMap[props.dialogue.status] || 'info'
})

// 状态文本
const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    pending: '待生成',
    generating: '生成中',
    completed: '已完成',
    failed: '失败',
  }
  return statusMap[props.dialogue.status] || '未知'
})

// 格式化时长
const formatDuration = (start?: number, end?: number) => {
  if (!start && !end) return '--'
  const duration = (end || 0) - (start || 0)
  return `${duration.toFixed(2)}s`
}

// 开始编辑
const startEdit = () => {
  editing.value = true
  editContent.value = props.dialogue.content
}

// 保存编辑
const onSave = () => {
  if (editContent.value !== props.dialogue.content) {
    emit('update', props.dialogue, editContent.value)
  }
  editing.value = false
}

defineExpose({
  startEdit,
})
</script>

<style scoped>
.dialogue-block {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  transition: all 0.3s;
}

.dialogue-block:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.dialogue-block.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.dialogue-block.is-narration {
  background: #f5f7fa;
}

.dialogue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.dialogue-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.character-name {
  font-weight: 500;
  color: #303133;
}

.dialogue-order {
  color: #909399;
  font-size: 12px;
}

.dialogue-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialogue-content {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.dialogue-content:hover {
  background: #ebeef5;
}

.dialogue-content p {
  margin: 0;
  line-height: 1.6;
  color: #303133;
  word-break: break-all;
}

.dialogue-waveform {
  margin-top: 12px;
  padding: 8px;
  background: #f0f2f5;
  border-radius: 4px;
}

.waveform-placeholder {
  text-align: center;
  color: #909399;
  font-size: 12px;
}
</style>

