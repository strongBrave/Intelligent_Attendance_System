<template>
  <div style="padding:32px;">
    <!-- 搜索和操作区域 -->
    <div class="search-section">
      <div class="search-controls">
        <div class="search-input">
          <el-input
            v-model="searchKeyword"
            placeholder="请输入姓名或手机号搜索"
            @input="onSearchInput"
            @clear="onSearchClear"
            clearable
            style="width: 300px;"
            :prefix-icon="Search"
          />
        </div>
        
        <div class="sort-controls">
          <span class="sort-label">排序：</span>
          <el-select v-model="sortBy" @change="onSortChange" style="width: 120px; margin-right: 10px;">
            <el-option label="姓名" value="name" />
            <el-option label="手机号" value="phone" />
            <el-option label="部门" value="department" />
            <el-option label="角色" value="role" />
          </el-select>
          
          <el-button 
            :icon="sortOrder === 'asc' ? 'sort-up' : 'sort-down'"
            @click="toggleSortOrder"
            circle
            :type="sortOrder === 'asc' ? 'primary' : 'info'"
            size="small"
          >
            {{ sortOrder === 'asc' ? '↑' : '↓' }}
          </el-button>
        </div>
      </div>
      
      <el-button type="primary" @click="$router.push('/employees/new')" :icon="Plus">
        添加员工
      </el-button>
    </div>

    <!-- 统计信息 -->
    <div v-if="!loading" class="stats-bar">
      <span class="stats-text">
        共找到 <strong>{{ total }}</strong> 名员工
        <span v-if="searchKeyword" class="search-info">
          （搜索："{{ searchKeyword }}"）
        </span>
      </span>
    </div>

    <!-- 员工表格 -->
    <el-table :data="list" border stripe style="background:#fff; margin-top: 16px;" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" sortable/>
      <el-table-column prop="name" label="姓名" min-width="100" show-overflow-tooltip>
        <template #default="scope">
          <span class="name-cell">{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" min-width="120" show-overflow-tooltip/>
      <el-table-column prop="department" label="部门" min-width="100" show-overflow-tooltip>
        <template #default="scope">
          <el-tag 
            :type="scope.row.department === '未分配' ? 'warning' : 'success'"
            size="small"
          >
            {{ scope.row.department }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="role" label="角色" width="80">
        <template #default="scope">
          <el-tag 
            :type="scope.row.role === 'admin' ? 'danger' : 'primary'"
            size="small"
          >
            {{ scope.row.role === 'admin' ? '管理员' : '员工' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" @click="$router.push(`/employees/${scope.row.id}`)">
            编辑
          </el-button>
          <el-button size="small" type="danger" @click="onDelete(scope.row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 空状态 -->
    <el-empty 
      v-if="!loading && list.length === 0" 
      :description="searchKeyword ? '未找到匹配的员工' : '暂无员工数据'"
    >
      <el-button v-if="searchKeyword" type="primary" @click="clearSearch">
        清除搜索
      </el-button>
      <el-button v-else type="primary" @click="$router.push('/employees/new')">
        添加员工
      </el-button>
    </el-empty>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import api from '../api'

const list = ref([])
const loading = ref(false)
const total = ref(0)

// 搜索和排序相关
const searchKeyword = ref('')
const sortBy = ref('name')
const sortOrder = ref('asc')

let searchTimer = null

const getList = async () => {
  loading.value = true
  try {
    const params = {
      search: searchKeyword.value.trim(),
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    }
    
    const res = await api.get('/admin/users', { params })
    list.value = res.data.users || []
    total.value = res.data.total || 0
    console.log('获取到的用户列表:', list.value)
  } catch (error) {
    console.error('获取用户列表失败:', error)
    const errorMsg = error.response?.data?.msg || error.response?.data?.error || '获取用户列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 搜索输入处理（防抖）
const onSearchInput = () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(() => {
    getList()
  }, 500) // 500ms 防抖
}

// 清除搜索
const onSearchClear = () => {
  searchKeyword.value = ''
  getList()
}

// 清除搜索按钮
const clearSearch = () => {
  searchKeyword.value = ''
  getList()
}

// 排序变化处理
const onSortChange = () => {
  getList()
}

// 切换排序方向
const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  getList()
}

const onDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个员工吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete(`/admin/users/${id}`)
    ElMessage.success('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      const errorMsg = error.response?.data?.msg || error.response?.data?.error || '删除失败'
      ElMessage.error(errorMsg)
    }
  }
}

onMounted(getList)
</script>

<style scoped>
.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-controls {
  display: flex;
  align-items: center;
  gap: 24px;
}

.search-input {
  display: flex;
  align-items: center;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.stats-bar {
  padding: 12px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 6px;
  border-left: 4px solid #3b82f6;
  margin-bottom: 16px;
}

.stats-text {
  font-size: 14px;
  color: #374151;
}

.stats-text strong {
  color: #1f2937;
  font-weight: 600;
}

.search-info {
  color: #6b7280;
  font-style: italic;
}

.name-cell {
  font-weight: 500;
  color: #1f2937;
}

:deep(.el-table th) {
  background-color: #f8fafc !important;
  color: #374151;
  font-weight: 600;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #fafbfc;
}

:deep(.el-table__row:hover > td) {
  background-color: #f0f9ff !important;
}

:deep(.el-button) {
  font-weight: 500;
}

:deep(.el-tag) {
  font-weight: 500;
  border: none;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #d1d5db;
  transition: all 0.2s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #9ca3af;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #3b82f6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-controls {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .search-input .el-input {
    width: 100% !important;
  }
  
  .sort-controls {
    justify-content: center;
  }
}
</style> 