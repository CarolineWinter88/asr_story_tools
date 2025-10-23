<template>
  <div class="voice-config-page">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="router.back()">返回</el-button>
      <h1>智能配音</h1>
    </div>
    
    <div class="config-container">
      <div class="left-panel">
        <ChapterList
          :chapters="chapterStore.chapters"
          :selected-id="selectedChapterId"
          @select="handleSelectChapter"
          @add="handleAddChapter"
          @edit="handleEditChapter"
          @parse="handleParseChapter"
          @generate="handleGenerateChapter"
          @delete="handleDeleteChapter"
        />
      </div>
      
      <div class="main-panel">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="角色管理" name="characters">
            <div v-loading="characterStore.loading" class="characters-grid">
              <CharacterCard
                v-for="character in characterStore.characters"
                :key="character.id"
                :character="character"
                @config="handleConfigVoice"
                @test="handleTestVoice"
                @delete="handleDeleteCharacter"
              />
              
              <el-empty v-if="!characterStore.hasCharacters" description="暂无角色，请先解析章节文本" />
            </div>
            
            <div class="actions-bar">
              <el-button type="primary" @click="handleExtractCharacters">
                自动提取角色
              </el-button>
              <el-button @click="showAddCharacterDialog = true">
                手动添加角色
              </el-button>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="对话预览" name="dialogues">
            <div v-if="selectedChapterId" class="dialogues-container">
              <div v-loading="dialogueStore.loading" class="dialogue-list">
                <DialogueBlock
                  v-for="dialogue in dialogueStore.dialogues"
                  :key="dialogue.id"
                  :dialogue="dialogue"
                  :characters="characterStore.characters"
                  @update="handleUpdateDialogue"
                  @delete="handleDeleteDialogue"
                  @play="handlePlayDialogue"
                />
                
                <el-empty v-if="!dialogueStore.hasDialogues" description="暂无对话，请先解析章节" />
              </div>
            </div>
            <el-empty v-else description="请先选择章节" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
    
    <!-- 声音配置对话框 -->
    <el-dialog
      v-model="showVoiceConfigDialog"
      title="配置声音"
      width="600px"
    >
      <el-form v-if="currentCharacter" :model="voiceForm" label-width="100px">
        <el-form-item label="角色名称">
          <el-input v-model="currentCharacter.name" disabled />
        </el-form-item>
        
        <el-form-item label="TTS引擎">
          <el-select v-model="voiceForm.engine" placeholder="请选择TTS引擎">
            <el-option label="Azure TTS" value="azure" />
            <el-option label="阿里云TTS" value="aliyun" />
            <el-option label="腾讯云TTS" value="tencent" />
            <el-option label="本地TTS" value="local" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="音色">
          <el-select v-model="voiceForm.voice_id" placeholder="请选择音色">
            <el-option
              v-for="voice in availableVoices"
              :key="voice.id"
              :label="voice.name"
              :value="voice.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="语速">
          <el-slider v-model="voiceForm.speed" :min="0.5" :max="2" :step="0.1" show-input />
        </el-form-item>
        
        <el-form-item label="音调">
          <el-slider v-model="voiceForm.pitch" :min="-12" :max="12" :step="1" show-input />
        </el-form-item>
        
        <el-form-item label="音量">
          <el-slider v-model="voiceForm.volume" :min="0" :max="100" show-input />
        </el-form-item>
        
        <el-form-item label="试听文本">
          <el-input
            v-model="testText"
            type="textarea"
            :rows="3"
            placeholder="输入文本进行试听"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showVoiceConfigDialog = false">取消</el-button>
        <el-button @click="handleTestCurrentVoice">试听</el-button>
        <el-button type="primary" @click="handleSaveVoiceConfig">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加角色对话框 -->
    <el-dialog
      v-model="showAddCharacterDialog"
      title="添加角色"
      width="400px"
    >
      <el-form :model="characterForm" label-width="80px">
        <el-form-item label="角色名称">
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useChapterStore } from '@/stores/chapter'
import { useCharacterStore } from '@/stores/character'
import { useDialogueStore } from '@/stores/dialogue'
import ChapterList from '@/components/ChapterList.vue'
import CharacterCard from '@/components/CharacterCard.vue'
import DialogueBlock from '@/components/DialogueBlock.vue'
import type { Chapter, Character, Dialogue } from '@/types'

const router = useRouter()
const route = useRoute()
const projectId = computed(() => Number(route.params.id))

