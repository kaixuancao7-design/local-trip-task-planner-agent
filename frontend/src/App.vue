<template>
  <div class="app-container">
    <el-header>
      <h1>Local Activity Agent</h1>
    </el-header>
    <el-main>
      <!-- 双栏布局 -->
      <div class="main-content">
        <!-- 左侧：地图与行程可视化区域 (60%) -->
        <div class="left-panel">
          <div class="map-container">
            <div id="map" class="map"></div>
            <div class="map-controls">
              <el-button size="small" @click="centerMap">定位</el-button>
              <el-button size="small" @click="zoomIn">放大</el-button>
              <el-button size="small" @click="zoomOut">缩小</el-button>
            </div>
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
            </el-card>
          </div>
        </div>
      </div>
    </el-main>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { generatePlan, confirmPlan } from './api/index.js'

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
    let map = null
    let markers = []

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
        plan.value = response.plan
        itinerary.value = null
        
        // 初始化地图
        initMap()
        
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
      }, 1000)
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
          plan_id: plan.value.plan_id
        })
        itinerary.value = response.itinerary
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
      // 实现导出功能
      console.log('导出行程单')
    }

    // 分享行程单
    const shareItinerary = () => {
      // 实现分享功能
      console.log('分享行程单')
    }

    // 初始化地图
    const initMap = () => {
      // 这里集成高德地图API
      // 由于是模拟环境，我们只创建一个占位符
      console.log('初始化地图')
    }

    // 标记地点
    const markLocations = () => {
      if (plan.value && plan.value.activities) {
        console.log('标记地点:', plan.value.activities)
      }
    }

    // 绘制路线
    const drawRoute = () => {
      if (plan.value && plan.value.activities) {
        console.log('绘制路线:', plan.value.activities)
      }
    }

    // 地图控制
    const centerMap = () => {
      console.log('定位地图')
    }

    const zoomIn = () => {
      console.log('放大地图')
    }

    const zoomOut = () => {
      console.log('缩小地图')
    }

    // 组件挂载时初始化
    onMounted(() => {
      // 初始化地图
      initMap()
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
      generatePlan: handleGeneratePlan,
      regeneratePlan,
      confirmPlan: handleConfirmPlan,
      flipCard,
      getActivityTime,
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

.route-info {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
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