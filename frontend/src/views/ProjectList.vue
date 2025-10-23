<template>
  <div class="project-list-page">
    <div class="page-header">
      <div class="header-title">
        <h1>我的项目</h1>
        <p>管理你的AI有声书项目</p>
      </div>
      <el-button type="primary" size="large" :icon="Plus" @click="showCreateDialog = true">
        创建项目
      </el-button>
    </div>
    
    <div class="page-toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索项目名称..."
        :prefix-icon="Search"
        clearable
        style="width: 300px"
        @input="handleSearch"
      />
      
      <el-radio-group v-model="statusFilter" @change="fetchData">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="draft">草稿</el-radio-button>
        <el-radio-button label="processing">处理中</el-radio-button>
        <el-radio-button label="completed">已完成</el-radio-button>
      </el-radio-group>
    </div>
    
    <div v-loading="projectStore.loading" class="projects-grid">
      <ProjectCard
        v-for="project in projectStore.projects"
        :key="project.id"
        :project="project"
        @click="handleProjectClick"
        @edit="handleEdit"
        @export="handleExport"
        @duplicate="handleDuplicate"
        @delete="handleDelete"
      />
      
      <el-empty v-if="!projectStore.loading && !projectStore.hasProjects" description="暂无项目，点击上方按钮创建第一个项目" />
    </div>
    
    <div v-if="projectStore.total > pageSize" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="projectStore.total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </div>
    
    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新项目"
      width="500px"
      @closed="resetForm"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import ProjectCard from '@/components/ProjectCard.vue'
import type { Project } from '@/types'

const router = useRouter()
const projectStore = useProjectStore()

// 搜索和过滤
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(12)

// 创建对话框
const showCreateDialog = ref(false)
const creating = ref(false)
const formRef = ref<FormInstance>()
const formData = ref({
  name: '',
  description: '',
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
  ],
}

// 获取项目列表
const fetchData = async () => {
  await projectStore.fetchProjects({
    page: currentPage.value,
    page_size: pageSize.value,
    search: searchKeyword.value || undefined,
  })
}

// 搜索
let searchTimeout: number
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchData()
  }, 500)
}

// 创建项目
const handleCreate = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      creating.value = true
      try {
        const project = await projectStore.createProject(formData.value)
        ElMessage.success('项目创建成功')
        showCreateDialog.value = false
        // 跳转到文本导入页
        router.push(`/projects/${project.id}/import`)
      } catch (error) {
        ElMessage.error('创建失败，请重试')
      } finally {
        creating.value = false
      }
    }
  })
}

// 点击项目卡片
const handleProjectClick = (project: Project) => {
  router.push(`/projects/${project.id}`)
}

// 编辑项目
const handleEdit = (project: Project) => {
  formData.value = {
    name: project.name,
    description: project.description || '',
  }
  // TODO: 实现编辑功能
  ElMessage.info('编辑功能开发中')
}

// 导出项目
const handleExport = (project: Project) => {
  router.push(`/projects/${project.id}/export`)
}

// 复制项目
const handleDuplicate = (project: Project) => {
  ElMessage.info('复制功能开发中')
}

// 删除项目
const handleDelete = async (project: Project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await projectStore.deleteProject(project.id)
    ElMessage.success('删除成功')
  } catch (error) {
    // 取消操作
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
  }
  formRef.value?.clearValidate()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.project-list-page {
  min-height: 100vh;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.header-title p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.page-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  min-height: 400px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
}
</style>

