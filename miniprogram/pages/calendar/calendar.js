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
      normal: 0,
      late: 0,
      absent: 0,
      early_leave: 0
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
      url: `${app.globalData.baseUrl}/api/user/attendance/month`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        year: year,
        month: month
      },
      success: (res) => {
        if (res.data.success) {
          const data = res.data.data
          const attendanceData = {}
          const stats = {
            normal: 0,
            late: 0,
            absent: 0,
            early_leave: 0
          }
          
          // 处理考勤数据
          data.forEach(item => {
            const date = item.date
            attendanceData[date] = {
              sign_in: item.sign_in ? item.sign_in.time : null,
              sign_out: item.sign_out ? item.sign_out.time : null,
              status: item.status,
              statusText: this.getStatusText(item.status),
              location: item.location
            }
            
            // 统计
            if (stats.hasOwnProperty(item.status)) {
              stats[item.status]++
            }
          })
          
          this.setData({
            attendanceData,
            stats
          })
          
          // 重新生成日历以显示考勤状态
          this.generateCalendar()
        }
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
    
    this.setData({
      selectedDate: date,
      selectedAttendance: attendance || {
        status: 'absent',
        statusText: '缺勤'
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
  }
}) 