import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 生成计划
export const generatePlan = async (data) => {
  try {
    const response = await api.post('/plan', data)
    return response.data
  } catch (error) {
    console.error('生成计划失败:', error)
    throw error
  }
}

// 确认并执行计划
export const confirmPlan = async (data) => {
  try {
    const response = await api.post('/confirm', data)
    return response.data
  } catch (error) {
    console.error('确认计划失败:', error)
    throw error
  }
}

// 获取用户偏好
export const getUserPreferences = async (userId) => {
  try {
    const response = await api.get(`/preferences/${userId}`)
    return response.data
  } catch (error) {
    console.error('获取用户偏好失败:', error)
    throw error
  }
}