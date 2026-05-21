import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// WebSocket连接管理
let ws = null
let wsCallbacks = {}

// 初始化WebSocket连接
export const initWebSocket = (onThinking, onComplete, onError) => {
  // 保存回调函数
  wsCallbacks = { onThinking, onComplete, onError }
  
  // 关闭现有连接
  if (ws) {
    ws.close()
  }
  
  // 建立新连接
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/api/v1/plan/ws`
  
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket连接已建立')
  }
  
  ws.onmessage = (event) => {
    console.log('WebSocket收到原始消息:', event.data)
    try {
      const data = JSON.parse(event.data)
      console.log('WebSocket解析后数据:', data)
      
      switch (data.type) {
        case 'thinking':
          console.log('调用thinking回调')
          wsCallbacks.onThinking?.(data)
          break
        case 'complete':
          console.log('调用complete回调')
          wsCallbacks.onComplete?.(data)
          break
        case 'error':
          console.log('调用error回调')
          wsCallbacks.onError?.(data)
          break
        case 'cancelled':
          console.log('任务已取消')
          break
        default:
          console.warn('未知消息类型:', data.type)
      }
    } catch (error) {
      console.error('解析WebSocket消息失败:', error, '原始数据:', event.data)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket错误:', error)
    wsCallbacks.onError?.({ message: '连接错误' })
  }
  
  ws.onclose = (event) => {
    console.log('WebSocket连接关闭:', event.code, event.reason)
    // 自动重连
    setTimeout(() => initWebSocket(wsCallbacks.onThinking, wsCallbacks.onComplete, wsCallbacks.onError), 3000)
  }
}

// 通过WebSocket发送生成计划请求
export const sendGeneratePlan = (user_id, input) => {
  return new Promise((resolve, reject) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        action: 'generate_plan',
        user_id,
        input
      }))
      resolve()
    } else {
      reject(new Error('WebSocket未连接'))
    }
  })
}

// 取消任务
export const cancelPlan = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'cancel' }))
  }
}

// 关闭WebSocket连接
export const closeWebSocket = () => {
  if (ws) {
    ws.close()
    ws = null
  }
}

// 生成计划（HTTP方式，作为备用）
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