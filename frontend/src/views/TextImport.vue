<template>
  <div class="text-import-page">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="router.back()">返回</el-button>
      <h1>文本导入</h1>
    </div>
    
    <div class="import-container">
      <el-steps :active="currentStep" align-center finish-status="success">
        <el-step title="上传文件" />
        <el-step title="章节识别" />
        <el-step title="确认导入" />
      </el-steps>
      
      <!-- 步骤1: 上传文件 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-upload
          ref="uploadRef"
          class="upload-box"
          drag
          :auto-upload="false"
          :limit="1"
          accept=".txt,.docx,.pdf"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">
            <p>将文件拖到此处，或<em>点击上传</em></p>
            <p class="upload-hint">支持 TXT、DOCX、PDF 格式</p>
          </div>
        </el-upload>
        
        <div v-if="selectedFile" class="file-info">
          <el-alert type="success" :closable="false">
            <template #title>
              已选择文件: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
            </template>
          </el-alert>
          
          <div class="actions">
            <el-button @click="clearFile">重新选择</el-button>
            <el-button type="primary" @click="handleUpload" :loading="uploading">
              下一步
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 步骤2: 章节识别 -->
      <div v-if="currentStep === 1" class="step-content">
        <el-alert
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #title>
            自动识别到 {{ chapters.length }} 个章节，您可以编辑章节标题和内容
          </template>
        </el-alert>
        
        <div class="chapters-preview">
          <el-collapse v-model="activeChapters">
            <el-collapse-item
              v-for="(chapter, index) in chapters"
              :key="index"
              :name="index"
            >
              <template #title>
                <div class="chapter-title-edit">
                  <span class="chapter-index">第 {{ chapter.order_index }} 章</span>
                  <el-input
                    v-model="chapter.title"
                    placeholder="章节标题"
                    @click.stop
                  />
                </div>
              </template>
              
              <el-input
                v-model="chapter.content"
                type="textarea"
                :rows="10"
                placeholder="章节内容"
              />
              <div class="chapter-info">
                字数: {{ chapter.word_count }}
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
        
        <div class="actions">
          <el-button @click="currentStep = 0">上一步</el-button>
          <el-button type="primary" @click="currentStep = 2">
            下一步
          </el-button>
        </div>
      </div>
      
      <!-- 步骤3: 确认导入 -->
      <div v-if="currentStep === 2" class="step-content">
        <el-result
          icon="success"
          title="准备就绪"
          :sub-title="`共 ${chapters.length} 个章节，总计 ${totalWords} 字`"
        >
          <template #extra>
            <el-space>
              <el-button @click="currentStep = 1">返回修改</el-button>
              <el-button type="primary" @click="handleConfirm" :loading="importing">
                确认导入
              </el-button>
            </el-space>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, UploadFile, UploadInstance } from 'element-plus'
import { ArrowLeft, UploadFilled } from '@element-plus/icons-vue'
import { uploadChapter } from '@/api/chapter'
import type { Chapter } from '@/types'

const router = useRouter()
const route = useRoute()
const projectId = computed(() => Number(route.params.id))

// 步骤控制
const currentStep = ref(0)
const uploadRef = ref<UploadInstance>()
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const importing = ref(false)

// 章节数据
const chapters = ref<Chapter[]>([])
const activeChapters = ref<number[]>([])

// 总字数
const totalWords = computed(() => {
  return chapters.value.reduce((sum, ch) => sum + ch.word_count, 0)
})

// 文件选择
const handleFileChange = (uploadFile: UploadFile) => {
  if (uploadFile.raw) {
    selectedFile.value = uploadFile.raw
  }
}

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 清除文件
const clearFile = () => {
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 上传文件
const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  try {
    const result = await uploadChapter(projectId.value, selectedFile.value, (progress) => {
      console.log('上传进度:', progress)
    })
    
    chapters.value = result.chapters
    currentStep.value = 1
    ElMessage.success('文件上传成功，已自动识别章节')
  } catch (error) {
    ElMessage.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

// 确认导入
const handleConfirm = async () => {
  importing.value = true
  try {
    // 章节已经在后端创建，直接跳转
    ElMessage.success('导入成功！')
    router.push(`/projects/${projectId.value}/voice-config`)
  } catch (error) {
    ElMessage.error('导入失败，请重试')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.text-import-page {
  min-height: 100vh;
  padding: 24px;
  background: white;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.import-container {
  max-width: 1000px;
  margin: 0 auto;
}

.step-content {
  margin-top: 40px;
}

.upload-box {
  margin: 40px 0;
}

.upload-icon {
  font-size: 67px;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
}

.upload-text p {
  margin: 8px 0;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.file-info {
  margin-top: 24px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.chapters-preview {
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.chapter-title-edit {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  padding-right: 16px;
}

.chapter-index {
  min-width: 80px;
  font-weight: 500;
  color: #409eff;
}

.chapter-title-edit .el-input {
  flex: 1;
}

.chapter-info {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  text-align: right;
}
</style>

