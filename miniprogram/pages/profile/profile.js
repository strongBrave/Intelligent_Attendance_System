const app = getApp()

Page({
  data: {
    userInfo: {
      name: '',
      phone: '',
      department: null,
      role: ''
    },
    avatarUrl: '', // 用户头像URL
    todayStatus: {
      sign_in: null,
      sign_out: null,
      sign_in_status: null,
      sign_out_status: null
    }
  },

  onLoad() {
    this.initPage()
  },

  onShow() {
    this.loadUserInfo()
    this.loadUserAvatar()
    this.checkTodayStatus()
  },

  // 初始化页面
  initPage() {
    this.loadUserInfo()
    this.loadUserAvatar()
    this.checkTodayStatus()
  },

  // 加载用户信息
  loadUserInfo() {
    const userInfo = app.getUserInfo()
    if (userInfo) {
      this.setData({
        userInfo: {
          name: userInfo.name || '',
          phone: userInfo.phone || '',
          department: userInfo.department || null,
          role: userInfo.role || ''
        }
      })
    }
  },

  // 加载用户头像
  loadUserAvatar() {
    const token = wx.getStorageSync('token')
    if (!token) return

    wx.request({
      url: `${app.globalData.baseUrl}/api/user/face_status`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          if (res.data.has_face && res.data.face_url) {
            // 构建完整的人脸图片URL
            // 处理Windows路径分隔符问题，统一使用正斜杠
            const normalizedPath = res.data.face_url.replace(/\\/g, '/')
            const filename = normalizedPath.split('/').pop()
            const avatarUrl = `${app.globalData.baseUrl}/uploads/faces/${filename}`
            
            // 检查URL协议，如果是HTTP则使用下载方式
            if (avatarUrl.startsWith('http://')) {
              this.downloadAndSetAvatar(avatarUrl)
            } else {
              this.setData({
                avatarUrl: avatarUrl
              })
            }
          }
        }
      },
      fail: (err) => {
        console.error('获取用户头像失败:', err)
      }
    })
  },

  // 下载并设置头像
  downloadAndSetAvatar(avatarUrl) {
    wx.downloadFile({
      url: avatarUrl,
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            avatarUrl: res.tempFilePath
          })
        } else {
          this.setData({
            avatarUrl: ''
          })
        }
      },
      fail: (err) => {
        console.error('头像下载失败:', err)
        this.setData({
          avatarUrl: ''
        })
      }
    })
  },



  // 检查今日考勤状态
  checkTodayStatus() {
    const token = wx.getStorageSync('token')
    if (!token) return

    wx.request({
      url: `${app.globalData.baseUrl}/api/attendance/today`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = res.data
          this.setData({
            todayStatus: {
              sign_in: data.check_in?.time || '',
              sign_out: data.check_out?.time || '',
              sign_in_status: data.check_in?.status || '',
              sign_out_status: data.check_out?.status || ''
            }
          })
        }
      },
      fail: (err) => {
        console.error('获取今日考勤状态失败:', err)
      }
    })
  },

  // 跳转到部门管理
  goToDepartmentManagement() {
    wx.navigateTo({
      url: '/pages/department/department'
    })
  },

  // 跳转到设置
  goToSettings() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    })
  },

  // 跳转到打卡页面
  goToAttendance() {
    wx.switchTab({
      url: '/pages/attendance/attendance'
    })
  },

  // 跳转到日历页面
  goToCalendar() {
    wx.switchTab({
      url: '/pages/calendar/calendar'
    })
  },

  // 跳转到统计页面
  goToStats() {
    wx.switchTab({
      url: '/pages/stats/stats'
    })
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync()
          wx.reLaunch({
            url: '/pages/login/login'
          })
        }
      }
    })
  },

  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      'normal': '正常',
      'late': '迟到',
      'absent': '缺勤',
      'early_leave': '早退',
      'late_leave': '晚退'
    }
    return statusMap[status] || status
  },

  // 头像加载成功
  onAvatarLoad(e) {
    // 头像加载成功
  },

  // 头像加载失败
  onAvatarError(e) {
    console.error('头像加载失败:', e.detail)
    // 加载失败时清空avatarUrl，显示占位符
    this.setData({
      avatarUrl: ''
    })
  }
}) 