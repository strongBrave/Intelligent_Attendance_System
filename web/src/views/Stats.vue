<template>
  <div class="stats-container">
    <!-- 页面标题和控制区域 -->
    <div class="page-header">
      <h1>统计分析</h1>
      <div class="header-controls">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          @change="onDateChange"
          size="default"
        />
        <el-button type="primary" @click="refreshAllData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 实时仪表盘 -->
    <el-card class="dashboard-card" v-loading="realtimeLoading">
      <template #header>
        <div class="card-title">
          <el-icon><DataLine /></el-icon>
          实时考勤仪表盘
          <span class="update-time" v-if="realtimeData">
            {{ realtimeData.update_time }}
          </span>
        </div>
      </template>
      
      <div class="realtime-stats" v-if="realtimeData">
        <div class="stat-item">
          <div class="stat-icon total">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ realtimeData.total_employees }}</div>
            <div class="stat-label">总员工数</div>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon signed-in">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ realtimeData.signed_in_count }}</div>
            <div class="stat-label">已签到</div>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon signed-out">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ realtimeData.signed_out_count }}</div>
            <div class="stat-label">已签退</div>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon attendance-rate">
            <el-icon><Star /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ realtimeData.attendance_rate }}%</div>
            <div class="stat-label">出勤率</div>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon late">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ realtimeData.late_count }}</div>
            <div class="stat-label">迟到</div>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon absent">
            <el-icon><Close /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ realtimeData.absent_count }}</div>
            <div class="stat-label">缺勤</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 考勤状态分布饼图 -->
      <el-card class="chart-card" v-loading="distributionLoading">
                 <template #header>
           <div class="card-title">
             <el-icon><Document /></el-icon>
             考勤状态分布
             <span class="chart-date">{{ formatDate(selectedDate) }}</span>
           </div>
         </template>
        <div ref="distributionChart" class="chart-container"></div>
      </el-card>

      <!-- 部门出勤率对比柱状图 -->
      <el-card class="chart-card" v-loading="departmentLoading">
                 <template #header>
           <div class="card-title">
             <el-icon><Files /></el-icon>
             部门出勤率对比
             <span class="chart-date">{{ formatDate(selectedDate) }}</span>
           </div>
         </template>
        <div ref="departmentChart" class="chart-container"></div>
      </el-card>

      <!-- 出勤率趋势折线图 -->
      <el-card class="chart-card chart-card-wide" v-loading="trendLoading">
                 <template #header>
           <div class="card-title">
             <el-icon><Star /></el-icon>
             出勤率趋势
            <span class="trend-period">{{ trendPeriod }}</span>
            <div class="trend-controls">
              <el-button-group size="small">
                <el-button 
                  :type="trendDays === 7 ? 'primary' : ''" 
                  @click="changeTrendDays(7)"
                >
                  7天
                </el-button>
                <el-button 
                  :type="trendDays === 14 ? 'primary' : ''" 
                  @click="changeTrendDays(14)"
                >
                  14天
                </el-button>
                <el-button 
                  :type="trendDays === 30 ? 'primary' : ''" 
                  @click="changeTrendDays(30)"
                >
                  30天
                </el-button>
              </el-button-group>
            </div>
          </div>
        </template>
        <div ref="trendChart" class="chart-container"></div>
      </el-card>

      <!-- 打卡地点分布图 -->
      <el-card class="chart-card" v-loading="locationLoading">
         <template #header>
           <div class="card-title">
             <el-icon><LocationFilled /></el-icon>
             签到地点分布地图
             <span class="chart-date">{{ formatDate(selectedDate) }}</span>
           </div>
         </template>
        <div ref="signInMap" class="map-container"></div>
        
        <!-- 签到统计信息 -->
        <div class="location-summary" v-if="signInMapData.length > 0">
          <el-divider content-position="left">签到统计 ({{ signInMapData.length }}条记录)</el-divider>
          <div class="location-stats">
            <el-tag v-for="status in getSignInStats()" :key="status.name" 
                    :type="getStatusTagType(status.name)" size="small">
              {{ status.name }}: {{ status.count }}人
            </el-tag>
          </div>
        </div>
        
        <div v-else class="no-data">
          <el-empty description="暂无签到地点数据" :image-size="80" />
        </div>
      </el-card>

      <!-- 签退地点分布地图 -->
      <el-card class="chart-card" v-loading="locationLoading">
         <template #header>
           <div class="card-title">
             <el-icon><LocationFilled /></el-icon>
             签退地点分布地图
             <span class="chart-date">{{ formatDate(selectedDate) }}</span>
           </div>
         </template>
        <div ref="signOutMap" class="map-container"></div>
        
        <!-- 签退统计信息 -->
        <div class="location-summary" v-if="signOutMapData.length > 0">
          <el-divider content-position="left">签退统计 ({{ signOutMapData.length }}条记录)</el-divider>
          <div class="location-stats">
            <el-tag v-for="status in getSignOutStats()" :key="status.name" 
                    :type="getStatusTagType(status.name)" size="small">
              {{ status.name }}: {{ status.count }}人
            </el-tag>
          </div>
        </div>
        
        <div v-else class="no-data">
          <el-empty description="暂无签退地点数据" :image-size="80" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, DataLine, User, Clock, Timer, Star, Warning, Close,
  Document, Files, LocationFilled
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '../api'

