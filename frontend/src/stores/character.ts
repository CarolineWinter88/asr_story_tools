import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Character, UpdateCharacterDTO } from '@/types'
import * as characterApi from '@/api/character'

export const useCharacterStore = defineStore('character', () => {
  // 状态
  const characters = ref<Character[]>([])
  const currentCharacter = ref<Character | null>(null)
  const loading = ref(false)

  // 计算属性
  const hasCharacters = computed(() => characters.value.length > 0)
  const characterMap = computed(() => {
    const map = new Map<number, Character>()
    characters.value.forEach((char) => map.set(char.id, char))
    return map
  })

  // 获取角色列表
  const fetchCharacters = async (projectId: number) => {
    loading.value = true
    try {
      const list = await characterApi.getCharacters(projectId)
      characters.value = list
      return list
    } finally {
      loading.value = false
    }
  }

  // 获取角色详情
  const fetchCharacter = async (id: number) => {
    loading.value = true
    try {
      const character = await characterApi.getCharacter(id)
      currentCharacter.value = character
      return character
    } finally {
      loading.value = false
    }
  }

  // 提取角色
  const extractCharacters = async (projectId: number) => {
    loading.value = true
    try {
      const result = await characterApi.extractCharacters(projectId)
      characters.value = result.characters
      return result.characters
    } finally {
      loading.value = false
    }
  }

  // 更新角色
  const updateCharacter = async (id: number, data: UpdateCharacterDTO) => {
    loading.value = true
    try {
      const character = await characterApi.updateCharacter(id, data)
      const index = characters.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        characters.value[index] = character
      }
      if (currentCharacter.value?.id === id) {
        currentCharacter.value = character
      }
      return character
    } finally {
      loading.value = false
    }
  }

  // 删除角色
  const deleteCharacter = async (id: number) => {
    loading.value = true
    try {
      await characterApi.deleteCharacter(id)
      characters.value = characters.value.filter((c) => c.id !== id)
      if (currentCharacter.value?.id === id) {
        currentCharacter.value = null
      }
    } finally {
      loading.value = false
    }
  }

  // 根据ID获取角色
  const getCharacterById = (id: number) => {
    return characterMap.value.get(id)
  }

  // 设置当前角色
  const setCurrentCharacter = (character: Character | null) => {
    currentCharacter.value = character
  }

  // 重置状态
  const reset = () => {
    characters.value = []
    currentCharacter.value = null
    loading.value = false
  }

  return {
    characters,
    currentCharacter,
    loading,
    hasCharacters,
    characterMap,
    fetchCharacters,
    fetchCharacter,
    extractCharacters,
    updateCharacter,
    deleteCharacter,
    getCharacterById,
    setCurrentCharacter,
    reset,
  }
})

