<template>
  <div class="department-detail-container">
    <!-- 页面标题和当前时间 -->
    <div class="page-header">
      <div class="header-left">
        <div class="breadcrumb">
          <el-button link @click="$router.push('/dashboard')">
            <el-icon><ArrowLeft /></el-icon>
            返回仪表盘
          </el-button>
          <el-divider direction="vertical" />
          <h1>{{ department?.name }} - 考勤详情</h1>
        </div>
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

    <!-- 部门统计信息 -->
    <div class="stats-cards" v-if="attendanceDetail">
      <el-card class="stat-card total">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.total_employees }}</div>
            <div class="stat-label">部门总人数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card sign-in">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.sign_in_count }}</div>
            <div class="stat-label">正常签到</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card sign-out">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.sign_out_count }}</div>
            <div class="stat-label">正常签退</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card late">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.late_count }}</div>
            <div class="stat-label">迟到</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card early-leave">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><ArrowDown /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.early_leave_count }}</div>
            <div class="stat-label">早退</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card absent">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Close /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.absent_count }}</div>
            <div class="stat-label">缺勤</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card not-yet-time">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.not_yet_time_count }}</div>
            <div class="stat-label">未到时间</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 考勤数据展示 -->
    <div class="attendance-sections">
      <!-- 正常签到记录 -->
      <el-card class="attendance-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><Clock /></el-icon>
              正常签到 ({{ attendanceDetail?.sign_in_records?.length || 0 }})
            </span>
            <el-tag type="primary" size="small">今日</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.sign_in_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签到时间" width="180" align="center" />
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="缺勤" value="absent" />
                  <el-option label="未到时间" value="not_yet_time" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button size="small" type="primary" @click="viewDetail(scope.row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.sign_in_records || attendanceDetail.sign_in_records.length === 0)" 
          description="暂无正常签到记录" 
          :image-size="80"
        />
      </el-card>

      <!-- 正常签退记录 -->
      <el-card class="attendance-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><Timer /></el-icon>
              正常签退 ({{ attendanceDetail?.sign_out_records?.length || 0 }})
            </span>
            <el-tag type="success" size="small">今日</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.sign_out_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签退时间" width="180" align="center" />
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="缺勤" value="absent" />
                  <el-option label="未到时间" value="not_yet_time" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button size="small" type="primary" @click="viewDetail(scope.row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.sign_out_records || attendanceDetail.sign_out_records.length === 0)" 
          description="暂无正常签退记录" 
          :image-size="80"
        />
      </el-card>

      <!-- 迟到记录 -->
      <el-card class="attendance-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><Warning /></el-icon>
              迟到记录 ({{ attendanceDetail?.late_records?.length || 0 }})
            </span>
            <el-tag type="warning" size="small">迟到</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.late_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签到时间" width="180" align="center" />
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="缺勤" value="absent" />
                  <el-option label="未到时间" value="not_yet_time" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button size="small" type="primary" @click="viewDetail(scope.row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.late_records || attendanceDetail.late_records.length === 0)" 
          description="暂无迟到记录" 
          :image-size="80"
        />
      </el-card>

      <!-- 早退记录 -->
      <el-card class="attendance-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><ArrowDown /></el-icon>
              早退记录 ({{ attendanceDetail?.early_leave_records?.length || 0 }})
            </span>
            <el-tag type="danger" size="small">早退</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.early_leave_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签退时间" width="180" align="center" />
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="缺勤" value="absent" />
                  <el-option label="未到时间" value="not_yet_time" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button size="small" type="primary" @click="viewDetail(scope.row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.early_leave_records || attendanceDetail.early_leave_records.length === 0)" 
          description="暂无早退记录" 
          :image-size="80"
        />
      </el-card>

      <!-- 缺勤记录 -->
      <el-card class="attendance-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><Close /></el-icon>
              缺勤记录 ({{ attendanceDetail?.absent_records?.length || 0 }})
            </span>
            <el-tag type="danger" size="small">缺勤</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.absent_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签到时间" width="180" align="center">
            <template #default="scope">
              <span style="color: #909399;">未签到</span>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip>
            <template #default="scope">
              <span style="color: #909399;">无位置信息</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
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
                    <el-option label="缺勤" value="absent" />
                    <el-option label="未到时间" value="not_yet_time" />
                  </template>
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="200">
            <template #default>
              <span style="color: #909399;">今日未签到</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.absent_records || attendanceDetail.absent_records.length === 0)" 
          description="暂无缺勤记录" 
          :image-size="80"
        />
      </el-card>

      <!-- 未到签到时间记录 -->
      <el-card class="attendance-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><Timer /></el-icon>
              未到签到时间 ({{ attendanceDetail?.not_yet_time_records?.length || 0 }})
            </span>
            <el-tag type="info" size="small">未到时间</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.not_yet_time_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签到时间" width="180" align="center" />
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="缺勤" value="absent" />
                  <el-option label="未到时间" value="not_yet_time" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-button size="small" type="primary" @click="viewDetail(scope.row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.not_yet_time_records || attendanceDetail.not_yet_time_records.length === 0)" 
          description="暂无未到签到时间记录" 
          :image-size="80"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, Clock, Refresh, User, Timer, Warning, Close, 
  TrendCharts, ArrowDown
} from '@element-plus/icons-vue'
import api from '../api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const department = ref(null)
const attendanceDetail = ref(null)
const currentDateTime = ref('')
let timeInterval = null

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

