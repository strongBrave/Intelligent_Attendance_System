<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>考勤仪表盘</h1>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 总体统计卡片 -->
    <div class="summary-cards" v-if="summary">
      <el-card class="summary-card total-employees">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_employees }}</div>
            <div class="card-label">总员工数</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card attendance-rate">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.overall_attendance_rate }}%</div>
            <div class="card-label">出勤率</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card sign-in">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_sign_in }}</div>
            <div class="card-label">已签到</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card sign-out">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_sign_out }}</div>
            <div class="card-label">已签退</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card late">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_late }}</div>
            <div class="card-label">迟到</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card absent">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><Close /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_absent }}</div>
            <div class="card-label">缺勤</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card early-leave">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><ArrowDown /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_early_leave || 0 }}</div>
            <div class="card-label">早退</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card late-leave">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><ArrowRight /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_late_leave || 0 }}</div>
            <div class="card-label">晚退</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card not-signed-in">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_not_signed_in }}</div>
            <div class="card-label">未签到</div>
          </div>
        </div>
      </el-card>

      <el-card class="summary-card not-signed-out">
        <div class="card-content">
          <div class="card-icon">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-value">{{ summary.total_not_signed_out || 0 }}</div>
            <div class="card-label">未签退</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 部门考勤统计表格 -->
    <el-card class="department-stats-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><OfficeBuilding /></el-icon>
            部门考勤统计
          </span>
          <span class="card-subtitle">今日考勤数据</span>
        </div>
      </template>

      <el-table 
        :data="departments" 
        border 
        stripe 
        v-loading="loading"
        class="department-stats-table"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
      >
        <el-table-column prop="department.name" label="部门" width="150" fixed="left">
          <template #default="scope">
            <div class="department-name">
              <el-icon><OfficeBuilding /></el-icon>
              <el-button 
                link 
                type="primary" 
                @click="viewDepartmentDetail(scope.row.department.id)"
                class="department-link"
              >
                {{ scope.row.department.name }}
              </el-button>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="total_employees" label="总人数" width="100" align="center">
          <template #default="scope">
            <el-tag type="info" size="small">{{ scope.row.total_employees }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="sign_in_count" label="签到人数" width="120" align="center">
          <template #default="scope">
            <div class="stat-cell sign-in">
              <el-icon><Clock /></el-icon>
              <span>{{ scope.row.sign_in_count }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="sign_out_count" label="签退人数" width="120" align="center">
          <template #default="scope">
            <div class="stat-cell sign-out">
              <el-icon><Timer /></el-icon>
              <span>{{ scope.row.sign_out_count }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="late_count" label="迟到人数" width="120" align="center">
          <template #default="scope">
            <div class="stat-cell late">
              <el-icon><Warning /></el-icon>
              <span>{{ scope.row.late_count }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="absent_count" label="缺勤人数" width="120" align="center">
          <template #default="scope">
            <div class="stat-cell absent">
              <el-icon><Close /></el-icon>
              <span>{{ scope.row.absent_count }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="early_leave_count" label="早退人数" width="120" align="center">
          <template #default="scope">
            <div class="stat-cell early-leave">
              <el-icon><ArrowDown /></el-icon>
              <span>{{ scope.row.early_leave_count }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="late_leave_count" label="晚退人数" width="120" align="center">
          <template #default="scope">
            <div class="stat-cell late-leave">
              <el-icon><ArrowRight /></el-icon>
              <span>{{ scope.row.late_leave_count || 0 }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="not_signed_in_count" label="未签到" width="120" align="center">
          <template #default="scope">
            <div class="stat-cell not-signed-in">
              <el-icon><User /></el-icon>
              <span>{{ scope.row.not_signed_in_count }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="not_signed_out_count" label="未签退" width="120" align="center">
          <template #default="scope">
            <div class="stat-cell not-signed-out">
              <el-icon><CircleClose /></el-icon>
              <span>{{ scope.row.not_signed_out_count || 0 }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="attendance_rate" label="出勤率" width="120" align="center">
          <template #default="scope">
            <div class="attendance-rate-cell">
              <el-progress 
                :percentage="scope.row.attendance_rate" 
                :color="getProgressColor(scope.row.attendance_rate)"
                :stroke-width="8"
                :show-text="false"
              />
              <span class="rate-text">{{ scope.row.attendance_rate }}%</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              @click="viewDepartmentDetail(scope.row.department.id)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty 
        v-if="!loading && departments.length === 0" 
        description="暂无部门数据" 
        :image-size="120"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Refresh, User, TrendCharts, Clock, Timer, Warning, Close, 
  ArrowDown, ArrowRight, CircleClose, OfficeBuilding 
} from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const departments = ref([])
const summary = ref(null)

// 获取仪表盘数据
const fetchDashboardData = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/dashboard/stats')
    departments.value = response.data.departments || []
    summary.value = response.data.summary || {}
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    const errorMsg = error.response?.data?.error || '获取数据失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchDashboardData()
}

// 查看部门详情
const viewDepartmentDetail = (departmentId) => {
  router.push(`/departments/${departmentId}`)
}

// 根据出勤率获取进度条颜色
const getProgressColor = (rate) => {
  if (rate >= 90) return '#67C23A'  // 绿色
  if (rate >= 80) return '#E6A23C'  // 橙色
  if (rate >= 70) return '#F56C6C'  // 红色
  return '#909399'  // 灰色
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard-container {
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

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.summary-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  align-items: center;
  padding: 8px;
}

.card-icon {
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

.total-employees .card-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.attendance-rate .card-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.sign-in .card-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.sign-out .card-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.late .card-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.absent .card-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.early-leave .card-icon {
  background: linear-gradient(135deg, #ff6b6b 0%, #ffa8a8 100%);
}

.late-leave .card-icon {
  background: linear-gradient(135deg, #845ec2 0%, #b39ddb 100%);
}

.not-signed-in .card-icon {
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
}

.not-signed-out .card-icon {
  background: linear-gradient(135deg, #8A2BE2 0%, #9370DB 100%);
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.card-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.department-stats-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-subtitle {
  font-size: 14px;
  color: #909399;
  font-weight: 400;
}

.department-stats-table {
  margin-top: 16px;
}

.department-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #303133;
}

.stat-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 500;
}

.stat-cell.sign-in {
  color: #409EFF;
}

.stat-cell.sign-out {
  color: #67C23A;
}

.stat-cell.late {
  color: #E6A23C;
}

.stat-cell.absent {
  color: #F56C6C;
}

.stat-cell.early-leave {
  color: #F56C6C;
}

.stat-cell.late-leave {
  color: #845EC2;
}

.stat-cell.not-signed-in {
  color: #E6A23C;
}

.stat-cell.not-signed-out {
  color: #8A2BE2;
}

.attendance-rate-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rate-text {
  font-size: 12px;
  font-weight: 500;
  color: #606266;
  min-width: 35px;
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

:deep(.el-progress-bar__outer) {
  border-radius: 4px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}

</style> 