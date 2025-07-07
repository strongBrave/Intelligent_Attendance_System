<template>
  <div class="attendance-container">
    <!-- 页面标题和当前时间 -->
    <div class="page-header">
      <div class="header-left">
        <h1>考勤管理</h1>
        <div class="current-time">
          <el-icon><Clock /></el-icon>
          <span>{{ currentDateTime }}</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 查询表单 -->
    <el-card class="query-card">
      <el-form :inline="true" class="query-form">
        <el-form-item label="员工姓名">
          <el-input v-model="query.name" placeholder="员工姓名" style="width:150px" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="query.department_id" placeholder="选择部门" style="width:180px" clearable>
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <div style="display: flex; align-items: center; gap: 8px;">
            <el-date-picker 
              v-model="query.dateRange" 
              type="daterange" 
              range-separator="至"
              start-placeholder="开始日期" 
              end-placeholder="结束日期"
              style="width:280px"
              :disabled-date="disabledDate"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
            <el-button size="small" @click="setDateRange('today')">今天</el-button>
            <el-button size="small" @click="setDateRange('yesterday')">昨天</el-button>
            <el-button size="small" @click="setDateRange('thisWeek')">本周</el-button>
            <el-button size="small" @click="setDateRange('lastWeek')">上周</el-button>
            <el-button size="small" @click="setDateRange('thisMonth')">本月</el-button>
            <el-button size="small" @click="setDateRange('lastMonth')">上月</el-button>
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="选择状态" style="width:120px" clearable>
            <el-option label="正常" value="normal" />
            <el-option label="迟到" value="late" />
            <el-option label="缺勤" value="absent" />
            <el-option label="早退" value="early_leave" />
            <el-option label="晚退" value="late_leave" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getList" :loading="loading">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 考勤记录表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <span>考勤记录 (共 {{ total }} 条)</span>
          <div class="table-actions">
            <el-button size="small" @click="exportData">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="list" 
        border 
        stripe 
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
      >
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="name" label="员工姓名" width="120" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="check_type" label="类型" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getCheckTypeTag(scope.row.check_type)" size="small">
              {{ getCheckTypeText(scope.row.check_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="140" align="center">
          <template #default="scope">
            <div class="status-selector">
              <el-select v-model="scope.row.status" size="small" style="width: 100px" placeholder="选择状态">
                <!-- 缺勤记录（没有id）只能补录签到相关状态 -->
                <template v-if="!scope.row.id">
                  <el-option label="正常签到" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="缺勤" value="absent" />
                </template>
                <!-- 已存在的记录可以修改为所有状态 -->
                <template v-else>
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="晚退" value="late_leave" />
                  <el-option label="缺勤" value="absent" />
                </template>
              </el-select>
              <el-button size="small" type="primary" @click="updateStatus(scope.row)" style="margin-left: 8px">更新</el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="日期" width="120" align="center" />
        <el-table-column prop="time" label="时间" width="100" align="center" />
        <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" @click="viewDetail(scope.row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="!loading && list.length === 0" 
        description="暂无考勤数据" 
        :image-size="120"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Refresh, Search, Download } from '@element-plus/icons-vue'
import api from '../api'

const loading = ref(false)
const list = ref([])
const departments = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const currentDateTime = ref('')
let timeInterval = null

const query = ref({ 
  name: '', 
  department_id: '', 
  dateRange: [], 
  status: '' 
})

// 获取当前时间
const updateCurrentTime = () => {
  const now = new Date()
  currentDateTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    weekday: 'long'
  })
}

// 获取部门列表
const fetchDepartments = async () => {
  try {
    const response = await api.get('/admin/departments')
    departments.value = response.data.departments || []
  } catch (error) {
    console.error('获取部门列表失败:', error)
    ElMessage.error('获取部门列表失败')
  }
}

// 获取考勤记录
const getList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (query.value.name) params.name = query.value.name
    if (query.value.department_id) params.department_id = query.value.department_id
    if (query.value.dateRange && query.value.dateRange.length === 2) {
      params.start_date = query.value.dateRange[0]
      params.end_date = query.value.dateRange[1]
    }
    if (query.value.status) params.status = query.value.status
    
    const response = await api.get('/admin/attendance/records', { params })
    list.value = response.data.records || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('获取考勤记录失败:', error)
    const errorMsg = error.response?.data?.error || '获取考勤记录失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 重置查询条件
const resetQuery = () => {
  query.value = { 
    name: '', 
    department_id: '', 
    dateRange: [], 
    status: '' 
  }
  currentPage.value = 1
  getList()
}

// 刷新数据
const refreshData = () => {
  getList()
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  getList()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  getList()
}

// 禁用未来日期
const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

// 获取打卡类型标签
const getCheckTypeTag = (type) => {
  const typeMap = {
    'sign_in': 'primary',
    'sign_out': 'success'
  }
  return typeMap[type] || 'info'
}

// 获取打卡类型文本
const getCheckTypeText = (type) => {
  const typeMap = {
    'sign_in': '签到',
    'sign_out': '签退'
  }
  return typeMap[type] || type
}

// 获取状态标签
const getStatusTag = (status) => {
  const statusMap = {
    'normal': 'success',
    'late': 'warning',
    'absent': 'danger',
    'early_leave': 'danger',
    'late_leave': 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'normal': '正常',
    'late': '迟到',
    'absent': '缺勤',
    'early_leave': '早退',
    'late_leave': '晚退'
  }
  return statusMap[status] || status
}

// 查看详情
const viewDetail = (row) => {
  console.log('查看详情:', row)
  // 这里可以添加查看详情的逻辑
}

// 导出数据
const exportData = () => {
  ElMessage.info('导出功能开发中...')
}

// 更新状态
const updateStatus = async (row) => {
  // 缺勤补录：如果没有id，调用补录接口
  if (!row.id) {
    try {
      const today = row.date || new Date().toISOString().slice(0, 10)
      await api.post('/admin/attendance/makeup', {
        user_id: row.user_id,
        date: today,
        check_type: row.check_type || 'sign_in',
        status: row.status
      })
      ElMessage.success('补录成功')
      await getList()
    } catch (error) {
      console.error('补录失败:', error)
      const errorMsg = error.response?.data?.error || '补录失败'
      ElMessage.error(errorMsg)
      await getList()
    }
    return
  }
  // 正常更新
  const oldStatus = row.status
  try {
    await api.put(`/admin/attendance/${row.id}/status`, {
      status: row.status
    })
    ElMessage.success('状态更新成功')
    await getList()
  } catch (error) {
    console.error('更新状态失败:', error)
    const errorMsg = error.response?.data?.error || '更新状态失败'
    ElMessage.error(errorMsg)
    row.status = oldStatus
    await getList()
  }
}

// 设置日期范围
const setDateRange = (range) => {
  const today = new Date()
  const todayStr = today.toISOString().slice(0, 10)
  
  let startDate, endDate
  
  switch (range) {
    case 'today':
      startDate = todayStr
      endDate = todayStr
      break
    case 'yesterday':
      const yesterday = new Date(today)
      yesterday.setDate(today.getDate() - 1)
      startDate = yesterday.toISOString().slice(0, 10)
      endDate = startDate
      break
    case 'thisWeek':
      const thisWeekStart = new Date(today)
      thisWeekStart.setDate(today.getDate() - today.getDay())
      startDate = thisWeekStart.toISOString().slice(0, 10)
      endDate = todayStr
      break
    case 'lastWeek':
      const lastWeekStart = new Date(today)
      lastWeekStart.setDate(today.getDate() - today.getDay() - 7)
      const lastWeekEnd = new Date(lastWeekStart)
      lastWeekEnd.setDate(lastWeekStart.getDate() + 6)
      startDate = lastWeekStart.toISOString().slice(0, 10)
      endDate = lastWeekEnd.toISOString().slice(0, 10)
      break
    case 'thisMonth':
      const thisMonthStart = new Date(today.getFullYear(), today.getMonth(), 1)
      startDate = thisMonthStart.toISOString().slice(0, 10)
      endDate = todayStr
      break
    case 'lastMonth':
      const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1)
      const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0)
      startDate = lastMonthStart.toISOString().slice(0, 10)
      endDate = lastMonthEnd.toISOString().slice(0, 10)
      break
    default:
      return
  }
  
  query.value.dateRange = [startDate, endDate]
  getList()
}

onMounted(() => {
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 1000)
  fetchDepartments()
  getList()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.attendance-container {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-left h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.current-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
}

.query-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

.query-form {
  margin: 0;
}

.table-card {
  border-radius: 8px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background: #f5f7fa !important;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f0f0f0;
}

.status-selector {
  display: flex;
  align-items: center;
}
</style> 