// 获取部门信息
const fetchDepartmentInfo = async () => {
  try {
    const response = await api.get(`/admin/departments/${route.params.id}`)
    department.value = response.data.department
  } catch (error) {
    console.error('获取部门信息失败:', error)
    ElMessage.error('获取部门信息失败')
  }
}

// 获取部门详细考勤数据
const fetchAttendanceDetail = async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/departments/${route.params.id}/attendance-detail`)
    attendanceDetail.value = response.data
  } catch (error) {
    console.error('获取考勤详情失败:', error)
    const errorMsg = error.response?.data?.error || '获取考勤详情失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 更新考勤状态
const updateStatus = async (record) => {
  console.log('更新状态被调用:', record)

  // 缺勤记录补录
  if (!record.id) {
    try {
      const today = attendanceDetail.value?.date || new Date().toISOString().slice(0, 10)
      const res = await api.post('/admin/attendance/makeup', {
        user_id: record.user_id,
        date: today,
        check_type: 'sign_in', // 默认补录为签到
        status: record.status
      })
      ElMessage.success('补录成功')
      await fetchAttendanceDetail()
    } catch (error) {
      console.error('补录失败:', error)
      const errorMsg = error.response?.data?.error || '补录失败'
      ElMessage.error(errorMsg)
      await fetchAttendanceDetail()
    }
    return
  }

  // 正常更新
  const oldStatus = record.status
  try {
    const response = await api.put(`/admin/attendance/${record.id}/status`, {
      status: record.status
    })
    ElMessage.success('状态更新成功')
    await fetchAttendanceDetail()
  } catch (error) {
    console.error('更新状态失败:', error)
    const errorMsg = error.response?.data?.error || '更新状态失败'
    ElMessage.error(errorMsg)
    record.status = oldStatus
    await fetchAttendanceDetail()
  }
}

// 刷新数据
const refreshData = () => {
  fetchAttendanceDetail()
}

// 查看详情
const viewDetail = (row) => {
  console.log('查看详情:', row)
  // 这里可以添加查看详情的逻辑
}

onMounted(() => {
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 1000)
  fetchDepartmentInfo()
  fetchAttendanceDetail()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.department-detail-container {
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

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 12px;
}

.breadcrumb h1 {
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

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 8px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.sign-in .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.sign-out .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.late .stat-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.early-leave .stat-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.absent .stat-icon {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.not-yet-time .stat-icon {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.attendance-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.attendance-section {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.status-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style> 