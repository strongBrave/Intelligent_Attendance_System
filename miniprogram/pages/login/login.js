const app = getApp()

Page({
  data: {
    phone: '',
    password: '',
    captcha: '',
    loading: false,
    showPassword: false,
    captchaImage: '',
    captchaId: ''
  },

  onLoad() {
    this.getCaptcha()
  },

  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value
    })
  },

  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    })
  },

  onCaptchaInput(e) {
    this.setData({
      captcha: e.detail.value
    })
  },

  togglePassword() {
    this.setData({
      showPassword: !this.data.showPassword
    })
  },

  getCaptcha() {
    wx.request({
      url: `${app.globalData.baseUrl}/api/captcha`,
      method: 'GET',
      success: (res) => {
        if (res.data.captcha_image && res.data.captcha_id) {
          this.setData({
            captchaImage: res.data.captcha_image,
            captchaId: res.data.captcha_id
          })
        } else {
          wx.showToast({
            title: '获取验证码失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.showToast({
          title: '获取验证码失败',
          icon: 'none'
        })
      }
    })
  },

  refreshCaptcha() {
    this.setData({
      captcha: ''
    })
    this.getCaptcha()
  },

  onLogin() {
    const { phone, password, captcha, captchaId } = this.data
    
    if (!phone) {
      wx.showToast({
        title: '请输入手机号',
        icon: 'none'
      })
      return
    }
    
    if (!password) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      })
      return
    }

    if (!captcha) {
      wx.showToast({
        title: '请输入验证码',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    // 构建登录数据
    const loginData = {
      phone: phone,
      password: password,
      captcha_id: captchaId,
      captcha_text: captcha
    }

    // 发送登录请求
    wx.request({
      url: `${app.globalData.baseUrl}/api/login`,
      method: 'POST',
      data: loginData,
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.data.token) {
          // 保存token和用户信息
          wx.setStorageSync('token', res.data.token)
          wx.setStorageSync('userInfo', res.data.user)
          
          wx.showToast({
            title: '登录成功',
            icon: 'success'
          })
          
          // 跳转到打卡页面
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/attendance/attendance'
            })
          }, 1500)
        } else {
          wx.showToast({
            title: res.data.msg || '登录失败',
            icon: 'none'
          })
          // 登录失败时刷新验证码
          this.refreshCaptcha()
        }
      },
      fail: (err) => {
        console.error('登录失败:', err)
        wx.showToast({
          title: '登录失败，请检查网络',
          icon: 'none'
        })
        // 登录失败时刷新验证码
        this.refreshCaptcha()
      },
      complete: () => {
        this.setData({ loading: false })
      }
    })
  },

  onBackToLogin() {
    wx.navigateBack()
  },

  onForgotPassword() {
    wx.navigateTo({
      url: '/pages/forgot-password/forgot-password'
    })
  }
}) 