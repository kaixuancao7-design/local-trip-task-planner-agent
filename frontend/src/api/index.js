import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 生成计划
export const generatePlan = async (data) => {
  try {
    const response = await api.post('/v1/plan/generate', data)
    return response.data
  } catch (error) {
    console.error('生成计划失败:', error)
    throw error
  }
}

// 确认并执行计划
export const confirmPlan = async (data) => {
  try {
    const response = await api.post('/v1/plan/execute', data)
    return response.data
  } catch (error) {
    console.error('确认计划失败:', error)
    throw error
  }
}

// 获取用户偏好
export const getUserPreferences = async (userId) => {
  try {
    const response = await api.get(`/v1/preferences/${userId}`)
    return response.data
  } catch (error) {
    console.error('获取用户偏好失败:', error)
    throw error
  }
}

// 获取天气信息
export const getWeather = async (city) => {
  try {
    const response = await api.get('/v1/tools/weather', {
      params: { city }
    })
    return response.data
  } catch (error) {
    console.error('获取天气失败:', error)
    throw error
  }
}

// 地理编码（地址转经纬度）
export const geocode = async (address) => {
  try {
    const response = await api.get('/v1/geocode', {
      params: { address }
    })
    return response.data
  } catch (error) {
    console.error('地理编码失败:', error)
    throw error
  }
}

// 获取路线信息
export const getRoute = async (origin, destination) => {
  try {
    const response = await api.get('/v1/tools/route', {
      params: { origin, destination }
    })
    return response.data
  } catch (error) {
    console.error('获取路线失败:', error)
    throw error
  }
}

// 获取用户位置（通过后端代理，保护隐私）
export const getUserLocation = async () => {
  try {
    const response = await api.get('/v1/tools/location')
    return response.data
  } catch (error) {
    console.error('获取位置失败:', error)
    throw error
  }
}

// 获取地图配置（通过后端获取，保护API key）
export const getMapConfig = async () => {
  try {
    const response = await api.get('/v1/tools/map/config')
    return response.data
  } catch (error) {
    console.error('获取地图配置失败:', error)
    throw error
  }
}