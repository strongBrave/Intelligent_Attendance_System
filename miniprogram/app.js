// app.js
App({
  globalData: {
    baseUrl: 'http://localhost:5000', // 本地测试
    userInfo: null,
    token: null
  },

  onLaunch() {
    // 检查登录状态
    this.checkLoginStatus()
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
    }
  },

  // 登录
  login(phone, password) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.baseUrl}/api/login`,
        method: 'POST',
        data: {
          phone: phone,
          password: password
        },
        success: (res) => {
          // 只要有token和user就判定登录成功
          if (res.data.token && res.data.user) {
            const { token, user } = res.data
            this.globalData.token = token
            this.globalData.userInfo = user
            // 保存到本地存储
            wx.setStorageSync('token', token)
            wx.setStorageSync('userInfo', user)
            resolve(res.data)
          } else {
            reject(new Error(res.data.msg || res.data.message || '登录失败'))
          }
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  // 登出
  logout() {
    this.globalData.token = null
    this.globalData.userInfo = null
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    
    wx.reLaunch({
      url: '/pages/login/login'
    })
  },

  // 检查是否已登录
  isLoggedIn() {
    return !!this.globalData.token
  },

  // 获取用户信息
  getUserInfo() {
    return this.globalData.userInfo
  },

  // 获取token
  getToken() {
    return this.globalData.token
  }
}) 