// 响应式数据
const loading = ref(false)
const selectedDate = ref(new Date())

// 各个图表的加载状态
const realtimeLoading = ref(false)
const distributionLoading = ref(false)
const departmentLoading = ref(false)
const trendLoading = ref(false)
const locationLoading = ref(false)

// 数据
const realtimeData = ref(null)
const distributionData = ref([])
const departmentData = ref([])
const trendData = ref([])
const trendPeriod = ref('')
const trendDays = ref(7)
const signInMapData = ref([])
const signOutMapData = ref([])

// 图表实例
const distributionChart = ref(null)
const departmentChart = ref(null)
const trendChart = ref(null)
const signInMap = ref(null)
const signOutMap = ref(null)

let distributionChartInstance = null
let departmentChartInstance = null
let trendChartInstance = null
let signInMapInstance = null
let signOutMapInstance = null

// 自动刷新定时器
let refreshTimer = null

// 获取实时仪表盘数据
const fetchRealtimeData = async () => {
  realtimeLoading.value = true
  try {
    const response = await api.get('/admin/stats/realtime-dashboard')
    if (response.data.success) {
      realtimeData.value = response.data.data
    }
  } catch (error) {
    console.error('获取实时数据失败:', error)
    ElMessage.error('获取实时数据失败')
  } finally {
    realtimeLoading.value = false
  }
}

// 获取考勤状态分布数据
const fetchDistributionData = async () => {
  distributionLoading.value = true
  try {
    const dateStr = formatDateString(selectedDate.value)
    const response = await api.get('/admin/stats/attendance-distribution', {
      params: { date: dateStr }
    })
    if (response.data.success) {
      distributionData.value = response.data.data
      await nextTick()
      renderDistributionChart()
    }
  } catch (error) {
    console.error('获取考勤分布数据失败:', error)
    ElMessage.error('获取考勤分布数据失败')
  } finally {
    distributionLoading.value = false
  }
}

// 获取部门出勤率对比数据
const fetchDepartmentData = async () => {
  departmentLoading.value = true
  try {
    const dateStr = formatDateString(selectedDate.value)
    const response = await api.get('/admin/stats/department-attendance-rate', {
      params: { date: dateStr }
    })
    if (response.data.success) {
      departmentData.value = response.data.data
      await nextTick()
      renderDepartmentChart()
    }
  } catch (error) {
    console.error('获取部门数据失败:', error)
    ElMessage.error('获取部门数据失败')
  } finally {
    departmentLoading.value = false
  }
}

