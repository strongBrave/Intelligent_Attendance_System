<template>
  <div class="attendance-settings-container">
    <el-card>
      <div class="header">
        <h2>打卡时间设置</h2>
        <el-button type="primary" @click="refreshSettings">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <!-- 部门选择 -->
      <div class="department-selector">
        <el-select 
          v-model="selectedDepartmentId" 
          placeholder="请选择部门" 
          @change="onDepartmentChange"
          style="width: 300px;"
        >
          <el-option
            v-for="dept in departments"
            :key="dept.id"
            :label="dept.name"
            :value="dept.id"
          />
        </el-select>
      </div>

      <!-- 打卡时间设置表单 -->
      <div v-if="selectedDepartmentId" class="settings-form">
        <el-form 
          :model="settings" 
          :rules="rules" 
          ref="formRef" 
          label-width="120px"
          class="settings-form-content"
        >
          <el-form-item label="签到时间" prop="sign_in_time">
            <el-time-picker
              v-model="settings.sign_in_time"
              format="HH:mm"
              placeholder="选择签到时间"
              style="width: 200px;"
            />
            <div class="form-tip">员工应该在此时间前签到</div>
          </el-form-item>

          <el-form-item label="签退时间" prop="sign_out_time">
            <el-time-picker
              v-model="settings.sign_out_time"
              format="HH:mm"
              placeholder="选择签退时间"
              style="width: 200px;"
            />
            <div class="form-tip">员工应该在此时间后签退</div>
          </el-form-item>

          <el-form-item label="迟到阈值" prop="late_threshold">
            <el-time-picker
              v-model="settings.late_threshold"
              format="HH:mm"
              placeholder="选择迟到阈值"
              style="width: 200px;"
            />
            <div class="form-tip">超过此时间签到算作迟到</div>
          </el-form-item>

          <el-form-item label="缺勤阈值" prop="absent_threshold">
            <el-time-picker
              v-model="settings.absent_threshold"
              format="HH:mm"
              placeholder="选择缺勤阈值"
              style="width: 200px;"
            />
            <div class="form-tip">超过此时间签到算作缺勤</div>
          </el-form-item>

          <el-form-item label="早退阈值" prop="early_leave_threshold">
            <el-time-picker
              v-model="settings.early_leave_threshold"
              format="HH:mm"
              placeholder="选择早退阈值"
              style="width: 200px;"
            />
            <div class="form-tip">早于此时间签退算作早退</div>
          </el-form-item>

          <el-form-item label="晚退阈值" prop="late_leave_threshold">
            <el-time-picker
              v-model="settings.late_leave_threshold"
              format="HH:mm"
              placeholder="选择晚退阈值"
              style="width: 200px;"
            />
            <div class="form-tip">超过此时间签退算作晚退</div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveSettings" :loading="saving">
              保存设置
            </el-button>
            <el-button @click="resetSettings">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 时间规则说明 -->
      <div v-if="selectedDepartmentId" class="rules-explanation">
        <el-alert
          title="时间规则说明"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="rules-content">
              <p><strong>正常签到：</strong>在签到时间前完成签到</p>
              <p><strong>迟到：</strong>在签到时间后、迟到阈值前完成签到</p>
              <p><strong>缺勤：</strong>在迟到阈值后、缺勤阈值前完成签到</p>
              <p><strong>正常签退：</strong>在签退时间后、晚退阈值前完成签退</p>
              <p><strong>早退：</strong>在早退阈值前完成签退</p>
              <p><strong>晚退：</strong>在晚退阈值后完成签退</p>
            </div>
          </template>
        </el-alert>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="!selectedDepartmentId" description="请选择部门进行设置" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import api from '../api'

const loading = ref(false)
const saving = ref(false)
const selectedDepartmentId = ref(null)
const departments = ref([])
const settings = ref({
  sign_in_time: null,
  sign_out_time: null,
  late_threshold: null,
  absent_threshold: null,
  early_leave_threshold: null,
  late_leave_threshold: null
})
const formRef = ref()

