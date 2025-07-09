<template>
  <div class="department-container">
    <el-card>
      <div class="header">
        <h2>部门管理</h2>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加部门
        </el-button>
      </div>

      <!-- 部门列表 -->
      <el-table :data="departments" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="部门名称" />
        <el-table-column label="打卡时间" width="280">
          <template #default="scope">
            <div class="time-info">
              <div class="time-grid">
                <div class="time-item">
                  <span class="time-label">签到:</span>
                  <span class="time-value">{{ scope.row.sign_in_time || '未设置' }}</span>
                </div>
                <div class="time-item">
                  <span class="time-label">签退:</span>
                  <span class="time-value">{{ scope.row.sign_out_time || '未设置' }}</span>
                </div>
                <div class="time-item">
                  <span class="time-label">迟到阈值:</span>
                  <span class="time-value">{{ scope.row.late_threshold || '未设置' }}</span>
                </div>
                <div class="time-item">
                  <span class="time-label">缺勤阈值:</span>
                  <span class="time-value">{{ scope.row.absent_threshold || '未设置' }}</span>
                </div>
                <div class="time-item">
                  <span class="time-label">早退阈值:</span>
                  <span class="time-value">{{ scope.row.early_leave_threshold || '未设置' }}</span>
                </div>
                <div class="time-item">
                  <span class="time-label">晚退阈值:</span>
                  <span class="time-value">{{ scope.row.late_leave_threshold || '未设置' }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="打卡位置" width="200">
          <template #default="scope">
            <div class="location-info" v-if="scope.row.location">
              <el-icon><Location /></el-icon>
              <span>{{ scope.row.location }}</span>
            </div>
            <span v-else class="no-location">未设置</span>
          </template>
        </el-table-column>
        <el-table-column label="距离阈值" width="120">
          <template #default="scope">
            <span>{{ scope.row.distance_threshold }}米</span>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="员工数量" width="120" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              @click="editDepartment(scope.row)"
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteDepartment(scope.row)"
              :disabled="scope.row.user_count > 0"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty v-if="!loading && departments.length === 0" description="暂无部门数据" />
    </el-card>

    <!-- 添加/编辑部门对话框 -->
    <el-dialog 
      :title="isEdit ? '编辑部门' : '添加部门'" 
      v-model="showAddDialog" 
      width="800px"
      @close="handleDialogClose"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="部门名称" prop="name">
          <el-input 
            v-model="form.name" 
            placeholder="请输入部门名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <!-- 打卡时间设置 -->
        <el-divider content-position="left">打卡时间设置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="签到时间" prop="sign_in_time">
              <el-time-picker
                v-model="form.sign_in_time"
                format="HH:mm"
                placeholder="选择签到时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="签退时间" prop="sign_out_time">
              <el-time-picker
                v-model="form.sign_out_time"
                format="HH:mm"
                placeholder="选择签退时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="迟到阈值" prop="late_threshold">
              <el-time-picker
                v-model="form.late_threshold"
                format="HH:mm"
                placeholder="选择迟到阈值"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="缺勤阈值" prop="absent_threshold">
              <el-time-picker
                v-model="form.absent_threshold"
                format="HH:mm"
                placeholder="选择缺勤阈值"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="早退阈值" prop="early_leave_threshold">
              <el-time-picker
                v-model="form.early_leave_threshold"
                format="HH:mm"
                placeholder="选择早退阈值"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="晚退阈值" prop="late_leave_threshold">
              <el-time-picker
                v-model="form.late_leave_threshold"
                format="HH:mm"
                placeholder="选择晚退阈值"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 打卡位置设置 -->
        <el-divider content-position="left">打卡位置设置</el-divider>
        
        <el-form-item label="打卡位置" prop="location">
          <div class="location-input">
            <el-input 
              v-model="form.location" 
              placeholder="请选择打卡位置"
              readonly
              style="flex: 1"
            />
            <el-button 
              type="primary" 
              @click="openMapPicker"
              style="margin-left: 10px"
            >
              <el-icon><Location /></el-icon>
              地图选点
            </el-button>
          </div>
          <div class="location-preview" v-if="form.location">
            <el-icon><Location /></el-icon>
            <span>{{ form.location }}</span>
          </div>
        </el-form-item>

        <el-form-item label="距离阈值" prop="distance_threshold">
          <el-input-number
            v-model="form.distance_threshold"
            :min="10"
            :max="1000"
            :step="10"
            style="width: 200px"
          />
          <span style="margin-left: 10px; color: #909399;">米</span>
          <div class="form-tip">员工必须在此距离范围内才能打卡成功</div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ isEdit ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 地图选点弹窗 -->
    <el-dialog 
      title="选择打卡位置" 
      v-model="showMapDialog" 
      width="900px"
      :close-on-click-modal="false"
    >
      <div class="map-container">
        <!-- 搜索框 -->
        <div class="map-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索地点，如：天安门、北京站等"
            class="search-input"
            @keyup.enter="searchPlace"
          >
            <template #append>
              <el-button @click="searchPlace" :loading="searching">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </template>
          </el-input>
          
          <!-- 搜索结果 -->
          <div class="search-results" v-if="searchResults.length > 0">
            <div 
              class="search-result-item"
              v-for="(result, index) in searchResults"
              :key="result.id"
              @click="selectSearchResult(result)"
            >
              <div class="result-name">{{ result.name }}</div>
              <div class="result-address">{{ result.address }}</div>
              <div class="result-distance" v-if="result.distance">{{ result.distance }}米</div>
            </div>
          </div>
        </div>
        
        <div id="map" class="map"></div>
        <div class="map-tips">
          <p>点击地图选择打卡位置，或搜索地址</p>
          <p v-if="selectedLocation">已选择: {{ selectedLocation }}</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showMapDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmLocation">确认位置</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Location, Search } from '@element-plus/icons-vue'
import api from '../api'

const loading = ref(false)
const submitting = ref(false)
const showAddDialog = ref(false)
const showMapDialog = ref(false)
const isEdit = ref(false)
const departments = ref([])
const formRef = ref()
let map = null
let marker = null
let selectedLocation = null
let searchKeyword = ref('')
let searchResults = ref([])
let searching = ref(false)

const form = ref({
  name: '',
  sign_in_time: null,
  sign_out_time: null,
  late_threshold: null,
  absent_threshold: null,
  early_leave_threshold: null,
  late_leave_threshold: null,
  location: '',
  distance_threshold: 100
})

const rules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '部门名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  sign_in_time: [
    { required: true, message: '请选择签到时间', trigger: 'change' }
  ],
  sign_out_time: [
    { required: true, message: '请选择签退时间', trigger: 'change' }
  ],
  distance_threshold: [
    { required: true, message: '请设置距离阈值', trigger: 'blur' }
  ]
}