const chapterStore = useChapterStore()
const characterStore = useCharacterStore()
const dialogueStore = useDialogueStore()

// 标签页
const activeTab = ref('characters')
const selectedChapterId = ref<number>()

// 声音配置
const showVoiceConfigDialog = ref(false)
const currentCharacter = ref<Character>()
const voiceForm = ref({
  engine: 'azure',
  voice_id: '',
  speed: 1.0,
  pitch: 0,
  volume: 100,
})
const testText = ref('这是一段测试文本，用于试听声音效果。')

// 可用音色列表（示例数据）
const availableVoices = ref([
  { id: 'zh-CN-XiaoxiaoNeural', name: '晓晓（女）' },
  { id: 'zh-CN-YunxiNeural', name: '云希（男）' },
  { id: 'zh-CN-YunyangNeural', name: '云扬（男）' },
  { id: 'zh-CN-XiaoyiNeural', name: '晓伊（女）' },
])

// 添加角色
const showAddCharacterDialog = ref(false)
const characterForm = ref({
  name: '',
  description: '',
})

// 选择章节
const handleSelectChapter = (chapter: Chapter) => {
  selectedChapterId.value = chapter.id
  dialogueStore.fetchDialogues(chapter.id)
}

// 添加章节
const handleAddChapter = () => {
  ElMessage.info('功能开发中')
}

// 编辑章节
const handleEditChapter = (chapter: Chapter) => {
  ElMessage.info('功能开发中')
}

// 解析章节
const handleParseChapter = async (chapter: Chapter) => {
  try {
    await dialogueStore.parseChapter(chapter.id)
    ElMessage.success('章节解析成功')
    if (selectedChapterId.value === chapter.id) {
      dialogueStore.fetchDialogues(chapter.id)
    }
  } catch (error) {
    ElMessage.error('解析失败，请重试')
  }
}

// 生成音频
const handleGenerateChapter = async (chapter: Chapter) => {
  ElMessage.info('功能开发中')
}

// 删除章节
const handleDeleteChapter = async (chapter: Chapter) => {
  await chapterStore.deleteChapter(chapter.id)
}

// 提取角色
const handleExtractCharacters = async () => {
  try {
    await characterStore.extractCharacters(projectId.value)
    ElMessage.success('角色提取成功')
  } catch (error) {
    ElMessage.error('提取失败，请重试')
  }
}

// 添加角色
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
    ElMessage.error('添加失败，请重试')
  }
}

// 配置声音
const handleConfigVoice = (character: Character) => {
  currentCharacter.value = character
  if (character.voice_config) {
    voiceForm.value = { ...character.voice_config }
  }
  showVoiceConfigDialog.value = true
}

// 保存声音配置
const handleSaveVoiceConfig = async () => {
  if (!currentCharacter.value) return
  
  try {
    await characterStore.updateCharacter(currentCharacter.value.id, {
      voice_config: voiceForm.value,
    })
    ElMessage.success('声音配置已保存')
    showVoiceConfigDialog.value = false
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  }
}

// 试听声音
const handleTestVoice = (character: Character) => {
  ElMessage.info('试听功能开发中')
}

// 试听当前配置
const handleTestCurrentVoice = () => {
  ElMessage.info('试听功能开发中')
}

// 删除角色
const handleDeleteCharacter = async (character: Character) => {
  await characterStore.deleteCharacter(character.id)
}

// 更新对话
const handleUpdateDialogue = async (dialogue: Dialogue) => {
  await dialogueStore.updateDialogue(dialogue.id, dialogue)
}

// 删除对话
const handleDeleteDialogue = async (dialogue: Dialogue) => {
  await dialogueStore.deleteDialogue(dialogue.id)
}

// 播放对话
const handlePlayDialogue = (dialogue: Dialogue) => {
  ElMessage.info('播放功能开发中')
}

onMounted(() => {
  chapterStore.fetchChapters(projectId.value)
  characterStore.fetchCharacters(projectId.value)
})
</script>

<style scoped>
.voice-config-page {
  min-height: 100vh;
  padding: 24px;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.config-container {
  display: flex;
  gap: 24px;
  height: calc(100vh - 120px);
}

.left-panel {
  width: 320px;
  flex-shrink: 0;
}

.main-panel {
  flex: 1;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
  min-height: 400px;
}

.actions-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid #ebeef5;
}

.dialogues-container {
  padding: 20px;
}

.dialogue-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>

