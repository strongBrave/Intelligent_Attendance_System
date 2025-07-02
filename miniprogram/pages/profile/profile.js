const app = getApp()

Page({
  data: {
    userInfo: {
      name: '',
      phone: '',
      department: null,
      role: ''
    },
    hasFace: false,
    faceUrl: '',
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
    this.checkTodayStatus()
  },

  // 初始化页面
  initPage() {
    this.loadUserInfo()
    this.checkFaceRegistration()
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

  // 检查人脸注册状态
  checkFaceRegistration() {
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
          const hasFace = res.data.has_face || false
          let faceUrl = ''
          
          if (hasFace && res.data.face_url) {
            // 构建完整的人脸照片URL
            const filename = res.data.face_url.split('/').pop()
            faceUrl = `${app.globalData.baseUrl}/uploads/faces/${filename}`
          }
          
          this.setData({
            hasFace: hasFace,
            faceUrl: faceUrl
          })
        }
      },
      fail: (err) => {
        console.error('检查人脸状态失败:', err)
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

  // 跳转到考勤记录
  goToAttendanceHistory() {
    wx.navigateTo({
      url: '/pages/attendance-history/attendance-history'
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
      'early_leave': '早退'
    }
    return statusMap[status] || status
  }
}) 