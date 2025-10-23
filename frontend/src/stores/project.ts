import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Project, CreateProjectDTO, PaginationParams } from '@/types'
import * as projectApi from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const total = ref(0)
  const loading = ref(false)

  // 计算属性
  const hasProjects = computed(() => projects.value.length > 0)
  const currentProjectId = computed(() => currentProject.value?.id)

  // 获取项目列表
  const fetchProjects = async (params?: PaginationParams) => {
    loading.value = true
    try {
      const response = await projectApi.getProjects(params)
      projects.value = response.items
      total.value = response.total
      return response
    } finally {
      loading.value = false
    }
  }

  // 获取项目详情
  const fetchProject = async (id: number) => {
    loading.value = true
    try {
      const project = await projectApi.getProject(id)
      currentProject.value = project
      return project
    } finally {
      loading.value = false
    }
  }

  // 创建项目
  const createProject = async (data: CreateProjectDTO) => {
    loading.value = true
    try {
      const project = await projectApi.createProject(data)
      projects.value.unshift(project)
      total.value += 1
      return project
    } finally {
      loading.value = false
    }
  }

  // 更新项目
  const updateProject = async (id: number, data: Partial<CreateProjectDTO>) => {
    loading.value = true
    try {
      const project = await projectApi.updateProject(id, data)
      const index = projects.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        projects.value[index] = project
      }
      if (currentProject.value?.id === id) {
        currentProject.value = project
      }
      return project
    } finally {
      loading.value = false
    }
  }

  // 删除项目
  const deleteProject = async (id: number) => {
    loading.value = true
    try {
      await projectApi.deleteProject(id)
      projects.value = projects.value.filter((p) => p.id !== id)
      total.value -= 1
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
    } finally {
      loading.value = false
    }
  }

  // 设置当前项目
  const setCurrentProject = (project: Project | null) => {
    currentProject.value = project
  }

  // 重置状态
  const reset = () => {
    projects.value = []
    currentProject.value = null
    total.value = 0
    loading.value = false
  }

  return {
    projects,
    currentProject,
    total,
    loading,
    hasProjects,
    currentProjectId,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
    setCurrentProject,
    reset,
  }
})

