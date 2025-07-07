<template>
  <el-container style="min-height:100vh;">
    <el-aside width="280px" class="sidebar">
      <div class="sidebar-header">
        <div class="logo-container">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" width="32" height="32">
              <path fill="currentColor" d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2M21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9M19 21H5V3H14V9H19Z"/>
            </svg>
          </div>
          <div class="logo-text">
            <div class="logo-title">智慧考勤</div>
            <div class="logo-subtitle">管理系统</div>
          </div>
        </div>
      </div>
      
      <el-menu 
        :default-active="$route.path" 
        router 
        class="sidebar-menu"
        :collapse="false"
      >
        <el-menu-item index="/" class="menu-item">
          <div class="menu-item-content">
            <svg class="menu-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"/>
            </svg>
            <span class="menu-text">仪表盘</span>
          </div>
        </el-menu-item>
        
        <el-menu-item index="/employees" class="menu-item">
          <div class="menu-item-content">
            <svg class="menu-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M16,4C18.21,4 20,5.79 20,8C20,10.21 18.21,12 16,12C13.79,12 12,10.21 12,8C12,5.79 13.79,4 16,4M16,14C20.42,14 24,15.79 24,18V20H8V18C8,15.79 11.58,14 16,14M6,6H8V4H6A2,2 0 0,0 4,6V8H6V6M4,18H6V16H4V18M4,14H6V12H4V14M4,10H6V8H4V10Z"/>
            </svg>
            <span class="menu-text">员工管理</span>
          </div>
        </el-menu-item>
        
        <el-menu-item index="/departments" class="menu-item">
          <div class="menu-item-content">
            <svg class="menu-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M12,5.5A3.5,3.5 0 0,1 15.5,9A3.5,3.5 0 0,1 12,12.5A3.5,3.5 0 0,1 8.5,9A3.5,3.5 0 0,1 12,5.5M5,8C5.56,8 6.08,8.15 6.53,8.42C6.38,9.85 6.8,11.27 7.66,12.38C7.16,13.34 6.16,14 5,14A3,3 0 0,1 2,11A3,3 0 0,1 5,8M19,8A3,3 0 0,1 22,11A3,3 0 0,1 19,14C17.84,14 16.84,13.34 16.34,12.38C17.2,11.27 17.62,9.85 17.47,8.42C17.92,8.15 18.44,8 19,8M5.5,18.25C5.5,16.18 8.41,14.5 12,14.5C15.59,14.5 18.5,16.18 18.5,18.25V20H5.5V18.25M0,20V18.5C0,17.11 1.89,15.94 4.45,15.6C3.86,16.28 3.5,17.22 3.5,18.25V20H0M24,20H20.5V18.25C20.5,17.22 20.14,16.28 19.55,15.6C22.11,15.94 24,17.11 24,18.5V20Z"/>
            </svg>
            <span class="menu-text">部门管理</span>
          </div>
        </el-menu-item>
        
        <el-menu-item index="/attendance" class="menu-item">
          <div class="menu-item-content">
            <svg class="menu-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M12,12H17V17H12V12Z"/>
            </svg>
            <span class="menu-text">考勤记录</span>
          </div>
        </el-menu-item>
        

        <el-menu-item index="/stats" class="menu-item">
          <div class="menu-item-content">
            <svg class="menu-icon" viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21M7,14A1,1 0 0,1 6,13V9A1,1 0 0,1 7,8H9A1,1 0 0,1 10,9V13A1,1 0 0,1 9,14H7M13,14A1,1 0 0,1 12,13V6A1,1 0 0,1 13,5H15A1,1 0 0,1 16,6V13A1,1 0 0,1 15,14H13M19,14A1,1 0 0,1 18,13V10A1,1 0 0,1 19,9H21A1,1 0 0,1 22,10V13A1,1 0 0,1 21,14H19Z"/>
            </svg>
            <span class="menu-text">统计分析</span>
          </div>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path fill="currentColor" d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
            </svg>
          </div>
          <span class="user-name">管理员</span>
        </div>
      </div>
    </el-aside>
    
    <el-container>
      <el-header class="main-header">
        <div class="header-left">
          <h1 class="page-title">智慧考勤管理系统</h1>
        </div>
        <div class="header-right">
          <el-button type="text" @click="logout" class="logout-btn">
            <svg class="logout-icon" viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M16,17V14H9V10H16V7L21,12L16,17M14,2A2,2 0 0,1 16,4V6H14V4H5V20H14V18H16V20A2,2 0 0,1 14,22H5A2,2 0 0,1 3,20V4A2,2 0 0,1 5,2H14Z"/>
            </svg>
            <span>退出登录</span>
          </el-button>
        </div>
      </el-header>
      <el-main class="main-content">
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
body { 
  margin: 0; 
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.sidebar {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
  border-right: 1px solid #e2e8f0;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent 0%, rgba(148, 163, 184, 0.2) 50%, transparent 100%);
  z-index: 1;
}

.sidebar-header {
  padding: 32px 24px 28px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.logo-text {
  flex: 1;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #334155 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
  margin: 0;
}

.logo-subtitle {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  margin-top: 2px;
  letter-spacing: 0.5px;
}

.sidebar-menu {
  background: transparent !important;
  border: none !important;
  padding: 16px 12px;
}

.menu-item {
  margin-bottom: 4px;
  border-radius: 12px !important;
  height: 48px !important;
  background: transparent !important;
  border: none !important;
  transition: all 0.3s ease !important;
  position: relative;
  overflow: hidden;
}

.menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.menu-item:hover::before {
  background: rgba(102, 126, 234, 0.08);
}

.menu-item.is-active::before {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
}

.menu-item-content {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 16px;
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
}

.menu-icon {
  color: #64748b;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.menu-item:hover .menu-icon {
  color: #667eea;
  transform: translateX(2px);
}

.menu-item.is-active .menu-icon {
  color: #667eea;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
  color: #475569 !important;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.menu-item:hover .menu-text {
  color: #334155 !important;
  transform: translateX(2px);
}

.menu-item.is-active .menu-text {
  color: #667eea !important;
  font-weight: 600;
}

/* 移除默认的Element Plus菜单样式 */
:deep(.el-menu-item) {
  color: transparent !important;
  background: transparent !important;
  border: none !important;
}

:deep(.el-menu-item:hover) {
  background: transparent !important;
  color: transparent !important;
}

:deep(.el-menu-item.is-active) {
  background: transparent !important;
  color: transparent !important;
}

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(226, 232, 240, 0.8);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-name {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}

.main-header {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  padding: 0 32px !important;
  height: 64px !important;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #334155 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logout-btn {
  display: flex !important;
  align-items: center;
  gap: 8px;
  padding: 8px 16px !important;
  border-radius: 8px !important;
  background: rgba(248, 113, 113, 0.1) !important;
  border: 1px solid rgba(248, 113, 113, 0.2) !important;
  color: #dc2626 !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.logout-btn:hover {
  background: rgba(248, 113, 113, 0.15) !important;
  border-color: rgba(248, 113, 113, 0.3) !important;
  transform: translateY(-1px);
}

.logout-icon {
  color: #dc2626;
}

.main-content {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #f8fafc 100%) !important;
  padding: 24px !important;
  min-height: calc(100vh - 64px);
}
</style> 