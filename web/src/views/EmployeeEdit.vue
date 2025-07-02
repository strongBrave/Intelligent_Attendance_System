<template>
  <div style="padding:32px;max-width:600px;margin:auto;">
    <el-card>
      <div style="font-size:20px;font-weight:bold;margin-bottom:24px;">{{isEdit ? '编辑员工' : '添加员工'}}</div>
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="姓名"></el-input>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="手机号"></el-input>
        </el-form-item>
        <el-form-item label="密码" v-if="!isEdit">
          <el-input v-model="form.password" type="password" placeholder="密码"></el-input>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="form.department_id" placeholder="选择部门" style="width: 100%;">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <!-- 人脸图片上传区域 -->
        <el-form-item label="人脸图片">
          <div class="face-upload-container">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
              :limit="5"
              multiple
              accept="image/*"
              list-type="picture-card"
              class="face-uploader"
              :show-file-list="true"
            >
              <el-icon><Plus /></el-icon>
              <template #tip>
                <div class="el-upload__tip">
                  支持jpg/png格式，最多上传5张图片，建议上传清晰的人脸正面照片
                </div>
              </template>
            </el-upload>
          </div>
          
          <!-- 图片预览 -->
          <div v-if="fileList.length > 0" class="face-preview">
            <div class="preview-title">已选择的图片 ({{fileList.length}}/5)</div>
            <div class="preview-list">
              <div 
                v-for="(file, index) in fileList" 
                :key="index" 
                class="preview-item"
              >
                <img :src="file.url" class="preview-image" />
                <div class="preview-actions">
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="removeFile(index)"
                    circle
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="onSubmit" :loading="loading">保存</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import api from '../api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isEdit = !!route.params.id
const loading = ref(false)
const uploadRef = ref()
const fileList = ref([])
const departments = ref([])

const form = ref({ 
  name: '',  // 姓名
  phone: '', 
  password: '', 
  department_id: null 
})

onMounted(async () => {
  // 获取部门列表
  try {
    const res = await api.get('/admin/departments')
    departments.value = res.data.departments || []
  } catch (error) {
    console.error('获取部门列表失败:', error)
  }
  
  if (isEdit) {
    try {
      const res = await api.get('/admin/users')
      const user = (res.data.users || []).find(u => u.id == route.params.id)
      if (user) {
        Object.assign(form.value, {
          name: user.name,  // 姓名
          phone: user.phone,
          department_id: user.department ? user.department.id : null
        })
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
})

// 处理文件选择
const handleFileChange = (file) => {
  // 验证文件类型
  const isImage = file.raw.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  
  // 验证文件大小 (5MB)
  const isLt5M = file.raw.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  
  // 创建预览URL
  file.url = URL.createObjectURL(file.raw)
  
  // 确保文件被添加到fileList中
  if (!fileList.value.find(f => f.uid === file.uid)) {
    fileList.value.push(file)
  }
  
  return true
}

// 处理文件移除
const handleFileRemove = (file) => {
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    // 释放预览URL
    if (fileList.value[index].url) {
      URL.revokeObjectURL(fileList.value[index].url)
    }
    fileList.value.splice(index, 1)
  }
}

// 移除文件
const removeFile = (index) => {
  // 释放预览URL
  if (fileList.value[index].url) {
    URL.revokeObjectURL(fileList.value[index].url)
  }
  fileList.value.splice(index, 1)
}

// 提交表单
const onSubmit = async () => {
  if (!form.value.name || !form.value.phone) {  // 检查姓名和手机号
    ElMessage.error('请填写完整信息')
    return
  }
  
  if (!isEdit && !form.value.password) {
    ElMessage.error('请设置密码')
    return
  }
  
  // 添加调试信息
  console.log('当前文件列表:', fileList.value)
  console.log('文件列表长度:', fileList.value.length)
  
  if (fileList.value.length === 0) {
    ElMessage.error('请至少上传一张人脸图片')
    return
  }
  
  loading.value = true
  
  try {
    if (isEdit) {
      // 编辑模式
      await api.put(`/admin/users/${route.params.id}`, form.value)
      
      // 如果上传了新的人脸图片，需要重新注册人脸
      if (fileList.value.length > 0) {
        await registerFaces(route.params.id)
      }
    } else {
      // 添加模式
      const userRes = await api.post('/admin/users', form.value)
      const userId = userRes.data.user.id
      
      // 注册人脸
      await registerFaces(userId)
    }
    
    ElMessage.success(isEdit ? '员工信息更新成功' : '员工添加成功')
    router.push('/employees')
  } catch (error) {
    console.error('保存失败:', error)
    const errorMsg = error.response?.data?.msg || error.response?.data?.error || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 注册人脸
const registerFaces = async (userId) => {
  try {
    if (fileList.value.length === 1) {
      // 单张图片，使用原来的API
      const formData = new FormData()
      formData.append('face_image', fileList.value[0].raw)
      formData.append('user_id', userId)
      
      const response = await api.post('/face/register_face', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.code === 0) {
        ElMessage.success('人脸注册成功')
      } else {
        throw new Error(response.data.msg)
      }
    } else {
      // 多张图片，使用新的API
      const formData = new FormData()
      formData.append('user_id', userId)
      
      fileList.value.forEach((file, index) => {
        formData.append('face_images', file.raw)
      })
      
      const response = await api.post('/face/register_multiple_faces', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.code === 0) {
        ElMessage.success(`人脸注册成功，处理了 ${response.data.data.valid_images} 张有效图片`)
      } else {
        throw new Error(response.data.msg)
      }
    }
  } catch (error) {
    console.error('人脸注册失败:', error)
    ElMessage.error(error.message || '人脸注册失败，请重试')
    throw error
  }
}
</script>

<style scoped>
.face-upload-container {
  width: 100%;
}

.face-uploader {
  width: 100%;
}

.face-preview {
  margin-top: 16px;
}

.preview-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
}

.preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.preview-item {
  position: relative;
  width: 120px;
  height: 120px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-actions {
  position: absolute;
  top: 4px;
  right: 4px;
}

:deep(.el-upload--picture-card) {
  width: 120px;
  height: 120px;
  line-height: 120px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 120px;
  height: 120px;
}
</style> 