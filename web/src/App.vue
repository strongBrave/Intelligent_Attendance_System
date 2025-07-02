<template>
  <el-container style="min-height:100vh;">
    <el-aside width="200px" style="background:#001529;">
      <div style="color:#fff;font-size:22px;text-align:center;padding:32px 0;letter-spacing:2px;">考勤后台</div>
      <el-menu :default-active="$route.path" router background-color="#001529" text-color="#fff" active-text-color="#409EFF" style="border:none">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/employees">员工管理</el-menu-item>
        <el-menu-item index="/departments">部门管理</el-menu-item>
        <el-menu-item index="/attendance">考勤管理</el-menu-item>
        <el-menu-item index="/attendance-settings">打卡时间设置</el-menu-item>
        <el-menu-item index="/stats">统计分析</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:#fff;box-shadow:0 2px 8px #f0f1f2;display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:20px;font-weight:bold;">智慧考勤系统</div>
        <el-button type="danger" @click="logout" size="small">退出登录</el-button>
      </el-header>
      <el-main style="background:#f7f8fa;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>
<style>
body { margin: 0; }
</style> 