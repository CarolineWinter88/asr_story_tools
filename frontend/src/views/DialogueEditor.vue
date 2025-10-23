<template>
  <div class="dialogue-editor-page">
    <div class="editor-container">
      <!-- 顶部工具栏 -->
      <div class="toolbar">
        <div class="left-section">
          <el-button :icon="ArrowLeft" @click="router.back()">返回</el-button>
          <el-divider direction="vertical" />
          
          <el-select
            v-model="selectedChapterId"
            placeholder="选择章节"
            style="width: 200px"
            @change="handleChapterChange"
          >
            <el-option
              v-for="chapter in chapterStore.chapters"
              :key="chapter.id"
              :label="chapter.title"
              :value="chapter.id"
            />
          </el-select>
          
          <el-divider direction="vertical" />
          
          <el-button-group>
            <el-button :icon="Edit" @click="handleParseChapter">解析对话</el-button>
            <el-button :icon="Plus" @click="handleAddDialogue">添加段落</el-button>
            <el-button :icon="Delete" @click="handleBatchDelete">批量删除</el-button>
          </el-button-group>
        </div>
        
        <div class="right-section">
          <el-button :icon="Refresh" @click="handleRefresh">刷新</el-button>
          <el-button :icon="Download" @click="handleExportDialogues">导出对话</el-button>
          <el-button type="primary" :icon="VideoPlay" @click="handleGenerateAll">
            生成全部音频
          </el-button>
        </div>
      </div>
      
      <!-- 主编辑区域 -->
      <div class="editor-content">
        <!-- 左侧对话列表 -->
        <div v-loading="dialogueStore.loading" class="dialogue-list">
          <div v-if="!dialogueStore.hasDialogues" class="empty-state">
            <el-empty description="暂无对话数据">
              <el-button type="primary" @click="handleParseChapter">
                解析章节对话
              </el-button>
            </el-empty>
          </div>
          
          <div v-else class="dialogue-items">
            <DialogueEditBlock
              v-for="(dialogue, index) in dialogueStore.dialogues"
              :key="dialogue.id"
              :dialogue="dialogue"
              :index="index"
              :characters="characterStore.characters"
              :selected="selectedDialogueId === dialogue.id"
              @select="handleSelectDialogue"
              @update="handleUpdateDialogue"
              @delete="handleDeleteDialogue"
              @generate="handleGenerateDialogue"
              @play="handlePlayDialogue"
              @move-up="handleMoveUp"
              @move-down="handleMoveDown"
            />
          </div>
        </div>
        
        <!-- 右侧属性面板 -->
        <div class="properties-panel">
          <el-tabs v-model="activeTab">
            <!-- 对话属性 -->
            <el-tab-pane label="对话属性" name="dialogue">
              <div v-if="currentDialogue" class="property-form">
                <el-form label-width="100px">
                  <el-form-item label="类型">
                    <el-radio-group v-model="currentDialogue.type" @change="handlePropertyChange">
                      <el-radio value="dialogue">对话</el-radio>
                      <el-radio value="narration">旁白</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  
                  <el-form-item v-if="currentDialogue.type === 'dialogue'" label="角色">
                    <el-select
                      v-model="currentDialogue.character_id"
                      placeholder="选择角色"
                      @change="handlePropertyChange"
                    >
                      <el-option
                        v-for="char in characterStore.characters"
                        :key="char.id"
                        :label="char.name"
                        :value="char.id"
                      >
                        <div class="character-option">
                          <img v-if="char.avatar" :src="char.avatar" class="char-avatar" />
                          <span>{{ char.name }}</span>
                        </div>
                      </el-option>
                    </el-select>
                    <el-button
                      style="margin-top: 8px"
                      size="small"
                      @click="showAddCharacterDialog = true"
                    >
                      添加新角色
                    </el-button>
                  </el-form-item>
                  
                  <el-form-item label="文本内容">
                    <el-input
                      v-model="currentDialogue.content"
                      type="textarea"
                      :rows="6"
                      @blur="handlePropertyChange"
                    />
                    <div class="char-count">{{ currentDialogue.content?.length || 0 }} 字符</div>
                  </el-form-item>
                  
                  <el-form-item label="语速调整">
                    <el-slider
                      v-model="dialogueSpeed"
                      :min="0.5"
                      :max="2"
                      :step="0.1"
                      show-input
                      @change="handleSpeedChange"
                    />
                  </el-form-item>
                  
                  <el-form-item label="音量调整">
                    <el-slider
                      v-model="dialogueVolume"
                      :min="0"
                      :max="100"
                      show-input
                      @change="handleVolumeChange"
                    />
                  </el-form-item>
                  
                  <el-form-item label="停顿时长">
                    <el-input-number
                      v-model="dialoguePause"
                      :min="0"
                      :max="5"
                      :step="0.1"
                      @change="handlePauseChange"
                    />
                    <span style="margin-left: 8px; color: #909399;">秒</span>
                  </el-form-item>
                  
                  <el-form-item label="音频状态">
                    <el-tag :type="getAudioStatusType(currentDialogue.status)">
                      {{ getAudioStatusText(currentDialogue.status) }}
                    </el-tag>
                  </el-form-item>
                  
                  <el-form-item v-if="currentDialogue.audio_path" label="音频时长">
                    <span>{{ formatDuration(currentDialogue.end_time - currentDialogue.start_time) }}</span>
                  </el-form-item>
                </el-form>
                
                <div class="action-buttons">
                  <el-button
                    type="primary"
                    :icon="VideoPlay"
                    :loading="generateLoading"
                    @click="handleGenerateDialogue(currentDialogue)"
                  >
                    生成音频
                  </el-button>
                  <el-button
                    v-if="currentDialogue.audio_path"
                    :icon="VideoPlay"
                    @click="handlePlayDialogue(currentDialogue)"
                  >
                    播放试听
                  </el-button>
                </div>
              </div>
              
              <el-empty v-else description="请选择一个对话段落" />
            </el-tab-pane>
            
            <!-- 角色管理 -->
            <el-tab-pane label="角色管理" name="characters">
              <div class="characters-list">
                <CharacterCard
                  v-for="character in characterStore.characters"
                  :key="character.id"
                  :character="character"
                  :compact="true"
                  @config="handleConfigCharacterVoice"
                  @edit="handleEditCharacter"
                  @delete="handleDeleteCharacter"
                />
                
                <el-button
                  type="primary"
                  style="width: 100%; margin-top: 16px"
                  @click="showAddCharacterDialog = true"
                >
                  添加角色
                </el-button>
              </div>
            </el-tab-pane>
            
            <!-- 章节信息 -->
            <el-tab-pane label="章节信息" name="chapter">
              <div v-if="currentChapter" class="chapter-info">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="章节标题">
                    {{ currentChapter.title }}
                  </el-descriptions-item>
                  <el-descriptions-item label="序号">
                    {{ currentChapter.order_index }}
                  </el-descriptions-item>
                  <el-descriptions-item label="字数">
                    {{ currentChapter.word_count?.toLocaleString() }}
                  </el-descriptions-item>
                  <el-descriptions-item label="对话数量">
                    {{ dialogueStore.dialogues.length }}
                  </el-descriptions-item>
                  <el-descriptions-item label="已生成">
                    {{ generatedCount }} / {{ dialogueStore.dialogues.length }}
                  </el-descriptions-item>
                  <el-descriptions-item label="总时长">
                    {{ formatDuration(currentChapter.duration) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="状态">
                    <el-tag :type="getStatusType(currentChapter.status)">
                      {{ getStatusText(currentChapter.status) }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
                
                <el-button
                  type="primary"
                  style="width: 100%; margin-top: 16px"
                  @click="handleViewChapterText"
                >
                  查看原文
                </el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
    
    <!-- 添加角色对话框 -->
    <el-dialog
      v-model="showAddCharacterDialog"
      title="添加角色"
      width="500px"
    >
      <el-form :model="characterForm" label-width="80px">
        <el-form-item label="角色名称" required>
          <el-input v-model="characterForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input
            v-model="characterForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddCharacterDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddCharacter">添加</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看原文对话框 -->
    <el-dialog
      v-model="showChapterTextDialog"
      title="章节原文"
      width="800px"
    >
      <div class="chapter-text">
        {{ currentChapter?.content }}
      </div>
    </el-dialog>
    
    <!-- 音频播放器 -->
    <AudioPlayer
      v-if="currentAudio"
      :src="currentAudio.src"
      :visible="showAudioPlayer"
      @close="showAudioPlayer = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Edit, Plus, Delete, Refresh, Download, VideoPlay
} from '@element-plus/icons-vue'
import { useChapterStore } from '@/stores/chapter'
import { useCharacterStore } from '@/stores/character'
import { useDialogueStore } from '@/stores/dialogue'
import DialogueEditBlock from '@/components/DialogueEditBlock.vue'
import CharacterCard from '@/components/CharacterCard.vue'
import AudioPlayer from '@/components/AudioPlayer.vue'
import type { Chapter, Character, Dialogue } from '@/types'

const router = useRouter()
const route = useRoute()
const projectId = computed(() => Number(route.params.id))

const chapterStore = useChapterStore()
const characterStore = useCharacterStore()
const dialogueStore = useDialogueStore()

// 状态
const selectedChapterId = ref<number>()
const selectedDialogueId = ref<number>()
const activeTab = ref('dialogue')
const generateLoading = ref(false)

// 对话框
const showAddCharacterDialog = ref(false)
const showChapterTextDialog = ref(false)
const showAudioPlayer = ref(false)

// 表单
const characterForm = ref({
  name: '',
  description: '',
})

// 对话属性
const dialogueSpeed = ref(1.0)
const dialogueVolume = ref(100)
const dialoguePause = ref(0)

// 当前数据
const currentChapter = computed(() => 
  chapterStore.chapters.find(c => c.id === selectedChapterId.value)
)

const currentDialogue = computed(() => 
  dialogueStore.dialogues.find(d => d.id === selectedDialogueId.value)
)

const currentAudio = ref<{ src: string } | null>(null)

// 已生成音频数量
const generatedCount = computed(() => 
  dialogueStore.dialogues.filter(d => d.status === 'completed').length
)

// 监听章节变化
watch(selectedChapterId, async (newId) => {
  if (newId) {
    await dialogueStore.fetchDialogues(newId)
    selectedDialogueId.value = undefined
  }
})

// 监听对话选择
watch(currentDialogue, (newDialogue) => {
  if (newDialogue) {
    dialogueSpeed.value = newDialogue.voice_config?.speed || 1.0
    dialogueVolume.value = newDialogue.voice_config?.volume || 100
    dialoguePause.value = newDialogue.pause_after || 0
  }
})

// 从URL参数加载章节
onMounted(async () => {
  await Promise.all([
    chapterStore.fetchChapters(projectId.value),
    characterStore.fetchCharacters(projectId.value),
  ])
  
  const chapterId = route.query.chapter
  if (chapterId) {
    selectedChapterId.value = Number(chapterId)
  } else if (chapterStore.chapters.length > 0) {
    selectedChapterId.value = chapterStore.chapters[0].id
  }
})

// 章节切换
const handleChapterChange = async (chapterId: number) => {
  await router.push({ 
    path: route.path, 
    query: { ...route.query, chapter: chapterId } 
  })
}

// 解析章节
const handleParseChapter = async () => {
  if (!selectedChapterId.value) {
    ElMessage.warning('请先选择章节')
    return
  }
  
  try {
    await dialogueStore.parseChapter(selectedChapterId.value)
    ElMessage.success('章节解析成功')
    await dialogueStore.fetchDialogues(selectedChapterId.value)
  } catch (error) {
    ElMessage.error('解析失败，请重试')
  }
}

// 添加对话
const handleAddDialogue = () => {
  if (!selectedChapterId.value) {
    ElMessage.warning('请先选择章节')
    return
  }
  ElMessage.info('添加对话功能开发中')
}

// 批量删除
const handleBatchDelete = () => {
  ElMessage.info('批量删除功能开发中')
}

// 刷新
const handleRefresh = async () => {
  if (selectedChapterId.value) {
    await dialogueStore.fetchDialogues(selectedChapterId.value)
    ElMessage.success('刷新成功')
  }
}

// 导出对话
const handleExportDialogues = () => {
  ElMessage.info('导出功能开发中')
}

// 生成全部音频
const handleGenerateAll = async () => {
  if (!selectedChapterId.value) {
    ElMessage.warning('请先选择章节')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要生成该章节的全部 ${dialogueStore.dialogues.length} 段音频吗？`,
      '批量生成',
      {
        confirmButtonText: '生成',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    ElMessage.info('批量生成功能开发中')
  } catch (error) {
    // 取消操作
  }
}

// 选择对话
const handleSelectDialogue = (dialogue: Dialogue) => {
  selectedDialogueId.value = dialogue.id
}

// 更新对话
const handleUpdateDialogue = async (dialogue: Dialogue) => {
  try {
    await dialogueStore.updateDialogue(dialogue.id, dialogue)
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// 删除对话
const handleDeleteDialogue = async (dialogue: Dialogue) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该对话段落吗？',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await dialogueStore.deleteDialogue(dialogue.id)
    ElMessage.success('删除成功')
    
    if (selectedDialogueId.value === dialogue.id) {
      selectedDialogueId.value = undefined
    }
  } catch (error) {
    // 取消操作
  }
}

// 生成对话音频
const handleGenerateDialogue = async (dialogue: Dialogue) => {
  generateLoading.value = true
  try {
    // TODO: 调用音频生成API
    ElMessage.info('音频生成功能开发中')
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    generateLoading.value = false
  }
}

// 播放对话
const handlePlayDialogue = (dialogue: Dialogue) => {
  if (dialogue.audio_path) {
    currentAudio.value = { src: dialogue.audio_path }
    showAudioPlayer.value = true
  } else {
    ElMessage.warning('该对话还未生成音频')
  }
}

// 移动对话
const handleMoveUp = async (dialogue: Dialogue) => {
  ElMessage.info('移动功能开发中')
}

const handleMoveDown = async (dialogue: Dialogue) => {
  ElMessage.info('移动功能开发中')
}

// 属性变更
const handlePropertyChange = async () => {
  if (currentDialogue.value) {
    await handleUpdateDialogue(currentDialogue.value)
  }
}

const handleSpeedChange = (value: number) => {
  if (currentDialogue.value) {
    if (!currentDialogue.value.voice_config) {
      currentDialogue.value.voice_config = {}
    }
    currentDialogue.value.voice_config.speed = value
    handlePropertyChange()
  }
}

const handleVolumeChange = (value: number) => {
  if (currentDialogue.value) {
    if (!currentDialogue.value.voice_config) {
      currentDialogue.value.voice_config = {}
    }
    currentDialogue.value.voice_config.volume = value
    handlePropertyChange()
  }
}

const handlePauseChange = (value: number) => {
  if (currentDialogue.value) {
    currentDialogue.value.pause_after = value
    handlePropertyChange()
  }
}

// 角色管理
const handleAddCharacter = async () => {
  if (!characterForm.value.name) {
    ElMessage.warning('请输入角色名称')
    return
  }
  
  try {
    await characterStore.createCharacter({
      project_id: projectId.value,
      ...characterForm.value,
    })
    ElMessage.success('角色添加成功')
    showAddCharacterDialog.value = false
    characterForm.value = { name: '', description: '' }
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const handleConfigCharacterVoice = (character: Character) => {
  router.push(`/projects/${projectId.value}/voice-config`)
}

const handleEditCharacter = (character: Character) => {
  ElMessage.info('编辑角色功能开发中')
}

const handleDeleteCharacter = async (character: Character) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色"${character.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await characterStore.deleteCharacter(character.id)
    ElMessage.success('删除成功')
  } catch (error) {
    // 取消操作
  }
}

// 查看原文
const handleViewChapterText = () => {
  showChapterTextDialog.value = true
}

// 工具函数
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    draft: '',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status] || ''
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

const getAudioStatusType = (status?: string) => {
  const types: Record<string, any> = {
    pending: '',
    generating: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status || 'pending'] || ''
}

const getAudioStatusText = (status?: string) => {
  const texts: Record<string, string> = {
    pending: '未生成',
    generating: '生成中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status || 'pending'] || '未知'
}

const formatDuration = (seconds?: number) => {
  if (!seconds) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}
</script>

<style scoped>
.dialogue-editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.left-section,
.right-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.editor-content {
  flex: 1;
  display: flex;
  gap: 24px;
  padding: 24px;
  overflow: hidden;
}

.dialogue-list {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 20px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.dialogue-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.properties-panel {
  width: 400px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.property-form {
  padding: 20px;
}

.char-count {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.action-buttons .el-button {
  flex: 1;
}

.character-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.char-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.characters-list {
  padding: 20px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.chapter-info {
  padding: 20px;
}

.chapter-text {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 14px;
  color: #303133;
}

/* 滚动条样式 */
.dialogue-list::-webkit-scrollbar,
.characters-list::-webkit-scrollbar,
.chapter-text::-webkit-scrollbar {
  width: 6px;
}

.dialogue-list::-webkit-scrollbar-thumb,
.characters-list::-webkit-scrollbar-thumb,
.chapter-text::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.dialogue-list::-webkit-scrollbar-thumb:hover,
.characters-list::-webkit-scrollbar-thumb:hover,
.chapter-text::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}
</style>

