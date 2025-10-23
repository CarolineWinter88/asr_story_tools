<template>
  <div class="chapter-list">
    <div class="list-header">
      <h3>章节列表</h3>
      <el-button type="primary" size="small" :icon="Plus" @click="emit('add')">
        添加章节
      </el-button>
    </div>
    
    <el-scrollbar height="100%">
      <div class="chapter-items">
        <div
          v-for="chapter in chapters"
          :key="chapter.id"
          class="chapter-item"
          :class="{ active: chapter.id === selectedId }"
          @click="emit('select', chapter)"
        >
          <div class="chapter-main">
            <span class="chapter-order">{{ chapter.order_index }}</span>
            <div class="chapter-info">
              <h4 class="chapter-title">{{ chapter.title }}</h4>
              <div class="chapter-meta">
                <span>{{ chapter.word_count }} 字</span>
                <span v-if="chapter.duration">{{ formatDuration(chapter.duration) }}</span>
              </div>
            </div>
          </div>
          
          <div class="chapter-actions" @click.stop>
            <el-dropdown @command="(cmd) => handleCommand(cmd, chapter)">
              <el-button size="small" :icon="MoreFilled" circle text />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">编辑</el-dropdown-item>
                  <el-dropdown-item command="parse">解析对话</el-dropdown-item>
                  <el-dropdown-item command="generate">生成音频</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        
        <el-empty v-if="chapters.length === 0" description="暂无章节" />
      </div>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { Plus, MoreFilled } from '@element-plus/icons-vue'
import type { Chapter } from '@/types'

interface Props {
  chapters: Chapter[]
  selectedId?: number
}

defineProps<Props>()

const emit = defineEmits<{
  select: [chapter: Chapter]
  add: []
  edit: [chapter: Chapter]
  parse: [chapter: Chapter]
  generate: [chapter: Chapter]
  delete: [chapter: Chapter]
}>()

// 格式化时长
const formatDuration = (seconds: number) => {
  if (!seconds) return '0分钟'
  const minutes = Math.floor(seconds / 60)
  return `${minutes}分钟`
}

// 处理下拉菜单命令
const handleCommand = (command: string, chapter: Chapter) => {
  switch (command) {
    case 'edit':
      emit('edit', chapter)
      break
    case 'parse':
      emit('parse', chapter)
      break
    case 'generate':
      emit('generate', chapter)
      break
    case 'delete':
      emit('delete', chapter)
      break
  }
}
</script>

<style scoped>
.chapter-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
}

.list-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.chapter-items {
  padding: 8px;
}

.chapter-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
  cursor: pointer;
  transition: all 0.3s;
}

.chapter-item:hover {
  background: #f5f7fa;
}

.chapter-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}

.chapter-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.chapter-order {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 500;
}

.chapter-info {
  flex: 1;
}

.chapter-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.chapter-actions {
  display: flex;
  align-items: center;
}
</style>

