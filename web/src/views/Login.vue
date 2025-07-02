<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-title">管理员登录</div>
      <el-form :model="form" @submit.prevent="onLogin">
        <el-form-item>
          <el-input v-model="form.phone" placeholder="手机号"></el-input>
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="form.password" 
            :type="showPassword ? 'text' : 'password'" 
            placeholder="密码"
          >
            <template #suffix>
              <el-icon 
                class="password-toggle" 
                @click="togglePassword"
                style="cursor: pointer;"
              >
                <View v-if="showPassword" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <div class="captcha-container">
            <el-input 
              v-model="form.captcha" 
              placeholder="验证码" 
              style="flex: 1; margin-right: 10px;"
              maxlength="4"
            ></el-input>
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
            </div>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onLogin" style="width:100%" :loading="loading">登录</el-button>
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
  background: #f7f8fa;
}
.login-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 16px #eee;
  padding: 48px 36px 36px 36px;
  min-width: 340px;
}
.login-title {
  font-size: 26px;
  font-weight: bold;
  color: #007AFF;
  text-align: center;
  margin-bottom: 32px;
  letter-spacing: 2px;
}
.password-toggle {
  color: #909399;
  font-size: 16px;
}
.password-toggle:hover {
  color: #409EFF;
}
.captcha-container {
  display: flex;
  align-items: center;
  gap: 10px;
}
.captcha-image-container {
  width: 120px;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.captcha-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.captcha-image:hover {
  opacity: 0.8;
}
.captcha-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #909399;
}
</style> 