import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/projects',
  },
  {
    path: '/projects',
    name: 'ProjectList',
    component: () => import('@/views/ProjectList.vue'),
    meta: { title: '我的项目' },
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/ProjectDetail.vue'),
    meta: { title: '项目详情' },
  },
  {
    path: '/projects/:id/import',
    name: 'TextImport',
    component: () => import('@/views/TextImport.vue'),
    meta: { title: '文本导入' },
  },
  {
    path: '/projects/:id/voice-config',
    name: 'VoiceConfig',
    component: () => import('@/views/VoiceConfig.vue'),
    meta: { title: '智能配音' },
  },
  {
    path: '/projects/:id/characters',
    name: 'CharacterManager',
    component: () => import('@/views/CharacterManager.vue'),
    meta: { title: '角色管理' },
  },
  {
    path: '/projects/:id/editor',
    name: 'DialogueEditor',
    component: () => import('@/views/DialogueEditor.vue'),
    meta: { title: '对话编辑器' },
  },
  {
    path: '/projects/:id/audio-preview/:chapterId',
    name: 'AudioPreview',
    component: () => import('@/views/AudioPreview.vue'),
    meta: { title: '音频预览' },
  },
  {
    path: '/projects/:id/export',
    name: 'ExportPage',
    component: () => import('@/views/ExportPage.vue'),
    meta: { title: '导出音频' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsPage.vue'),
    meta: { title: '设置' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI有声书工具`
  }
  next()
})

export default router

