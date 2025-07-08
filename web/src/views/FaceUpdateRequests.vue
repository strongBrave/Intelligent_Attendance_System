<template>
  <div class="face-requests-container">
    <div class="page-header">
      <h1>人脸更新申请审核</h1>
      <p>管理员可以在这里查看和处理用户提交的人脸更新申请</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card pending">
        <div class="stat-icon">⏳</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </div>
      <div class="stat-card approved">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.approved }}</div>
          <div class="stat-label">已通过</div>
        </div>
      </div>
      <div class="stat-card rejected">
        <div class="stat-icon">❌</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.rejected }}</div>
          <div class="stat-label">已拒绝</div>
        </div>
      </div>
      <div class="stat-card total">
        <div class="stat-icon">📋</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.total }}</div>
          <div class="stat-label">总申请</div>
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filters">
      <el-select v-model="currentStatus" @change="fetchRequests" placeholder="按状态筛选" clearable>
        <el-option label="全部" value=""></el-option>
        <el-option label="待审核" value="pending"></el-option>
        <el-option label="已通过" value="approved"></el-option>
        <el-option label="已拒绝" value="rejected"></el-option>
      </el-select>
      
      <el-button @click="fetchRequests" :loading="loading">
        <i class="el-icon-refresh"></i> 刷新
      </el-button>
    </div>

    <!-- 申请列表 -->
    <div class="requests-table">
      <el-table 
        :data="requests" 
        v-loading="loading"
        @row-click="showRequestDetail"
        style="cursor: pointer;"
      >
        <el-table-column prop="user_name" label="申请用户" width="120">
          <template #default="scope">
            <div class="user-info">
              <div class="user-name">{{ scope.row.user_name }}</div>
              <div class="user-phone">{{ scope.row.user_phone }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="department" label="部门" width="120" />
        
        <el-table-column prop="reason" label="申请原因" min-width="200">
          <template #default="scope">
            <div class="reason-text">{{ scope.row.reason }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag 
              :type="getStatusTagType(scope.row.status)"
              size="small"
            >
              {{ scope.row.status_text }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="scope">
            <div class="time-text">{{ formatTime(scope.row.created_at) }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="admin_name" label="处理人" width="100">
          <template #default="scope">
            <div class="admin-text">{{ scope.row.admin_name || '-' }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              @click.stop="showRequestDetail(scope.row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchRequests"
          @current-change="fetchRequests"
        />
      </div>
    </div>

    <!-- 申请详情弹窗 -->
    <el-dialog 
      v-model="showDetailDialog" 
      title="人脸更新申请详情"
      width="80%"
      :before-close="handleCloseDetail"
    >
      <div v-if="currentRequest" class="request-detail">
        <!-- 用户信息 -->
        <div class="detail-section">
          <h3>申请用户信息</h3>
          <div class="user-detail">
            <div class="detail-item">
              <label>姓名：</label>
              <span>{{ currentRequest.user.name }}</span>
            </div>
            <div class="detail-item">
              <label>手机号：</label>
              <span>{{ currentRequest.user.phone }}</span>
            </div>
            <div class="detail-item">
              <label>部门：</label>
              <span>{{ currentRequest.user.department }}</span>
            </div>
          </div>
        </div>

        <!-- 申请信息 -->
        <div class="detail-section">
          <h3>申请信息</h3>
          <div class="request-info">
            <div class="detail-item">
              <label>申请原因：</label>
              <span>{{ currentRequest.reason }}</span>
            </div>
            <div class="detail-item">
              <label>申请时间：</label>
              <span>{{ currentRequest.created_at }}</span>
            </div>
            <div class="detail-item">
              <label>当前状态：</label>
              <el-tag :type="getStatusTagType(currentRequest.status)">
                {{ currentRequest.status_text }}
              </el-tag>
            </div>
            <div class="detail-item" v-if="currentRequest.similarity_score !== null">
              <label>相似度：</label>
              <span :class="getSimilarityClass(currentRequest.similarity_score)">
                {{ (currentRequest.similarity_score * 100).toFixed(2) }}%
              </span>
            </div>
          </div>
        </div>

        <!-- 人脸照片对比 -->
        <div class="detail-section">
          <h3>人脸照片对比</h3>
          <div class="face-comparison">
            <div class="face-item">
              <h4>原照片</h4>
              <div class="face-image-container">
                <img 
                  v-if="currentRequest.old_face_url" 
                  :src="getImageUrl(currentRequest.old_face_url)" 
                  class="face-image"
                  @error="onImageError"
                />
                <div v-else class="no-image">暂无原照片</div>
              </div>
            </div>
            <div class="face-item">
              <h4>新照片</h4>
              <div class="face-image-container">
                <img 
                  v-if="currentRequest.new_face_url" 
                  :src="getImageUrl(currentRequest.new_face_url)" 
                  class="face-image"
                  @error="onImageError"
                />
                <div v-else class="no-image">暂无新照片</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 审核信息 -->
        <div class="detail-section" v-if="currentRequest.admin_comment">
          <h3>审核信息</h3>
          <div class="audit-info">
            <div class="detail-item">
              <label>处理人：</label>
              <span>{{ currentRequest.admin?.name || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>处理时间：</label>
              <span>{{ currentRequest.updated_at || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>审核备注：</label>
              <span>{{ currentRequest.admin_comment }}</span>
            </div>
          </div>
        </div>

        <!-- 审核操作 -->
        <div class="detail-section" v-if="currentRequest.status === 'pending'">
          <h3>审核操作</h3>
          <div class="audit-actions">
            <div class="comment-input">
              <label>审核备注：</label>
              <el-input
                v-model="auditComment"
                type="textarea"
                :rows="3"
                placeholder="请填写审核备注..."
                maxlength="500"
                show-word-limit
              />
            </div>
            <div class="action-buttons">
              <el-button 
                type="danger" 
                @click="rejectRequest"
                :loading="processing"
              >
                拒绝申请
              </el-button>
              <el-button 
                type="success" 
                @click="approveRequest"
                :loading="processing"
              >
                批准申请
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

export default {
  name: 'FaceUpdateRequests',
  setup() {
    const loading = ref(false)
    const processing = ref(false)
    const showDetailDialog = ref(false)
    
    const requests = ref([])
    const stats = reactive({
      total: 0,
      pending: 0,
      approved: 0,
      rejected: 0
    })
    
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    const currentStatus = ref('')
    
    const currentRequest = ref(null)
    const auditComment = ref('')

    // 获取申请列表
    const fetchRequests = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          per_page: pageSize.value
        }
        if (currentStatus.value) {
          params.status = currentStatus.value
        }

        const response = await api.get('/admin/face-update-requests', { params })
        
        requests.value = response.data.requests || []
        total.value = response.data.total || 0
      } catch (error) {
        console.error('获取申请列表失败:', error)
        ElMessage.error('获取申请列表失败')
      } finally {
        loading.value = false
      }
    }

    // 获取统计信息
    const fetchStats = async () => {
      try {
        const response = await api.get('/admin/face-update-requests/stats')
        Object.assign(stats, response.data.stats)
      } catch (error) {
        console.error('获取统计信息失败:', error)
      }
    }

    // 显示申请详情
    const showRequestDetail = async (request) => {
      try {
        const response = await api.get(`/admin/face-update-requests/${request.id}`)
        currentRequest.value = response.data.request
        auditComment.value = ''
        showDetailDialog.value = true
      } catch (error) {
        console.error('获取申请详情失败:', error)
        ElMessage.error('获取申请详情失败')
      }
    }

    // 批准申请
    const approveRequest = async () => {
      if (!currentRequest.value) return

      try {
        processing.value = true
        await api.put(`/admin/face-update-requests/${currentRequest.value.id}/approve`, {
          admin_comment: auditComment.value
        })
        
        ElMessage.success('申请已批准')
        showDetailDialog.value = false
        fetchRequests()
        fetchStats()
      } catch (error) {
        console.error('批准申请失败:', error)
        ElMessage.error(error.response?.data?.error || '批准申请失败')
      } finally {
        processing.value = false
      }
    }

    // 拒绝申请
    const rejectRequest = async () => {
      if (!currentRequest.value) return
      
      if (!auditComment.value.trim()) {
        ElMessage.error('拒绝申请时必须填写原因')
        return
      }

      try {
        await ElMessageBox.confirm('确定要拒绝这个申请吗？', '确认拒绝', {
          type: 'warning'
        })

        processing.value = true
        await api.put(`/admin/face-update-requests/${currentRequest.value.id}/reject`, {
          admin_comment: auditComment.value
        })
        
        ElMessage.success('申请已拒绝')
        showDetailDialog.value = false
        fetchRequests()
        fetchStats()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('拒绝申请失败:', error)
          ElMessage.error(error.response?.data?.error || '拒绝申请失败')
        }
      } finally {
        processing.value = false
      }
    }

    // 关闭详情弹窗
    const handleCloseDetail = () => {
      showDetailDialog.value = false
      currentRequest.value = null
      auditComment.value = ''
    }

    // 获取状态标签类型
    const getStatusTagType = (status) => {
      const typeMap = {
        pending: 'warning',
        approved: 'success',
        rejected: 'danger'
      }
      return typeMap[status] || 'info'
    }

    // 获取相似度样式类
    const getSimilarityClass = (score) => {
      if (score >= 0.9) return 'high-similarity'
      if (score >= 0.7) return 'medium-similarity'
      return 'low-similarity'
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      if (!timeStr) return '-'
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    // 获取图片URL
    const getImageUrl = (imagePath) => {
      if (!imagePath) return ''
      // 处理Windows路径分隔符问题
      const normalizedPath = imagePath.replace(/\\/g, '/')
      const filename = normalizedPath.split('/').pop()
      // 静态文件不使用API前缀，直接访问后端的静态文件路由
      return `http://localhost:5000/uploads/faces/${filename}`
    }

    // 图片加载错误处理
    const onImageError = (event) => {
      event.target.style.display = 'none'
      const nextElement = event.target.nextElementSibling
      if (nextElement) {
        nextElement.style.display = 'block'
      }
    }

    onMounted(() => {
      fetchRequests()
      fetchStats()
    })

    return {
      loading,
      processing,
      showDetailDialog,
      requests,
      stats,
      currentPage,
      pageSize,
      total,
      currentStatus,
      currentRequest,
      auditComment,
      fetchRequests,
      fetchStats,
      showRequestDetail,
      approveRequest,
      rejectRequest,
      handleCloseDetail,
      getStatusTagType,
      getSimilarityClass,
      formatTime,
      getImageUrl,
      onImageError
    }
  }
}
</script>

<style scoped>
.face-requests-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 36px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.stat-card.pending .stat-icon {
  background: rgba(255, 152, 0, 0.1);
}

.stat-card.approved .stat-icon {
  background: rgba(76, 175, 80, 0.1);
}

.stat-card.rejected .stat-icon {
  background: rgba(244, 67, 54, 0.1);
}

.stat-card.total .stat-icon {
  background: rgba(64, 158, 255, 0.1);
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 筛选器 */
.filters {
  background: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 表格 */
.requests-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.user-info {
  line-height: 1.4;
}

.user-name {
  font-weight: 600;
  color: #303133;
}

.user-phone {
  font-size: 12px;
  color: #909399;
}

.reason-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time-text, .admin-text {
  font-size: 13px;
  color: #606266;
}

.pagination {
  padding: 16px;
  display: flex;
  justify-content: center;
}

/* 详情弹窗 */
.request-detail {
  max-height: 80vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.detail-item {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.detail-item label {
  width: 100px;
  color: #606266;
  font-weight: 500;
  flex-shrink: 0;
}

.detail-item span {
  color: #303133;
  flex: 1;
}

/* 人脸照片对比 */
.face-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.face-item h4 {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
  text-align: center;
}

.face-image-container {
  width: 100%;
  height: 200px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.face-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-image {
  color: #909399;
  font-size: 14px;
}

/* 相似度样式 */
.high-similarity {
  color: #67c23a;
  font-weight: 600;
}

.medium-similarity {
  color: #e6a23c;
  font-weight: 600;
}

.low-similarity {
  color: #f56c6c;
  font-weight: 600;
}

/* 审核操作 */
.audit-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-input label {
  color: #606266;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style> 