// 获取出勤率趋势数据
const fetchTrendData = async () => {
  trendLoading.value = true
  try {
    const response = await api.get('/admin/stats/attendance-trend', {
      params: { days: trendDays.value }
    })
    if (response.data.success) {
      trendData.value = response.data.data
      trendPeriod.value = response.data.period
      await nextTick()
      renderTrendChart()
    }
  } catch (error) {
    console.error('获取趋势数据失败:', error)
    ElMessage.error('获取趋势数据失败')
  } finally {
    trendLoading.value = false
  }
}

// 获取打卡地点分布数据
const fetchMapData = async () => {
  locationLoading.value = true
  try {
    const dateStr = formatDateString(selectedDate.value)
    const response = await api.get('/admin/stats/attendance-map', {
      params: { date: dateStr }
    })
    if (response.data.success) {
      signInMapData.value = response.data.sign_in_data || []
      signOutMapData.value = response.data.sign_out_data || []
      await nextTick()
      renderMaps()
    }
  } catch (error) {
    console.error('获取地图数据失败:', error)
    ElMessage.error('获取地图数据失败')
  } finally {
    locationLoading.value = false
  }
}

// 渲染考勤状态分布饼图
const renderDistributionChart = () => {
  if (!distributionChart.value) return
  
  if (!distributionChartInstance) {
    distributionChartInstance = echarts.init(distributionChart.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '考勤状态',
        type: 'pie',
        radius: '60%',
        center: ['60%', '50%'],
        data: distributionData.value,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          formatter: '{b}\n{c}人'
        }
      }
    ],
    color: ['#67C23A', '#E6A23C', '#F56C6C', '#F78989', '#9370DB']
  }
  
  distributionChartInstance.setOption(option)
}

// 渲染部门出勤率对比柱状图
const renderDepartmentChart = () => {
  if (!departmentChart.value) return
  
  if (!departmentChartInstance) {
    departmentChartInstance = echarts.init(departmentChart.value)
  }
  
  const departments = departmentData.value.map(item => item.department)
  const attendanceRates = departmentData.value.map(item => item.attendance_rate)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const data = departmentData.value[params[0].dataIndex]
        return `${data.department}<br/>
                出勤率: ${data.attendance_rate}%<br/>
                出勤人数: ${data.attended_count}/${data.total_employees}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: departments,
      axisLabel: {
        interval: 0,
        rotate: departments.length > 5 ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: '出勤率(%)',
      min: 0,
      max: 100
    },
    series: [
      {
        type: 'bar',
        data: attendanceRates,
        itemStyle: {
          color: function(params) {
            const rate = params.value
            if (rate >= 90) return '#67C23A'
            if (rate >= 80) return '#E6A23C'
            if (rate >= 70) return '#F56C6C'
            return '#F78989'
          },
          borderRadius: [4, 4, 0, 0]
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%'
        }
      }
    ]
  }
  
  departmentChartInstance.setOption(option)
}

// 渲染出勤率趋势折线图
const renderTrendChart = () => {
  if (!trendChart.value) return
  
  if (!trendChartInstance) {
    trendChartInstance = echarts.init(trendChart.value)
  }
  
  const dates = trendData.value.map(item => item.weekday)
  const rates = trendData.value.map(item => item.attendance_rate)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = trendData.value[params[0].dataIndex]
        return `${data.date}<br/>
                出勤率: ${data.attendance_rate}%<br/>
                出勤人数: ${data.attended_count}/${data.total_employees}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '出勤率(%)',
      min: 0,
      max: 100
    },
    series: [
      {
        type: 'line',
        data: rates,
        smooth: true,
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ]
          }
        },
        symbol: 'circle',
        symbolSize: 6,
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%'
        }
      }
    ]
  }
  
  trendChartInstance.setOption(option)
}

// 渲染地图
const renderMaps = () => {
  renderSignInMap()
  renderSignOutMap()
}

