<template>
  <div class="project-detail-page">
    <div v-loading="projectStore.loading" class="detail-container">
      <!-- 项目头部 -->
      <div class="project-header">
        <el-button :icon="ArrowLeft" @click="router.push('/projects')">
          返回项目列表
        </el-button>
        
        <div v-if="project" class="header-content">
          <div class="project-info">
            <div class="cover-wrapper">
              <img v-if="project.cover_image" :src="project.cover_image" alt="封面" />
              <div v-else class="cover-placeholder">
                <el-icon :size="48"><Document /></el-icon>
              </div>
            </div>
            
            <div class="info-text">
              <h1>{{ project.name }}</h1>
              <p class="description">{{ project.description || '暂无描述' }}</p>
              
              <div class="meta-info">
                <el-tag :type="getStatusType(project.status)">
                  {{ getStatusText(project.status) }}
                </el-tag>
                <span>创建于 {{ formatDate(project.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="header-actions">
            <el-button :icon="Edit" @click="handleEditProject">编辑</el-button>
            <el-button :icon="Setting" @click="handleSettings">设置</el-button>
            <el-dropdown trigger="click" @command="handleMoreAction">
              <el-button :icon="MoreFilled">更多</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="duplicate">复制项目</el-dropdown-item>
                  <el-dropdown-item command="export">导出项目</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除项目</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
      
      <!-- 统计卡片 -->
      <div v-if="project" class="stats-cards">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#409eff"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ project.chapters_count || 0 }}</div>
              <div class="stat-label">章节数</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#67c23a"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ project.characters_count || 0 }}</div>
              <div class="stat-label">角色数</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#e6a23c"><Clock /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ formatDuration(project.total_duration) }}</div>
              <div class="stat-label">总时长</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="32" color="#f56c6c"><Headset /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ audioProgress }}%</div>
              <div class="stat-label">音频进度</div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 快捷操作 -->
      <div class="quick-actions">
        <h2>快捷操作</h2>
        <div class="actions-grid">
          <el-card class="action-card" @click="handleImportText">
            <div class="action-icon">
              <el-icon :size="48"><Upload /></el-icon>
            </div>
            <div class="action-title">导入文本</div>
            <div class="action-desc">上传TXT、DOCX或PDF文件</div>
          </el-card>
          
          <el-card class="action-card" @click="handleVoiceConfig">
            <div class="action-icon">
              <el-icon :size="48"><Microphone /></el-icon>
            </div>
            <div class="action-title">配音管理</div>
            <div class="action-desc">配置角色声音和参数</div>
          </el-card>
          
          <el-card class="action-card" @click="handleEditDialogue">
            <div class="action-icon">
              <el-icon :size="48"><Edit /></el-icon>
            </div>
            <div class="action-title">对话编辑</div>
            <div class="action-desc">编辑和调整对话内容</div>
          </el-card>
          
          <el-card class="action-card" @click="handleAudioPreview">
            <div class="action-icon">
              <el-icon :size="48"><Headset /></el-icon>
            </div>
            <div class="action-title">音频预览</div>
            <div class="action-desc">预览和播放生成的音频</div>
          </el-card>
          
          <el-card class="action-card" @click="handleGenerateAudio">
            <div class="action-icon">
              <el-icon :size="48"><VideoPlay /></el-icon>
            </div>
            <div class="action-title">生成音频</div>
            <div class="action-desc">批量生成或单章节生成</div>
          </el-card>
          
          <el-card class="action-card" @click="handleExport">
            <div class="action-icon">
              <el-icon :size="48"><Download /></el-icon>
            </div>
            <div class="action-title">导出项目</div>
            <div class="action-desc">导出音频文件</div>
          </el-card>
        </div>
      </div>
      
      <!-- 章节列表 -->
      <div class="chapters-section">
        <div class="section-header">
          <h2>章节列表</h2>
          <el-button type="primary" :icon="Plus" @click="handleAddChapter">
            添加章节
          </el-button>
        </div>
        
        <el-table
          v-loading="chapterStore.loading"
          :data="chapterStore.chapters"
          stripe
          @row-click="handleChapterClick"
        >
          <el-table-column prop="order_index" label="序号" width="80" />
          <el-table-column prop="title" label="章节标题" min-width="200" />
          <el-table-column prop="word_count" label="字数" width="100">
            <template #default="{ row }">
              {{ row.word_count?.toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="时长" width="100">
            <template #default="{ row }">
              {{ formatDuration(row.duration) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="{ row }">
              <el-button-group size="small">
                <el-button :icon="View" @click.stop="handleViewChapter(row)">
                  查看
                </el-button>
                <el-button :icon="Edit" @click.stop="handleEditChapter(row)">
                  编辑
                </el-button>
                <el-button :icon="VideoPlay" @click.stop="handleGenerateChapter(row)">
                  生成
                </el-button>
                <el-button :icon="Delete" type="danger" @click.stop="handleDeleteChapter(row)">
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
        
        <el-empty v-if="!chapterStore.loading && !chapterStore.hasChapters" description="暂无章节，点击导入文本开始" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Document, Edit, Setting, MoreFilled, User, Clock, Headset,
  Upload, Microphone, VideoPlay, Download, Plus, View, Delete
} from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import { useChapterStore } from '@/stores/chapter'
import type { Project, Chapter } from '@/types'

const router = useRouter()
const route = useRoute()
const projectId = computed(() => Number(route.params.id))

const projectStore = useProjectStore()
const chapterStore = useChapterStore()

const project = computed(() => projectStore.currentProject)

// 音频进度
const audioProgress = computed(() => {
  if (!project.value?.chapters_count) return 0
  // TODO: 计算实际音频生成进度
  return 0
})

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    draft: '',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status] || ''
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

// 格式化日期
const formatDate = (date: string | Date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

// 格式化时长
const formatDuration = (seconds?: number) => {
  if (!seconds) return '--:--'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }
  return `${minutes}:${String(secs).padStart(2, '0')}`
}

// 编辑项目
const handleEditProject = () => {
  ElMessage.info('编辑功能开发中')
}

// 设置
const handleSettings = () => {
  ElMessage.info('设置功能开发中')
}

// 更多操作
const handleMoreAction = (command: string) => {
  switch (command) {
    case 'duplicate':
      ElMessage.info('复制功能开发中')
      break
    case 'export':
      handleExport()
      break
    case 'delete':
      handleDeleteProject()
      break
  }
}

// 删除项目
const handleDeleteProject = async () => {
  if (!project.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.value.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await projectStore.deleteProject(project.value.id)
    ElMessage.success('删除成功')
    router.push('/projects')
  } catch (error) {
    // 取消操作
  }
}

// 快捷操作
const handleImportText = () => {
  router.push(`/projects/${projectId.value}/import`)
}

const handleVoiceConfig = () => {
  router.push(`/projects/${projectId.value}/voice-config`)
}

const handleEditDialogue = () => {
  router.push(`/projects/${projectId.value}/editor`)
}

const handleAudioPreview = () => {
  router.push(`/projects/${projectId.value}/preview`)
}

const handleGenerateAudio = () => {
  ElMessage.info('批量生成功能开发中')
}

const handleExport = () => {
  router.push(`/projects/${projectId.value}/export`)
}

// 章节操作
const handleAddChapter = () => {
  ElMessage.info('添加章节功能开发中')
}

const handleChapterClick = (chapter: Chapter) => {
  router.push(`/projects/${projectId.value}/editor?chapter=${chapter.id}`)
}

const handleViewChapter = (chapter: Chapter) => {
  router.push(`/projects/${projectId.value}/editor?chapter=${chapter.id}`)
}

const handleEditChapter = (chapter: Chapter) => {
  router.push(`/projects/${projectId.value}/editor?chapter=${chapter.id}`)
}

const handleGenerateChapter = (chapter: Chapter) => {
  ElMessage.info('生成章节音频功能开发中')
}

const handleDeleteChapter = async (chapter: Chapter) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除章节"${chapter.title}"吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await chapterStore.deleteChapter(chapter.id)
    ElMessage.success('删除成功')
  } catch (error) {
    // 取消操作
  }
}

onMounted(async () => {
  await projectStore.fetchProject(projectId.value)
  await chapterStore.fetchChapters(projectId.value)
})
</script>

<style scoped>
.project-detail-page {
  min-height: 100vh;
  padding: 24px;
  background: #f5f7fa;
}

.detail-container {
  max-width: 1400px;
  margin: 0 auto;
}

.project-header {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-top: 16px;
}

.project-info {
  display: flex;
  gap: 24px;
}

.cover-wrapper {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.cover-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #909399;
}

.info-text h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.description {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 14px;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: default;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.quick-actions h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.action-card {
  cursor: pointer;
  text-align: center;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-icon {
  color: #409eff;
  margin-bottom: 12px;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.action-desc {
  font-size: 12px;
  color: #909399;
}

.chapters-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

:deep(.el-table) {
  cursor: default;
}

:deep(.el-table__row) {
  cursor: pointer;
}
</style>

