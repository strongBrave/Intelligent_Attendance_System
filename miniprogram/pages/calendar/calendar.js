const app = getApp()

Page({
  data: {
    // 当前年月
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth() + 1,
    
    // 星期标题
    weekdays: ['日', '一', '二', '三', '四', '五', '六'],
    
    // 日历数据
    calendarDays: [],
    
    // 统计信息
    stats: {
      normal_sign_in: 0,
      normal_sign_out: 0,
      late: 0,
      absent: 0,
      early_leave: 0,
      late_leave: 0
    },
    
    // 选中日期
    selectedDate: '',
    selectedAttendance: null,
    
    // 考勤数据
    attendanceData: {}
  },

  onLoad() {
    this.initCalendar()
  },

  onShow() {
    this.loadAttendanceData()
  },

  // 初始化日历
  initCalendar() {
    this.generateCalendar()
  },

  // 生成日历数据
  generateCalendar() {
    const year = this.data.currentYear
    const month = this.data.currentMonth
    const days = []
    
    // 获取当月第一天和最后一天
    const firstDay = new Date(year, month - 1, 1)
    const lastDay = new Date(year, month, 0)
    const firstDayWeek = firstDay.getDay()
    const lastDate = lastDay.getDate()
    
    // 获取上个月的最后几天
    const prevMonth = new Date(year, month - 1, 0)
    const prevLastDate = prevMonth.getDate()
    
    // 添加上个月的日期
    for (let i = firstDayWeek - 1; i >= 0; i--) {
      const day = prevLastDate - i
      const date = new Date(year, month - 2, day)
      days.push({
        day: day,
        date: this.formatDate(date),
        isCurrentMonth: false,
        isToday: false,
        attendance: null
      })
    }
    
    // 添加当月的日期
    const today = new Date()
    for (let day = 1; day <= lastDate; day++) {
      const date = new Date(year, month - 1, day)
      const isToday = year === today.getFullYear() && 
                     month === today.getMonth() + 1 && 
                     day === today.getDate()
      
      days.push({
        day: day,
        date: this.formatDate(date),
        isCurrentMonth: true,
        isToday: isToday,
        attendance: this.data.attendanceData[this.formatDate(date)] || null
      })
    }
    
    // 添加下个月的日期
    const remainingDays = 42 - days.length // 保持6行
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(year, month, day)
      days.push({
        day: day,
        date: this.formatDate(date),
        isCurrentMonth: false,
        isToday: false,
        attendance: null
      })
    }
    
    this.setData({
      calendarDays: days
    })
  },

  // 格式化日期
  formatDate(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  },

  // 上个月
  prevMonth() {
    let { currentYear, currentMonth } = this.data
    if (currentMonth === 1) {
      currentYear--
      currentMonth = 12
    } else {
      currentMonth--
    }
    
    this.setData({
      currentYear,
      currentMonth
    })
    
    this.generateCalendar()
    this.loadAttendanceData()
  },

  // 下个月
  nextMonth() {
    let { currentYear, currentMonth } = this.data
    if (currentMonth === 12) {
      currentYear++
      currentMonth = 1
    } else {
      currentMonth++
    }
    
    this.setData({
      currentYear,
      currentMonth
    })
    
    this.generateCalendar()
    this.loadAttendanceData()
  },

  // 加载考勤数据
  loadAttendanceData() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    const year = this.data.currentYear
    const month = this.data.currentMonth
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/user/month`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        year: year,
        month: month
      },
      success: (res) => {
        this.processAttendanceData(res.data)
      },
      fail: (err) => {
        console.error('获取考勤数据失败:', err)
        wx.showToast({
          title: '获取考勤数据失败',
          icon: 'none'
        })
      }
    })
  },

  // 选择日期
  selectDate(e) {
    const date = e.currentTarget.dataset.date
    const attendance = this.data.attendanceData[date]
    
    // 如果没有考勤数据，创建默认结构
    const defaultAttendance = {
      sign_in: null,
      sign_out: null,
      status: 'absent',
      statusText: this.getStatusText('absent')
    }
    
    this.setData({
      selectedDate: date,
      selectedAttendance: attendance || defaultAttendance
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
    const result = statusMap[status] || status || '未知'
    return result
  },

  // 检查数据完整性
  validateAttendanceData(data) {
    if (!Array.isArray(data)) {
      console.error('[日历] 考勤数据不是数组格式:', data)
      return false
    }
    
    data.forEach((item, index) => {
      if (!item.date) {
        console.warn(`[日历] 第${index}条记录缺少日期字段:`, item)
      }
      if (!item.status) {
        console.warn(`[日历] 第${index}条记录缺少状态字段:`, item)
      }
      
      // 验证签到签退数据结构
      if (item.sign_in && (!item.sign_in.time || !item.sign_in.status)) {
        console.warn(`[日历] 第${index}条记录签到数据结构不完整:`, item.sign_in)
      }
      if (item.sign_out && (!item.sign_out.time || !item.sign_out.status)) {
        console.warn(`[日历] 第${index}条记录签退数据结构不完整:`, item.sign_out)
      }
    })
    
    return true
  },

  // 跳转到打卡页面
  goToAttendance() {
    wx.switchTab({
      url: '/pages/attendance/attendance'
    })
  },

  // 刷新数据
  refreshData() {
    wx.showLoading({
      title: '刷新中...'
    })
    
    this.loadAttendanceData()
    
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    }, 1000)
  },



  // 提取数据处理逻辑为独立方法
  processAttendanceData(response) {
    if (response.success) {
      const data = response.data
      
      // 验证数据完整性
      if (!this.validateAttendanceData(data)) {
        wx.showToast({
          title: '考勤数据格式错误',
          icon: 'none'
        })
        return
      }
      
      const attendanceData = {}
      const stats = {
        normal_sign_in: 0,
        normal_sign_out: 0,
        late: 0,
        absent: 0,
        early_leave: 0,
        late_leave: 0
      }
      
      // 处理考勤数据
      data.forEach(item => {
        const date = item.date
        
        // 处理签到数据
        let processedSignIn = null
        if (item.sign_in) {
          processedSignIn = {
            time: item.sign_in.time,
            status: item.sign_in.status,
            statusText: this.getStatusText(item.sign_in.status),
            location: item.sign_in.location
          }
        }
        
        // 处理签退数据
        let processedSignOut = null
        if (item.sign_out) {
          processedSignOut = {
            time: item.sign_out.time,
            status: item.sign_out.status,
            statusText: this.getStatusText(item.sign_out.status),
            location: item.sign_out.location
          }
        }
        
        attendanceData[date] = {
          sign_in: processedSignIn,
          sign_out: processedSignOut,
          status: item.status,
          statusText: this.getStatusText(item.status),
          location: item.location
        }
        
        // 分别统计签到和签退状态
        if (processedSignIn) {
          const signInStatus = processedSignIn.status
          if (signInStatus === 'normal') {
            stats.normal_sign_in++
          } else if (signInStatus === 'late') {
            stats.late++
          } else if (stats.hasOwnProperty(signInStatus)) {
            stats[signInStatus]++
          }
        } else {
          // 没有签到记录算作缺勤
          stats.absent++
        }
        
        if (processedSignOut) {
          const signOutStatus = processedSignOut.status
          if (signOutStatus === 'normal') {
            stats.normal_sign_out++
          } else if (stats.hasOwnProperty(signOutStatus)) {
            stats[signOutStatus]++
          }
        }
      })
      
      this.setData({
        attendanceData,
        stats
      })
      
      // 重新生成日历以显示考勤状态
      this.generateCalendar()
    } else {
      wx.showToast({
        title: response.message || '获取数据失败',
        icon: 'none'
      })
    }
  }
}) 