// 渲染签到地图
const renderSignInMap = () => {
  if (!signInMap.value) return
  
  // 检查是否有高德地图
  if (typeof AMap === 'undefined') {
    // 如果没有高德地图，显示提示信息
    signInMap.value.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #666;">
        <p>📍 地图功能需要配置高德地图API密钥</p>
        <p style="font-size: 12px;">请在 index.html 中替换 YOUR_AMAP_KEY</p>
        <p style="font-size: 12px;">签到数据: ${signInMapData.value.length} 条记录</p>
      </div>
    `
    return
  }
  
  // 创建高德地图实例
  if (signInMapInstance) {
    signInMapInstance.destroy()
  }
  
  signInMapInstance = new AMap.Map(signInMap.value, {
    zoom: 13,
    center: [116.397428, 39.90923], // 默认中心点（北京）
    mapStyle: 'amap://styles/normal'
  })
  
  // 添加标记点
  signInMapData.value.forEach(point => {
    const marker = new AMap.Marker({
      position: [point.lng, point.lat],
      title: `${point.user_name} - ${point.status}`,
      icon: getMarkerIcon(point.status, 'sign_in')
    })
    
    // 添加信息窗口
    const infoWindow = new AMap.InfoWindow({
      content: `
        <div style="padding: 10px;">
          <h4>${point.user_name}</h4>
          <p><strong>状态:</strong> ${getStatusText(point.status)}</p>
          <p><strong>时间:</strong> ${point.time}</p>
          <p><strong>地址:</strong> ${point.address}</p>
          ${point.remark ? `<p><strong>备注:</strong> ${point.remark}</p>` : ''}
        </div>
      `
    })
    
    marker.on('click', () => {
      infoWindow.open(signInMapInstance, marker.getPosition())
    })
    
    signInMapInstance.add(marker)
  })
  
  // 自动调整视野
  if (signInMapData.value.length > 0) {
    const bounds = signInMapData.value.map(point => [point.lng, point.lat])
    signInMapInstance.setFitView(bounds)
  }
}

// 渲染签退地图
const renderSignOutMap = () => {
  if (!signOutMap.value) return
  
  // 检查是否有高德地图
  if (typeof AMap === 'undefined') {
    signOutMap.value.innerHTML = `
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #666;">
        <p>📍 地图功能需要配置高德地图API密钥</p>
        <p style="font-size: 12px;">请在 index.html 中替换 YOUR_AMAP_KEY</p>
        <p style="font-size: 12px;">签退数据: ${signOutMapData.value.length} 条记录</p>
      </div>
    `
    return
  }
  
  // 创建高德地图实例
  if (signOutMapInstance) {
    signOutMapInstance.destroy()
  }
  
  signOutMapInstance = new AMap.Map(signOutMap.value, {
    zoom: 13,
    center: [116.397428, 39.90923], // 默认中心点（北京）
    mapStyle: 'amap://styles/normal'
  })
  
  // 添加标记点
  signOutMapData.value.forEach(point => {
    const marker = new AMap.Marker({
      position: [point.lng, point.lat],
      title: `${point.user_name} - ${point.status}`,
      icon: getMarkerIcon(point.status, 'sign_out')
    })
    
    // 添加信息窗口
    const infoWindow = new AMap.InfoWindow({
      content: `
        <div style="padding: 10px;">
          <h4>${point.user_name}</h4>
          <p><strong>状态:</strong> ${getStatusText(point.status)}</p>
          <p><strong>时间:</strong> ${point.time}</p>
          <p><strong>地址:</strong> ${point.address}</p>
          ${point.remark ? `<p><strong>备注:</strong> ${point.remark}</p>` : ''}
        </div>
      `
    })
    
    marker.on('click', () => {
      infoWindow.open(signOutMapInstance, marker.getPosition())
    })
    
    signOutMapInstance.add(marker)
  })
  
  // 自动调整视野
  if (signOutMapData.value.length > 0) {
    const bounds = signOutMapData.value.map(point => [point.lng, point.lat])
    signOutMapInstance.setFitView(bounds)
  }
}

// 获取标记图标
const getMarkerIcon = (status, checkType) => {
  const colors = {
    normal: '#67C23A',    // 绿色
    late: '#E6A23C',      // 橙色
    absent: '#F56C6C',    // 红色
    early_leave: '#F78989', // 浅红色
    late_leave: '#9370DB'   // 紫色
  }
  
  const color = colors[status] || '#909399'
  const symbol = checkType === 'sign_in' ? '↑' : '↓'
  
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(`
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" fill="${color}" stroke="white" stroke-width="2"/>
      <text x="12" y="16" text-anchor="middle" fill="white" font-size="12" font-weight="bold">${symbol}</text>
    </svg>
  `)}`
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    normal: '正常',
    late: '迟到', 
    absent: '缺勤',
    early_leave: '早退',
    late_leave: '晚退'
  }
  return statusMap[status] || status
}

