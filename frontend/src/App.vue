<template>
  <div class="app-container">
    <el-header>
      <h1>Local Activity Agent</h1>
    </el-header>
    <el-main>
      <el-row :gutter="20">
        <el-col :span="8">
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
                <el-button type="primary" @click="generatePlan">生成计划</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
        <el-col :span="16">
          <el-card v-if="plan">
            <template #header>
              <div class="card-header">
                <span>活动计划</span>
                <el-button type="success" @click="confirmPlan" style="margin-left: 10px">确认执行</el-button>
              </div>
            </template>
            <div class="plan-content">
              <h3>{{ plan.title }}</h3>
              <el-divider></el-divider>
              <h4>时间安排</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="(item, index) in plan.schedule"
                  :key="index"
                  :timestamp="item.time"
                >
                  {{ item.activity }}
                </el-timeline-item>
              </el-timeline>
              <el-divider></el-divider>
              <h4>活动内容</h4>
              <el-list>
                <el-list-item v-for="(activity, index) in plan.activities" :key="index">
                  <template #default>
                    <div>
                      <span class="activity-name">{{ activity.name }}</span>
                      <span class="activity-location">{{ activity.location }}</span>
                      <span v-if="activity.travel_time" class="activity-travel">{{ activity.travel_time }}</span>
                    </div>
                  </template>
                </el-list-item>
              </el-list>
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
          <el-card v-else-if="itinerary">
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
            </div>
          </el-card>
          <el-card v-else>
            <template #header>
              <div class="card-header">
                <span>计划预览</span>
              </div>
            </template>
            <p>请输入活动需求并点击生成计划</p>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script>
import { ref } from 'vue'
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

    const handleGeneratePlan = async () => {
      try {
        const response = await generatePlan(userInput.value)
        plan.value = response.plan
        itinerary.value = null
      } catch (error) {
        console.error('生成计划失败:', error)
      }
    }

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

    return {
      userInput,
      plan,
      itinerary,
      generatePlan: handleGeneratePlan,
      confirmPlan: handleConfirmPlan
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
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-content,
.itinerary-content {
  padding: 10px;
}

.activity-name,
.restaurant-name {
  font-weight: bold;
  margin-right: 10px;
}

.activity-location,
.restaurant-address {
  color: #666;
  margin-right: 10px;
}

.activity-travel {
  color: #409EFF;
}

.activity-time {
  color: #666;
  margin-right: 10px;
}

.activity-status {
  color: #67C23A;
}

.restaurant-info {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>