<template>
  <div class="login-container">
    <div class="login-background">
      <div class="bg-decoration"></div>
      <div class="bg-decoration-2"></div>
    </div>
    <div class="login-card">
      <div class="login-header">
        <div class="login-icon">
          <svg viewBox="0 0 24 24" width="30" height="30">
            <path fill="currentColor" d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2M21 9V7L15 1H5C3.89 1 3 1.89 3 3V21C3 22.11 3.89 23 5 23H19C20.11 23 21 22.11 21 21V9M19 21H5V3H14V9H19Z"/>
          </svg>
        </div>
        <div class="login-text">
          <h1 class="login-title">考勤管理系统</h1>
          <p class="login-subtitle">管理员登录</p>
        </div>
      </div>
      
      <el-form :model="form" @submit.prevent="onLogin" class="login-form">
        <el-form-item>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M6.62,10.79C6.57,10.62 6.54,10.45 6.54,10.28C6.54,9.47 7.19,8.82 8,8.82C8.81,8.82 9.46,9.47 9.46,10.28C9.46,10.45 9.43,10.62 9.38,10.79L12,22H4L6.62,10.79M16.5,3C19,5 19,9 16.5,11C14,9 14,5 16.5,3Z"/>
            </svg>
            <el-input v-model="form.phone" placeholder="请输入手机号" class="styled-input"></el-input>
          </div>
        </el-form-item>
        
        <el-form-item>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
            </svg>
            <el-input 
              v-model="form.password" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="请输入密码"
              class="styled-input"
            >
              <template #suffix>
                <el-icon 
                  class="password-toggle" 
                  @click="togglePassword"
                >
                  <View v-if="showPassword" />
                  <Hide v-else />
                </el-icon>
              </template>
            </el-input>
          </div>
        </el-form-item>
        
        <el-form-item>
          <div class="captcha-wrapper">
            <div class="input-wrapper captcha-input">
              <svg class="input-icon" viewBox="0 0 24 24" width="18" height="18">
                <path fill="currentColor" d="M12,1A11,11 0 0,0 1,12A11,11 0 0,0 12,23A11,11 0 0,0 23,12A11,11 0 0,0 12,1M12,3A9,9 0 0,1 21,12A9,9 0 0,1 12,21A9,9 0 0,1 3,12A9,9 0 0,1 12,3M8,12A2,2 0 0,1 10,10A2,2 0 0,1 12,12A2,2 0 0,1 10,14A2,2 0 0,1 8,12M14,12A2,2 0 0,1 16,10A2,2 0 0,1 18,12A2,2 0 0,1 16,14A2,2 0 0,1 14,12Z"/>
              </svg>
              <el-input 
                v-model="form.captcha" 
                placeholder="验证码" 
                class="styled-input"
                maxlength="4"
              ></el-input>
            </div>
            <div class="captcha-image-container">
              <img 
                v-if="captchaImage" 
                :src="captchaImage" 
                alt="验证码" 
                class="captcha-image"
                @click="refreshCaptcha"
                title="点击刷新验证码"
              />
              <div v-else class="captcha-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
              </div>
              <div class="captcha-refresh" @click="refreshCaptcha">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path fill="currentColor" d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z"/>
                </svg>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="onLogin" 
            class="login-button"
            :loading="loading"
          >
            <span v-if="!loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Hide, Loading } from '@element-plus/icons-vue'
import api from '../api'
import { useRouter } from 'vue-router'

const router = useRouter()
const form = ref({ phone: '', password: '', captcha: '' })
const showPassword = ref(false)
const loading = ref(false)
const captchaImage = ref('')
const captchaId = ref('')

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const getCaptcha = async () => {
  try {
    const res = await api.get('/captcha')
    captchaImage.value = res.data.captcha_image
    captchaId.value = res.data.captcha_id
  } catch (error) {
    console.error('获取验证码失败:', error)
    ElMessage.error('获取验证码失败')
  }
}

const refreshCaptcha = () => {
  form.value.captcha = ''
  getCaptcha()
}

const onLogin = async () => {
  if (!form.value.phone || !form.value.password || !form.value.captcha) {
    ElMessage.error('请填写完整信息')
    return
  }

  loading.value = true
  try {
    const loginData = {
      phone: form.value.phone,
      password: form.value.password,
      captcha_id: captchaId.value,
      captcha_text: form.value.captcha
    }
    
    const res = await api.post('/login', loginData)
    if (res.data.token) {
      localStorage.setItem('token', res.data.token)
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error(res.data.msg || '登录失败')
      // 登录失败时刷新验证码
      refreshCaptcha()
    }
  } catch (e) {
    console.error('登录失败:', e)
    const errorMsg = e.response?.data?.msg || '登录失败'
    ElMessage.error(errorMsg)
    // 登录失败时刷新验证码
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  getCaptcha()
})
</script>
<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgba(238, 245, 255, 0.9) 0%, 
    rgba(247, 250, 255, 0.95) 50%, 
    rgba(255, 249, 245, 0.9) 100%);
  backdrop-filter: blur(10px);
}

.bg-decoration {
  position: absolute;
  top: -20%;
  left: -20%;
  width: 40%;
  height: 40%;
  background: radial-gradient(circle, rgba(168, 200, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.bg-decoration-2 {
  position: absolute;
  bottom: -20%;
  right: -20%;
  width: 60%;
  height: 60%;
  background: radial-gradient(circle, rgba(255, 218, 200, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 8s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 18px;
  box-shadow: 
    0 15px 30px rgba(0, 0, 0, 0.1),
    0 3px 9px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 24px 36px;
  width: 435px;
  position: relative;
  z-index: 10;
}

.login-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 24px;
}

.login-icon {
  width: 45px;
  height: 45px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}

.login-text {
  flex: 1;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 4px 0;
  letter-spacing: 0.5px;
  text-align: left;
}

.login-subtitle {
  color: #8892b0;
  font-size: 14px;
  margin: 0;
  font-weight: 400;
  text-align: left;
}

.login-form {
  margin-top: 18px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 16px;
  z-index: 2;
  color: #a8b2d1;
}

:deep(.styled-input .el-input__wrapper) {
  padding-left: 48px;
  height: 52px;
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid rgba(203, 213, 225, 0.5);
  box-shadow: none;
  transition: all 0.3s ease;
  width: 100%;
}

:deep(.styled-input .el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.9);
}

:deep(.styled-input .el-input__wrapper.is-focus) {
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

:deep(.styled-input .el-input__inner) {
  color: #334155;
  font-size: 15px;
}

:deep(.styled-input .el-input__inner::placeholder) {
  color: #94a3b8;
}

:deep(.styled-input) {
  width: 100%;
}

.password-toggle {
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.password-toggle:hover {
  color: #667eea;
}

.captcha-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-image-container {
  position: relative;
  width: 120px;
  height: 52px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid rgba(203, 213, 225, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.captcha-image-container:hover {
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-1px);
}

.captcha-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
}

.captcha-refresh {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  background: rgba(102, 126, 234, 0.9);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s ease;
}

.captcha-image-container:hover .captcha-refresh {
  opacity: 1;
}

.captcha-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #94a3b8;
}

.login-button {
  width: 100%;
  height: 52px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

:deep(.login-button.is-loading) {
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
}

/* 表单项间距 */
:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}
</style> 