// 获取签到统计
const getSignInStats = () => {
  const stats = {}
  signInMapData.value.forEach(point => {
    const statusText = getStatusText(point.status)
    stats[statusText] = (stats[statusText] || 0) + 1
  })
  return Object.entries(stats).map(([name, count]) => ({ name, count }))
}

// 获取签退统计  
const getSignOutStats = () => {
  const stats = {}
  signOutMapData.value.forEach(point => {
    const statusText = getStatusText(point.status)
    stats[statusText] = (stats[statusText] || 0) + 1
  })
  return Object.entries(stats).map(([name, count]) => ({ name, count }))
}

// 获取状态标签类型
const getStatusTagType = (statusName) => {
  const typeMap = {
    '正常': 'success',
    '迟到': 'warning',
    '缺勤': 'danger',
    '早退': 'warning', 
    '晚退': 'info'
  }
  return typeMap[statusName] || ''
}

// 工具函数
const formatDate = (date) => {
  if (!date) return ''
  return date.toLocaleDateString('zh-CN')
}

const formatDateString = (date) => {
  if (!date) return ''
  return date.toISOString().split('T')[0]
}

// 事件处理
const onDateChange = () => {
  fetchDistributionData()
  fetchDepartmentData()
  fetchMapData()
}

const changeTrendDays = (days) => {
  trendDays.value = days
  fetchTrendData()
}

const refreshAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchRealtimeData(),
      fetchDistributionData(),
      fetchDepartmentData(),
      fetchTrendData(),
      fetchMapData()
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

// 响应式处理
const handleResize = () => {
  if (distributionChartInstance) distributionChartInstance.resize()
  if (departmentChartInstance) departmentChartInstance.resize()
  if (trendChartInstance) trendChartInstance.resize()
  if (signInMapInstance) signInMapInstance.resize()
  if (signOutMapInstance) signOutMapInstance.resize()
}

// 生命周期
onMounted(() => {
  refreshAllData()
  
  // 设置自动刷新实时数据
  refreshTimer = setInterval(() => {
    fetchRealtimeData()
  }, 30000) // 每30秒刷新一次实时数据
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  // 清理定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 清理图表实例
  if (distributionChartInstance) distributionChartInstance.dispose()
  if (departmentChartInstance) departmentChartInstance.dispose()
  if (trendChartInstance) trendChartInstance.dispose()
  if (signInMapInstance) signInMapInstance.dispose()
  if (signOutMapInstance) signOutMapInstance.dispose()
  
  // 移除事件监听
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.stats-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.dashboard-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.update-time {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.chart-date {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

.trend-period {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
  font-weight: normal;
  margin-right: 12px;
}

.trend-controls {
  flex-shrink: 0;
}

.realtime-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid transparent;
}

.stat-item .stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 20px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.stat-icon.signed-in {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: #4facfe;
}

.stat-icon.signed-out {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border-color: #43e97b;
}

.stat-icon.attendance-rate {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-color: #f093fb;
}

.stat-icon.late {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  border-color: #fa709a;
}

.stat-icon.absent {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  border-color: #ff9a9e;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-card-wide {
  grid-column: span 2;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.map-container {
  width: 100%;
  height: 300px;
  border-radius: 8px;
  overflow: hidden;
}

.location-summary {
  margin-top: 16px;
}

.location-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .chart-card-wide {
    grid-column: span 1;
  }
  
  .charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .stats-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-controls {
    justify-content: space-between;
  }
  
  .realtime-stats {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style> 