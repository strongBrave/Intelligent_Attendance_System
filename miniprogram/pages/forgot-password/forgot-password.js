const app = getApp()

Page({
  data: {
    currentStep: 1,
    phone: '',
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    userName: '',
    loading: false,
    showOldPassword: false,
    showPassword: false,
    showConfirmPassword: false
  },

  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value
    })
  },

  onOldPasswordInput(e) {
    this.setData({
      oldPassword: e.detail.value
    })
  },

  onNewPasswordInput(e) {
    this.setData({
      newPassword: e.detail.value
    })
  },

  onConfirmPasswordInput(e) {
    this.setData({
      confirmPassword: e.detail.value
    })
  },

  toggleOldPassword() {
    this.setData({
      showOldPassword: !this.data.showOldPassword
    })
  },

  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword
    })
  },

  toggleConfirmPassword() {
    this.setData({
      showConfirmPassword: !this.data.showConfirmPassword
    })
  },

  // 验证手机号格式
  validatePhone(phone) {
    const phoneRegex = /^1[3-9]\d{9}$/
    return phoneRegex.test(phone)
  },

  // 验证密码强度
  validatePassword(password) {
    if (password.length < 6) {
      return false, '密码长度至少6位'
    }
    if (!/[a-zA-Z]/.test(password)) {
      return false, '密码必须包含字母'
    }
    if (!/\d/.test(password)) {
      return false, '密码必须包含数字'
    }
    return true, '密码强度符合要求'
  },

  // 步骤1：验证原密码
  onVerifyOldPassword() {
    const { phone, oldPassword } = this.data
    
    if (!phone) {
      wx.showToast({
        title: '请输入手机号',
        icon: 'none'
      })
      return
    }
    
    if (!this.validatePhone(phone)) {
      wx.showToast({
        title: '手机号格式不正确',
        icon: 'none'
      })
      return
    }
    
    if (!oldPassword) {
      wx.showToast({
        title: '请输入原密码',
        icon: 'none'
      })
      return
    }
    
    this.setData({ loading: true })
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/verify-old-password`,
      method: 'POST',
      data: {
        phone: phone,
        old_password: oldPassword
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            currentStep: 2,
            userName: res.data.user_name,
            loading: false
          })
          wx.showToast({
            title: '验证成功',
            icon: 'success'
          })
        } else {
          wx.showToast({
            title: res.data.msg || '验证失败',
            icon: 'none'
          })
          this.setData({ loading: false })
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
        this.setData({ loading: false })
      }
    })
  },

  // 步骤2：重置密码
  onResetPassword() {
    const { newPassword, confirmPassword, phone } = this.data
    
    if (!newPassword || !confirmPassword) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      })
      return
    }
    
    if (newPassword !== confirmPassword) {
      wx.showToast({
        title: '两次输入的密码不一致',
        icon: 'none'
      })
      return
    }
    
    const [isValid, message] = this.validatePassword(newPassword)
    if (!isValid) {
      wx.showToast({
        title: message,
        icon: 'none'
      })
      return
    }
    
    this.setData({ loading: true })
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/reset-password`,
      method: 'POST',
      data: {
        phone: phone,
        new_password: newPassword,
        confirm_password: confirmPassword
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({
            title: '密码重置成功',
            icon: 'success'
          })
          
          // 延迟跳转到登录页面
          setTimeout(() => {
            wx.navigateBack()
          }, 1500)
        } else {
          wx.showToast({
            title: res.data.msg || '重置失败',
            icon: 'none'
          })
        }
        this.setData({ loading: false })
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        })
        this.setData({ loading: false })
      }
    })
  },

  // 返回登录页面
  onBackToLogin() {
    wx.navigateBack()
  }
}) 