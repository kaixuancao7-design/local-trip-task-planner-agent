<template>
  <div class="app-container">
    <el-header>
      <h1>Local Activity Agent</h1>
      <div class="header-weather" v-if="currentWeather">
        <el-badge :value="currentWeather.temperature + '°C'" class="badge" />
        <span>{{ currentWeather.description }}</span>
      </div>
    </el-header>
    <el-main>
      <!-- 双栏布局 -->
      <div class="main-content">
        <!-- 左侧：地图与行程可视化区域 (60%) -->
        <div class="left-panel">
          <div class="map-container">
            <div id="map" class="map"></div>
            <div class="map-controls">
              <el-button size="small" @click="centerMap" type="primary">定位</el-button>
              <el-button size="small" @click="zoomIn">放大</el-button>
              <el-button size="small" @click="zoomOut">缩小</el-button>
            </div>
            <div class="location-info" v-if="currentLocation">
              <i class="el-icon-map-marker"></i>
              <span>{{ currentLocation.address }}</span>
            </div>
          </div>
          
          <!-- 当前天气卡片 -->
          <div v-if="currentWeather" class="weather-card">
            <el-card>
              <template #header>
                <span>当前天气</span>
              </template>
              <div class="weather-content">
                <div class="weather-icon">{{ getWeatherIcon(currentWeather.description) }}</div>
                <div class="weather-info">
                  <h3>{{ currentWeather.city }}</h3>
                  <p class="weather-temp">{{ currentWeather.temperature }}°C</p>
                  <p class="weather-desc">{{ currentWeather.description }}</p>
                  <div class="weather-details">
                    <span>湿度: {{ currentWeather.humidity }}%</span>
                    <span>风速: {{ currentWeather.wind_speed }} m/s</span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          
          <div v-if="plan" class="route-info">
            <h4>路线信息</h4>
            <el-divider></el-divider>
            <el-timeline>
              <el-timeline-item
                v-for="(item, index) in plan.schedule"
                :key="index"
                :timestamp="item.time"
              >
                {{ item.activity }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>
        
        <!-- 右侧：对话与行程管理区域 (40%) -->
        <div class="right-panel">
          <!-- 用户输入区域 -->
          <div class="input-section">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>用户输入</span>
                </div>
              </template>
              <el-form :model="userInput" label-width="80px">
                <el-form-item label="用户ID">
                  <el-input v-model="userInput.user_id" placeholder="请输入用户ID"></el-input>
                </el-form-item>
                <el-form-item label="活动需求">
                  <el-input
                    v-model="userInput.input"
                    type="textarea"
                    :rows="4"
                    placeholder="例如：这周末想带老婆去南京紫金山爬山，中午吃顿好的，不要太辣。"
                  ></el-input>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="generatePlan" :loading="loading">
                    {{ loading ? '生成中...' : '生成计划' }}
                  </el-button>
                  <el-button v-if="plan" type="warning" @click="regeneratePlan" style="margin-left: 10px">
                    重新规划
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </div>
          
          <!-- Agent思考过程 -->
          <div v-if="thinking" class="thinking-section">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>Agent思考过程</span>
                </div>
              </template>
              <div class="thinking-content">
                <p v-for="(thought, index) in thinkingSteps" :key="index" class="thinking-step">
                  {{ thought }}
                </p>
                <p v-if="isStreaming" class="thinking-step streaming">
                  {{ currentStreamText }}
                  <span class="typing-indicator">|</span>
                </p>
              </div>
            </el-card>
          </div>
          
          <!-- 行程卡片展示 -->
          <div v-if="plan" class="plan-section">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>活动计划</span>
                  <el-button type="success" @click="confirmPlan" style="margin-left: 10px">
                    确认执行
                  </el-button>
                </div>
              </template>
              <div class="plan-content">
                <h3>{{ plan.title }}</h3>
                <el-divider></el-divider>
                
                <!-- 行程卡片 -->
                <div class="activity-cards">
                  <div 
                    v-for="(activity, index) in plan.activities" 
                    :key="index"
                    :class="['activity-card', { flipped: flippedCards[index] }]"
                    @click="flipCard(index)"
                  >
                    <div class="card-front">
                      <div class="card-icon">
                        <i class="el-icon-location"></i>
                      </div>
                      <h4>{{ activity.name }}</h4>
                      <p class="card-time">{{ getActivityTime(activity) }}</p>
                      <p class="card-location">{{ activity.location }}</p>
                      <p v-if="activity.travel_time" class="card-travel">{{ activity.travel_time }}</p>
                    </div>
                    <div class="card-back">
                      <h4>详细信息</h4>
                      <p>{{ activity.description || '暂无详细描述' }}</p>
                      <p class="card-notes">注意事项：{{ activity.notes || '无' }}</p>
                    </div>
                  </div>
                </div>
                
                <el-divider></el-divider>
                <h4>餐饮推荐</h4>
                <el-list>
                  <el-list-item v-for="(restaurant, index) in plan.restaurants" :key="index">
                    <template #default>
                      <div>
                        <span class="restaurant-name">{{ restaurant.name }}</span>
                        <span class="restaurant-address">{{ restaurant.address }}</span>
                      </div>
                    </template>
                  </el-list-item>
                </el-list>
                
                <el-divider></el-divider>
                <h4>交通建议</h4>
                <p>{{ plan.transportation }}</p>
                
                <el-divider></el-divider>
                <h4>预估费用</h4>
                <p>{{ plan.estimated_cost }} 元</p>
              </div>
            </el-card>
          </div>
          
          <!-- 行程单 -->
          <div v-else-if="itinerary" class="itinerary-section">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>行程单</span>
                </div>
              </template>
              <div class="itinerary-content">
                <h3>预订成功</h3>
                <el-divider></el-divider>
                <h4>活动安排</h4>
                <el-list>
                  <el-list-item v-for="(activity, index) in itinerary.details.activities" :key="index">
                    <template #default>
                      <div>
                        <span class="activity-name">{{ activity.name }}</span>
                        <span class="activity-time">{{ activity.time }}</span>
                        <span class="activity-status">{{ activity.status }}</span>
                      </div>
                    </template>
                  </el-list-item>
                </el-list>
                <el-divider></el-divider>
                <h4>餐饮预订</h4>
                <div class="restaurant-info">
                  <p>{{ itinerary.details.restaurant.name }}</p>
                  <p>{{ itinerary.details.restaurant.time }}</p>
                  <p>{{ itinerary.details.restaurant.location }}</p>
                  <p>{{ itinerary.details.restaurant.status }}</p>
                </div>
                <el-divider></el-divider>
                <div class="itinerary-actions">
                  <el-button type="primary" @click="exportItinerary">导出行程单</el-button>
                  <el-button type="info" @click="shareItinerary" style="margin-left: 10px">分享</el-button>
                </div>
              </div>
            </el-card>
          </div>
          
          <!-- 默认状态 -->
          <div v-else class="default-section">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>计划预览</span>
                </div>
              </template>
              <p>请输入活动需求并点击生成计划</p>
              <p class="hint">系统已自动定位到您的当前位置</p>
            </el-card>
          </div>
        </div>
      </div>
    </el-main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { generatePlan, confirmPlan, getWeather, getUserLocation, getMapConfig } from './api/index.js'

export default {
  name: 'App',
  setup() {
    const userInput = ref({
      user_id: 'user123',
      input: ''
    })
    const plan = ref(null)
    const itinerary = ref(null)
    const loading = ref(false)
    const thinking = ref(false)
    const thinkingSteps = ref([])
    const isStreaming = ref(false)
    const currentStreamText = ref('')
    const flippedCards = ref([])
    
    // 地图相关
    let map = null
    let markers = []
    const currentLocation = ref({
      lat: 32.0603,
      lng: 118.7969,
      address: '南京市'
    })
    
    // 天气相关
    const currentWeather = ref(null)

    // 获取天气图标
    const getWeatherIcon = (desc) => {
      if (!desc) return '☀️'
      if (desc.includes('晴')) return '☀️'
      if (desc.includes('云')) return '☁️'
      if (desc.includes('雨')) return '🌧️'
      if (desc.includes('雪')) return '❄️'
      return '🌤️'
    }

    // 获取用户当前位置（通过后端代理，保护隐私）
    const fetchUserLocation = async () => {
      try {
        const response = await getUserLocation()
        if (response.success) {
          return {
            lat: response.lat,
            lng: response.lng,
            city: response.city,
            address: response.address
          }
        }
      } catch (error) {
        console.warn('通过后端获取位置失败:', error)
      }
      // 使用默认位置（南京）
      return {
        lat: 32.0603,
        lng: 118.7969,
        city: '南京市',
        address: '南京市'
      }
    }

    // 获取当前天气
    const fetchWeather = async (city) => {
      try {
        const response = await getWeather(city)
        if (response.success) {
          currentWeather.value = response
        }
      } catch (error) {
        console.error('获取天气失败:', error)
      }
    }

    // 动态加载地图脚本
    const loadMapScript = async () => {
      return new Promise(async (resolve, reject) => {
        try {
          // 从后端获取地图配置
          const config = await getMapConfig()
          if (!config.success) {
            throw new Error('获取地图配置失败')
          }
          
          const apiKey = config.map_api_key
          const mapUrl = `${config.map_api_url}?v=1.4.15&key=${apiKey}`
          
          // 创建script标签加载地图API
          const script = document.createElement('script')
          script.type = 'text/javascript'
          script.src = mapUrl
          script.onload = () => {
            console.log('地图API加载成功')
            resolve()
          }
          script.onerror = () => {
            console.error('地图API加载失败')
            reject(new Error('地图API加载失败'))
          }
          
          document.head.appendChild(script)
        } catch (error) {
          console.error('加载地图脚本失败:', error)
          reject(error)
        }
      })
    }

    // 等待AMap加载完成
    const waitForAMap = () => {
      return new Promise((resolve) => {
        const checkAMap = () => {
          if (window.AMap && window.AMap.Map) {
            resolve()
          } else {
            setTimeout(checkAMap, 100)
          }
        }
        checkAMap()
      })
    }

    // 逆地理编码获取地址
    const reverseGeocode = async (lat, lng) => {
      await waitForAMap()
      return new Promise((resolve) => {
        try {
          const geocoder = new window.AMap.Geocoder({
            radius: 1000,
            extensions: 'all'
          })
          geocoder.getAddress([lng, lat], (status, result) => {
            if (status === 'complete' && result.regeocode) {
              const address = result.regeocode.formattedAddress
              resolve(address)
            } else {
              resolve('南京市')
            }
          })
        } catch (error) {
          console.error('逆地理编码失败:', error)
          resolve('南京市')
        }
      })
    }

    // 初始化地图
    const initMap = async (lat, lng) => {
      await waitForAMap()
      
      try {
        const mapContainer = document.getElementById('map')
        if (!mapContainer) return
        
        // 创建地图实例
        map = new window.AMap.Map('map', {
          center: [lng || currentLocation.value.lng, lat || currentLocation.value.lat],
          zoom: 13,
          resizeEnable: true
        })
        
        // 添加比例尺控件
        map.addControl(new window.AMap.Scale())
        
        // 添加缩放控件
        map.addControl(new window.AMap.Zoom())
        
        // 添加定位控件
        map.addControl(new window.AMap.Geolocation({
          enableHighAccuracy: true,
          timeout: 10000,
          buttonPosition: 'RB',
          buttonOffset: new window.AMap.Pixel(10, 20)
        }))
        
        // 在当前位置添加标记
        addMarker(lat || currentLocation.value.lat, lng || currentLocation.value.lng, '您的位置')
        
        // 添加点击事件
        map.on('click', (e) => {
          console.log('地图点击:', e.lnglat.getLng(), e.lnglat.getLat())
        })
        
        console.log('地图初始化成功')
      } catch (error) {
        console.error('地图初始化失败:', error)
      }
    }

    // 添加标记
    const addMarker = (lat, lng, title) => {
      if (!map) return
      
      const marker = new window.AMap.Marker({
        position: [lng, lat],
        title: title,
        icon: new window.AMap.Icon({
          image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
          size: new window.AMap.Size(32, 32),
          imageSize: new window.AMap.Size(32, 32)
        })
      })
      
      map.add(marker)
      markers.push(marker)
      
      // 添加信息窗口
      marker.on('click', () => {
        const infoWindow = new window.AMap.InfoWindow({
          content: `<div style="padding: 10px;">${title}</div>`,
          offset: new window.AMap.Pixel(0, -30)
        })
        infoWindow.open(map, [lng, lat])
      })
    }

    // 标记地点
    const markLocations = () => {
      if (!map || !plan.value || !plan.value.activities) return
      
      // 清除之前的标记（保留当前位置标记）
      if (markers.length > 1) {
        const currentMarker = markers.shift()
        map.remove(markers)
        markers = [currentMarker]
      }
      
      // 为每个活动地点添加标记
      plan.value.activities.forEach((activity, index) => {
        if (activity.location) {
          // 使用地理编码获取坐标
          if (window.AMap) {
            const geocoder = new window.AMap.Geocoder()
            geocoder.getLocation(activity.location, (status, result) => {
              if (status === 'complete' && result.geocodes.length > 0) {
                const location = result.geocodes[0].location
                addMarker(location.lat, location.lng, activity.name)
              }
            })
          }
        }
      })
    }

    // 绘制路线
    const drawRoute = () => {
      if (!map || !plan.value || !plan.value.activities) return
      
      // 简单实现：绘制活动地点连线
      if (plan.value.activities.length >= 2) {
        const points = []
        
        plan.value.activities.forEach((activity) => {
          if (activity.location) {
            // 模拟坐标
            const coords = activity.location.includes('紫金山') 
              ? [118.8533, 32.0705]
              : [118.7969, 32.0603]
            points.push(coords)
          }
        })
        
        if (points.length >= 2) {
          const polyline = new window.AMap.Polyline({
            path: points,
            strokeColor: '#409EFF',
            strokeWeight: 4,
            strokeOpacity: 0.8
          })
          map.add(polyline)
        }
      }
    }

    // 地图控制
    const centerMap = () => {
      if (map) {
        map.setCenter([currentLocation.value.lng, currentLocation.value.lat])
        map.setZoom(13)
      }
    }

    const zoomIn = () => {
      if (map) {
        const currentZoom = map.getZoom()
        map.setZoom(currentZoom + 1)
      }
    }

    const zoomOut = () => {
      if (map) {
        const currentZoom = map.getZoom()
        map.setZoom(currentZoom - 1)
      }
    }

    // 生成计划
    const handleGeneratePlan = async () => {
      try {
        loading.value = true
        thinking.value = true
        thinkingSteps.value = []
        isStreaming.value = true
        currentStreamText.value = ''
        
        // 模拟流式输出
        simulateStreaming()
        
        const response = await generatePlan(userInput.value)
        plan.value = response
        itinerary.value = null
        
        // 标记地点
        markLocations()
        
        // 绘制路线
        drawRoute()
      } catch (error) {
        console.error('生成计划失败:', error)
      } finally {
        loading.value = false
        thinking.value = false
        isStreaming.value = false
      }
    }

    // 模拟流式输出
    const simulateStreaming = () => {
      const steps = [
        '正在解析用户输入...',
        '正在提取关键实体...',
        '正在检索用户偏好...',
        '正在规划活动路线...',
        '正在计算最佳时间安排...',
        '正在生成详细计划...'
      ]
      
      let index = 0
      const interval = setInterval(() => {
        if (index < steps.length) {
          thinkingSteps.value.push(steps[index])
          index++
        } else {
          clearInterval(interval)
        }
      }, 800)
    }

    // 重新规划
    const regeneratePlan = () => {
      handleGeneratePlan()
    }

    // 确认计划
    const handleConfirmPlan = async () => {
      try {
        const response = await confirmPlan({
          user_id: userInput.value.user_id,
          plan_id: plan.value.plan_id || 'test_plan'
        })
        itinerary.value = response
      } catch (error) {
        console.error('确认计划失败:', error)
      }
    }

    // 翻转卡片
    const flipCard = (index) => {
      flippedCards.value[index] = !flippedCards.value[index]
    }

    // 获取活动时间
    const getActivityTime = (activity) => {
      if (plan.value && plan.value.schedule) {
        const schedule = plan.value.schedule.find(item => 
          item.activity.includes(activity.name)
        )
        return schedule ? schedule.time : ''
      }
      return ''
    }

    // 导出行程单
    const exportItinerary = () => {
      console.log('导出行程单')
    }

    // 分享行程单
    const shareItinerary = () => {
      console.log('分享行程单')
    }

    // 组件挂载时初始化
    onMounted(async () => {
      try {
        // 通过后端API获取用户位置（保护隐私）
        const location = await fetchUserLocation()
        currentLocation.value.lat = location.lat
        currentLocation.value.lng = location.lng
        currentLocation.value.address = location.address
        
        // 获取当前城市的天气
        const city = location.city || '南京'
        await fetchWeather(city)
        
        // 动态加载地图脚本（从后端获取配置，保护API key）
        await loadMapScript()
        
        // 等待AMap对象加载完成
        await waitForAMap()
        
        // 初始化地图
        await initMap(location.lat, location.lng)
      } catch (error) {
        console.error('初始化失败:', error)
        // 使用默认值
        try {
          await loadMapScript()
          await waitForAMap()
          initMap()
        } catch (mapError) {
          console.error('地图初始化失败:', mapError)
        }
        fetchWeather('南京')
      }
    })

    return {
      userInput,
      plan,
      itinerary,
      loading,
      thinking,
      thinkingSteps,
      isStreaming,
      currentStreamText,
      flippedCards,
      currentLocation,
      currentWeather,
      generatePlan: handleGeneratePlan,
      regeneratePlan,
      confirmPlan: handleConfirmPlan,
      flipCard,
      getActivityTime,
      getWeatherIcon,
      exportItinerary,
      shareItinerary,
      centerMap,
      zoomIn,
      zoomOut
    }
  }
}
</script>

<style>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  background-color: #409EFF;
  color: white;
  text-align: center;
  line-height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-weather {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.header-weather .badge {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 2px 8px;
}

.el-main {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
}

.main-content {
  display: flex;
  height: 100%;
  gap: 20px;
}

/* 左侧面板 */
.left-panel {
  flex: 0 0 60%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.map-container {
  position: relative;
  height: 500px;
  background-color: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.map {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 10px;
  z-index: 100;
}

.location-info {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 14px;
  color: #333;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 5px;
}

.location-info i {
  color: #409EFF;
}

.route-info {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 天气卡片 */
.weather-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.weather-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
}

.weather-icon {
  font-size: 64px;
}

.weather-info h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.weather-temp {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin: 0 0 5px 0;
}

.weather-desc {
  font-size: 16px;
  color: #666;
  margin: 0 0 10px 0;
}

.weather-details {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #999;
}

/* 右侧面板 */
.right-panel {
  flex: 0 0 40%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.input-section,
.thinking-section,
.plan-section,
.itinerary-section,
.default-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-content,
.itinerary-content {
  padding: 20px;
}

/* 思考过程 */
.thinking-content {
  padding: 10px;
}

.thinking-step {
  margin: 10px 0;
  line-height: 1.5;
}

.streaming {
  font-style: italic;
  color: #409EFF;
}

.typing-indicator {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 活动卡片 */
.activity-cards {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.activity-card {
  position: relative;
  height: 120px;
  perspective: 1000px;
  cursor: pointer;
}

.card-front,
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.6s;
}

.card-front {
  background-color: #f8f9fa;
  border-left: 4px solid #409EFF;
}

.card-back {
  background-color: #e3f2fd;
  transform: rotateY(180deg);
}

.activity-card.flipped .card-front {
  transform: rotateY(180deg);
}

.activity-card.flipped .card-back {
  transform: rotateY(0deg);
}

.card-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 24px;
  color: #409EFF;
}

.card-time {
  font-size: 14px;
  color: #666;
  margin: 5px 0;
}

.card-location {
  font-size: 14px;
  color: #666;
  margin: 5px 0;
}

.card-travel {
  font-size: 12px;
  color: #409EFF;
  margin: 5px 0;
}

.card-notes {
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

/* 行程单 */
.itinerary-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 提示信息 */
.hint {
  color: #999;
  font-size: 14px;
  margin-top: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .left-panel,
  .right-panel {
    flex: 1;
  }
  
  .map-container {
    height: 300px;
  }
}
</style>