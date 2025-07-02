<template>
  <div style="padding:32px;">
    <el-button type="primary" @click="$router.push('/employees/new')" style="margin-bottom:20px;">添加员工</el-button>
    <el-table :data="list" border stripe style="background:#fff" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60"/>
      <el-table-column prop="name" label="姓名"/>
      <el-table-column prop="phone" label="手机号"/>
      <el-table-column prop="department" label="部门"/>
      <el-table-column prop="role" label="角色"/>
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" @click="$router.push(`/employees/${scope.row.id}`)">编辑</el-button>
          <el-button size="small" type="danger" @click="onDelete(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 空状态 -->
    <el-empty v-if="!loading && list.length === 0" description="暂无员工数据" />
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

const list = ref([])
const loading = ref(false)

const getList = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/users')
    list.value = res.data.users || []
    console.log('获取到的用户列表:', list.value)
  } catch (error) {
    console.error('获取用户列表失败:', error)
    const errorMsg = error.response?.data?.msg || error.response?.data?.error || '获取用户列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
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