// 获取部门列表
const fetchDepartments = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/departments')
    departments.value = response.data.departments || []
    
    // 调试信息：检查数据结构
    console.log('部门数据:', departments.value)
    if (departments.value.length > 0) {
      console.log('第一个部门的数据:', departments.value[0])
      console.log('晚退阈值字段:', departments.value[0].late_leave_threshold)
    }
  } catch (error) {
    console.error('获取部门列表失败:', error)
    const errorMsg = error.response?.data?.msg || error.response?.data?.error || '获取部门列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 添加部门
const addDepartment = async () => {
  submitting.value = true
  try {
    const submitData = {
      name: form.value.name,
      sign_in_time: formatTime(form.value.sign_in_time),
      sign_out_time: formatTime(form.value.sign_out_time),
      late_threshold: formatTime(form.value.late_threshold),
      absent_threshold: formatTime(form.value.absent_threshold),
      early_leave_threshold: formatTime(form.value.early_leave_threshold),
      late_leave_threshold: formatTime(form.value.late_leave_threshold),
      location: form.value.location,
      distance_threshold: form.value.distance_threshold
    }
    
    await api.post('/admin/departments', submitData)
    ElMessage.success('部门添加成功')
    showAddDialog.value = false
    resetForm()
    fetchDepartments()
  } catch (error) {
    console.error('添加部门失败:', error)
    const errorMsg = error.response?.data?.msg || error.response?.data?.error || '添加部门失败'
    ElMessage.error(errorMsg)
  } finally {
    submitting.value = false
  }
}

// 编辑部门
const editDepartment = (department) => {
  isEdit.value = true
  form.value = {
    id: department.id,
    name: department.name,
    sign_in_time: parseTime(department.sign_in_time),
    sign_out_time: parseTime(department.sign_out_time),
    late_threshold: parseTime(department.late_threshold),
    absent_threshold: parseTime(department.absent_threshold),
    early_leave_threshold: parseTime(department.early_leave_threshold),
    late_leave_threshold: parseTime(department.late_leave_threshold),
    location: department.location || '',
    distance_threshold: department.distance_threshold || 100
  }
  showAddDialog.value = true
}

// 更新部门
const updateDepartment = async () => {
  submitting.value = true
  try {
    const submitData = {
      name: form.value.name,
      sign_in_time: formatTime(form.value.sign_in_time),
      sign_out_time: formatTime(form.value.sign_out_time),
      late_threshold: formatTime(form.value.late_threshold),
      absent_threshold: formatTime(form.value.absent_threshold),
      early_leave_threshold: formatTime(form.value.early_leave_threshold),
      late_leave_threshold: formatTime(form.value.late_leave_threshold),
      location: form.value.location,
      distance_threshold: form.value.distance_threshold
    }
    
    await api.put(`/admin/departments/${form.value.id}`, submitData)
    ElMessage.success('部门更新成功')
    showAddDialog.value = false
    resetForm()
    fetchDepartments()
  } catch (error) {
    console.error('更新部门失败:', error)
    const errorMsg = error.response?.data?.msg || error.response?.data?.error || '更新部门失败'
    ElMessage.error(errorMsg)
  } finally {
    submitting.value = false
  }
}

// 删除部门
const deleteDepartment = async (department) => {
  if (department.user_count > 0) {
    ElMessage.warning('该部门下还有员工，无法删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除部门 "${department.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.delete(`/admin/departments/${department.id}`)
    ElMessage.success('部门删除成功')
    fetchDepartments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除部门失败:', error)
      const errorMsg = error.response?.data?.msg || error.response?.data?.error || '删除部门失败'
      ElMessage.error(errorMsg)
    }
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    if (isEdit.value) {
      await updateDepartment()
    } else {
      await addDepartment()
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  form.value = {
    name: '',
    sign_in_time: null,
    sign_out_time: null,
    late_threshold: null,
    absent_threshold: null,
    early_leave_threshold: null,
    late_leave_threshold: null,
    location: '',
    distance_threshold: 100
  }
  isEdit.value = false
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 监听对话框关闭
const handleDialogClose = () => {
  resetForm()
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return null
  const hours = time.getHours().toString().padStart(2, '0')
  const minutes = time.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// 解析时间字符串
const parseTime = (timeStr) => {
  if (!timeStr) return null
  const [hours, minutes] = timeStr.split(':').map(Number)
  const date = new Date()
  date.setHours(hours, minutes, 0, 0)
  return date
}

// 打开地图选点
const openMapPicker = () => {
  showMapDialog.value = true
  nextTick(() => {
    initMap()
  })
}

// 初始化地图
const initMap = () => {
  // 高德地图API Key
  const apiKey = '734274af737d9f10deb2b7733964e2a3'
  
  // 动态加载高德地图SDK
  if (typeof AMap === 'undefined') {
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=1.4.15&key=${apiKey}&plugin=AMap.Geocoder,AMap.PlaceSearch`
    script.onload = () => {
      createMap()
    }
    document.head.appendChild(script)
  } else {
    createMap()
  }
}

// 创建地图
const createMap = () => {
  try {
    // 创建地图实例
    map = new AMap.Map('map', {
      zoom: 15,
      center: [116.397428, 39.90923] // 默认北京
    })

    // 添加点击事件
    map.on('click', (e) => {
      const lnglat = e.lnglat
      
      // 清除之前的标记
      if (marker) {
        map.remove(marker)
      }
      
      // 添加新标记
      marker = new AMap.Marker({
        position: lnglat,
        map: map
      })
      
      // 获取地址信息
      getAddressFromCoords(lnglat.lat, lnglat.lng)
    })

    console.log('地图初始化完成')
  } catch (error) {
    console.error('地图初始化失败:', error)
    ElMessage.error('地图加载失败，请检查网络连接')
  }
}

// 根据坐标获取地址
const getAddressFromCoords = async (lat, lng) => {
  try {
    // TODO: 请替换为您的Web服务API Key
    // 当前Key为JS API Key，无法用于Web服务API
    const apiKey = '5c3066c36f6fa333afc7f55f78c33ff0'  // 需要替换为实际的Web服务API Key
    
         // API Key已配置，继续调用高德API
    
    const response = await fetch(`https://restapi.amap.com/v3/geocode/regeo?key=${apiKey}&location=${lng},${lat}&poitype=&radius=1000&extensions=all&batch=false&roadlevel=0`)
    const data = await response.json()
    
    console.log('高德API响应:', data) // 调试信息
    
    if (data && data.status === '1' && data.regeocode) {
      const regeocode = data.regeocode
      let address = regeocode.formatted_address || ''
      
      // 如果没有formatted_address，尝试组合地址
      if (!address && regeocode.addressComponent) {
        const addr = regeocode.addressComponent
        const addressParts = [
          addr.province || '',
          addr.city || '',
          addr.district || '',
          addr.township || '',
          addr.streetNumber?.street || '',
          addr.streetNumber?.number || ''
        ]
        address = addressParts.filter(part => part).join('')
      }
      
      selectedLocation = `${lat},${lng} (${address || '经纬度坐标'})`
    } else {
      console.log('高德API错误:', data?.info || '未知错误')
      selectedLocation = `${lat},${lng} (经纬度坐标)`
    }
  } catch (error) {
    console.error('获取地址失败:', error)
    selectedLocation = `${lat},${lng} (经纬度坐标)`
  }
}

// 搜索地点
const searchPlace = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  // TODO: 请替换为您的Web服务API Key
  const apiKey = '5c3066c36f6fa333afc7f55f78c33ff0'  // 需要替换为实际的Web服务API Key
  
     // API Key已配置，继续调用高德API

  searching.value = true
  console.log('开始搜索:', searchKeyword.value)
  
  try {
    // 使用高德地图API搜索地点
    const url = `https://restapi.amap.com/v3/place/text?key=${apiKey}&keywords=${encodeURIComponent(searchKeyword.value)}&types=&city=&citylimit=false&children=1&offset=10&page=1&extensions=all`
    console.log('请求URL:', url)
    
    const response = await fetch(url)
    const data = await response.json()
    
    console.log('高德搜索响应:', data)
    
    if (data && data.status === '1' && data.pois && data.pois.length > 0) {
      searchResults.value = data.pois.map(place => {
        const [lng, lat] = place.location.split(',')
        return {
          id: place.id,
          name: place.name,
          address: place.address || place.pname + place.cityname + place.adname,
          location: `${lat},${lng}`, // 转换为纬度,经度格式
          distance: place.distance || null
        }
      })
      console.log('搜索结果:', searchResults.value)
    } else {
      console.log('搜索失败，API响应:', data)
      ElMessage.warning(data?.info || '未找到相关地点')
      searchResults.value = []
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请重试')
  } finally {
    searching.value = false
  }
}

// 选择搜索结果
const selectSearchResult = (result) => {
  const [lat, lng] = result.location.split(',').map(Number)
  // 清除之前的标记
  if (marker) {
    map.remove(marker)
  }
  // 添加新标记
  marker = new AMap.Marker({
    position: [lng, lat],
    map: map
  })
  // 设置地图中心
  map.setCenter([lng, lat])
  // 更新已选位置
  selectedLocation = `${lat},${lng} (${result.address})`
}

// 确认位置选择
const confirmLocation = () => {
  if (selectedLocation) {
    form.value.location = selectedLocation
    showMapDialog.value = false
    ElMessage.success('位置选择成功')
  } else {
    ElMessage.warning('请先选择位置')
  }
}

onMounted(() => {
  fetchDepartments()
})
</script>

<style scoped>
.department-container {
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

.time-info {
  font-size: 12px;
  color: #606266;
}

.time-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
  padding: 4px 0;
}

.time-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2px 8px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #e6f3ff;
  min-height: 24px;
}

.time-item:nth-child(odd) {
  border-left-color: #409eff;
}

.time-item:nth-child(even) {
  border-left-color: #67c23a;
}

.time-label {
  color: #606266;
  font-weight: 500;
  font-size: 11px;
  white-space: nowrap;
}

.time-value {
  color: #303133;
  font-weight: 600;
  font-size: 12px;
  margin-left: 8px;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #409EFF;
  font-size: 12px;
}

.no-location {
  color: #909399;
  font-size: 12px;
}

.location-input {
  display: flex;
  align-items: center;
}

.location-preview {
  margin-top: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #409EFF;
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-size: 12px;
}

.map-container {
  position: relative;
}

.map {
  width: 100%;
  height: 400px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.map-tips {
  margin-top: 10px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-empty) {
  margin-top: 40px;
}

:deep(.el-time-picker) {
  width: 100%;
}

.map-search {
  margin-bottom: 10px;
}

.search-input {
  width: 100%;
}

.search-results {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  margin-top: 5px;
}

.search-result-item {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.search-result-item:hover {
  background-color: #f5f7fa;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-name {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.result-address {
  font-size: 12px;
  color: #606266;
  margin-bottom: 2px;
}

.result-distance {
  font-size: 12px;
  color: #909399;
}
</style> 