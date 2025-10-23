<template>
  <el-card class="project-card" :body-style="{ padding: '0' }" shadow="hover" @click="emit('click', project)">
    <div class="card-cover">
      <img v-if="project.cover_image" :src="project.cover_image" alt="项目封面" />
      <div v-else class="cover-placeholder">
        <el-icon :size="48"><Document /></el-icon>
      </div>
      <el-tag class="status-tag" :type="statusType" size="small">
        {{ statusText }}
      </el-tag>
    </div>
    
    <div class="card-content">
      <h3 class="project-title">{{ project.name }}</h3>
      <p v-if="project.description" class="project-description">
        {{ project.description }}
      </p>
      
      <div class="project-stats">
        <div class="stat-item">
          <el-icon><Reading /></el-icon>
          <span>{{ project.chapters_count }} 章节</span>
        </div>
        <div class="stat-item">
          <el-icon><User /></el-icon>
          <span>{{ project.characters_count }} 角色</span>
        </div>
        <div class="stat-item">
          <el-icon><Clock /></el-icon>
          <span>{{ formatDuration(project.total_duration) }}</span>
        </div>
      </div>
      
      <div class="card-footer">
        <span class="update-time">{{ formatTime(project.updated_at) }}</span>
        <div class="card-actions" @click.stop>
          <el-button size="small" type="primary" @click="emit('edit', project)">
            编辑
          </el-button>
          <el-dropdown @command="handleCommand">
            <el-button size="small" :icon="MoreFilled" circle />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="export">导出</el-dropdown-item>
                <el-dropdown-item command="duplicate">复制</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Document, Reading, User, Clock, MoreFilled } from '@element-plus/icons-vue'
import type { Project } from '@/types'

interface Props {
  project: Project
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [project: Project]
  edit: [project: Project]
  export: [project: Project]
  duplicate: [project: Project]
  delete: [project: Project]
}>()

// 状态类型
const statusType = computed(() => {
  const statusMap: Record<string, any> = {
    draft: 'info',
    processing: 'warning',
    completed: 'success',
  }
  return statusMap[props.project.status] || 'info'
})

// 状态文本
const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    processing: '处理中',
    completed: '已完成',
  }
  return statusMap[props.project.status] || '未知'
})

// 格式化时长
const formatDuration = (seconds: number) => {
  if (!seconds) return '0分钟'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

// 格式化时间
const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN')
}

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  switch (command) {
    case 'export':
      emit('export', props.project)
      break
    case 'duplicate':
      emit('duplicate', props.project)
      break
    case 'delete':
      emit('delete', props.project)
      break
  }
}
</script>

<style scoped>
.project-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.project-card:hover {
  transform: translateY(-4px);
}

.card-cover {
  position: relative;
  width: 100%;
  height: 160px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: white;
}

.status-tag {
  position: absolute;
  top: 12px;
  right: 12px;
}

.card-content {
  padding: 16px;
}

.project-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}

.project-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding: 12px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.stat-item .el-icon {
  color: #909399;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.update-time {
  font-size: 12px;
  color: #909399;
}

.card-actions {
  display: flex;
  gap: 8px;
}
</style>

