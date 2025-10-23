<template>
  <el-card class="character-card" shadow="hover">
    <div class="character-header">
      <el-avatar :size="60" :src="character.avatar">
        <el-icon :size="30"><User /></el-icon>
      </el-avatar>
      
      <div class="character-info">
        <h3 class="character-name">{{ character.name }}</h3>
        <p v-if="character.description" class="character-description">
          {{ character.description }}
        </p>
      </div>
    </div>
    
    <div class="voice-config">
      <div class="config-item">
        <span class="config-label">引擎:</span>
        <el-tag size="small">{{ character.voice_config?.engine || '未配置' }}</el-tag>
      </div>
      <div class="config-item">
        <span class="config-label">音色:</span>
        <span class="config-value">{{ character.voice_config?.voice_id || '未选择' }}</span>
      </div>
      <div class="config-row">
        <div class="config-item">
          <span class="config-label">语速:</span>
          <span class="config-value">{{ character.voice_config?.speed || 1.0 }}</span>
        </div>
        <div class="config-item">
          <span class="config-label">音调:</span>
          <span class="config-value">{{ character.voice_config?.pitch || 0 }}</span>
        </div>
      </div>
    </div>
    
    <div class="character-stats">
      <div class="stat-item">
        <span class="stat-label">对话数</span>
        <span class="stat-value">{{ character.dialogue_count }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">总时长</span>
        <span class="stat-value">{{ formatDuration(character.total_duration) }}</span>
      </div>
    </div>
    
    <div class="character-actions">
      <el-button type="primary" size="small" @click="emit('config', character)">
        配置声音
      </el-button>
      <el-button size="small" @click="emit('test', character)">
        试听
      </el-button>
      <el-button size="small" type="danger" plain @click="emit('delete', character)">
        删除
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { User } from '@element-plus/icons-vue'
import type { Character } from '@/types'

interface Props {
  character: Character
}

defineProps<Props>()

const emit = defineEmits<{
  config: [character: Character]
  test: [character: Character]
  delete: [character: Character]
}>()

// 格式化时长
const formatDuration = (seconds: number) => {
  if (!seconds) return '0s'
  if (seconds < 60) return `${seconds.toFixed(0)}s`
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${minutes}m ${secs}s`
}
</script>

<style scoped>
.character-card {
  height: 100%;
}

.character-header {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.character-info {
  flex: 1;
}

.character-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.character-description {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.voice-config {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.config-item:last-child {
  margin-bottom: 0;
}

.config-row {
  display: flex;
  gap: 16px;
}

.config-row .config-item {
  flex: 1;
}

.config-label {
  font-size: 13px;
  color: #606266;
  min-width: 45px;
}

.config-value {
  font-size: 13px;
  color: #303133;
}

.character-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 4px;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 500;
  color: #409eff;
}

.character-actions {
  display: flex;
  gap: 8px;
}

.character-actions .el-button {
  flex: 1;
}
</style>