// 表单验证规则
const rules = {
  sign_in_time: [
    { required: true, message: '请选择签到时间', trigger: 'change' }
  ],
  sign_out_time: [
    { required: true, message: '请选择签退时间', trigger: 'change' }
  ],
  late_threshold: [
    { required: true, message: '请选择迟到阈值', trigger: 'change' }
  ],
  absent_threshold: [
    { required: true, message: '请选择缺勤阈值', trigger: 'change' }
  ],
  early_leave_threshold: [
    { required: true, message: '请选择早退阈值', trigger: 'change' }
  ],
  late_leave_threshold: [
    { required: true, message: '请选择晚退阈值', trigger: 'change' }
  ]
}

// 获取部门列表
const fetchDepartments = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/departments')
    departments.value = response.data.departments || []
  } catch (error) {
    console.error('获取部门列表失败:', error)
    const errorMsg = error.response?.data?.msg || error.response?.data?.error || '获取部门列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 获取部门打卡时间设置
const fetchDepartmentSettings = async (departmentId) => {
  try {
    const response = await api.get(`/admin/departments/${departmentId}/attendance-settings`)
    const settingsData = response.data.settings
    
    // 将时间字符串转换为Date对象
    settings.value = {
      sign_in_time: parseTimeString(settingsData.sign_in_time),
      sign_out_time: parseTimeString(settingsData.sign_out_time),
      late_threshold: parseTimeString(settingsData.late_threshold),
      absent_threshold: parseTimeString(settingsData.absent_threshold),
      early_leave_threshold: parseTimeString(settingsData.early_leave_threshold),
      late_leave_threshold: parseTimeString(settingsData.late_leave_threshold)
    }
  } catch (error) {
    console.error('获取打卡时间设置失败:', error)
    const errorMsg = error.response?.data?.msg || error.response?.data?.error || '获取打卡时间设置失败'
    ElMessage.error(errorMsg)
  }
}

// 解析时间字符串为Date对象
const parseTimeString = (timeStr) => {
  if (!timeStr) return null
  const [hours, minutes] = timeStr.split(':').map(Number)
  const date = new Date()
  date.setHours(hours, minutes, 0, 0)
  return date
}

// 格式化Date对象为时间字符串
const formatTimeString = (date) => {
  if (!date) return null
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// 部门选择变化
const onDepartmentChange = (departmentId) => {
  if (departmentId) {
    fetchDepartmentSettings(departmentId)
  } else {
    settings.value = {
      sign_in_time: null,
      sign_out_time: null,
      late_threshold: null,
      absent_threshold: null,
      early_leave_threshold: null,
      late_leave_threshold: null
    }
  }
}

// 保存设置
const saveSettings = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    saving.value = true
    
    // 将Date对象转换为时间字符串
    const settingsData = {
      sign_in_time: formatTimeString(settings.value.sign_in_time),
      sign_out_time: formatTimeString(settings.value.sign_out_time),
      late_threshold: formatTimeString(settings.value.late_threshold),
      absent_threshold: formatTimeString(settings.value.absent_threshold),
      early_leave_threshold: formatTimeString(settings.value.early_leave_threshold),
      late_leave_threshold: formatTimeString(settings.value.late_leave_threshold)
    }
    
    await api.put(`/admin/departments/${selectedDepartmentId.value}/attendance-settings`, settingsData)
    
    ElMessage.success('打卡时间设置保存成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('保存设置失败:', error)
      const errorMsg = error.response?.data?.msg || error.response?.data?.error || '保存设置失败，请稍后重试'
      ElMessage.error(errorMsg)
    }
  } finally {
    saving.value = false
  }
}

// 重置设置
const resetSettings = () => {
  if (selectedDepartmentId.value) {
    fetchDepartmentSettings(selectedDepartmentId.value)
  }
}

// 刷新设置
const refreshSettings = () => {
  fetchDepartments()
  if (selectedDepartmentId.value) {
    fetchDepartmentSettings(selectedDepartmentId.value)
  }
}

onMounted(() => {
  fetchDepartments()
})
</script>

<style scoped>
.attendance-settings-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #303133;
}

.department-selector {
  margin-bottom: 30px;
}

.settings-form {
  margin-bottom: 30px;
}

.settings-form-content {
  max-width: 600px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.rules-explanation {
  margin-top: 30px;
}

.rules-content p {
  margin: 5px 0;
  font-size: 14px;
}

.rules-content strong {
  color: #409EFF;
}

:deep(.el-time-picker) {
  width: 200px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style> 