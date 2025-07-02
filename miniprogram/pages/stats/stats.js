const app = getApp()

Page({
  data: {
    // 当前月份
    currentMonth: new Date().getMonth() + 1,
    selectedMonth: '',
    
    // 统计概览
    overview: {
      normal: 0,
      late: 0,
      absent: 0,
      early_leave: 0
    },
    
    // 出勤率
    attendanceRate: 0,
    
    // 详细统计
    detailStats: {
      totalDays: 0,
      actualDays: 0,
      avgSignInTime: '--:--',
      avgSignOutTime: '--:--'
    },
    
    // 图表数据
    chartData: []
  },

  onLoad() {
    this.initPage()
  },

  onShow() {
    this.loadStatsData()
  },

  // 初始化页面
  initPage() {
    const now = new Date()
    const selectedMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    
    this.setData({
      currentMonth: now.getMonth() + 1,
      selectedMonth: selectedMonth
    })
  },

  // 月份选择器变化
  onMonthChange(e) {
    const selectedMonth = e.detail.value
    this.setData({
      selectedMonth: selectedMonth,
      currentMonth: parseInt(selectedMonth.split('-')[1])
    })
    
    this.loadStatsData()
  },

  // 加载统计数据
  loadStatsData() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    const [year, month] = this.data.selectedMonth.split('-')
    
    wx.showLoading({
      title: '加载中...'
    })

    // 获取月度考勤数据
    wx.request({
      url: `${app.globalData.baseUrl}/api/user/attendance/month`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        year: parseInt(year),
        month: parseInt(month)
      },
      success: (res) => {
        wx.hideLoading()
        
        if (res.data.success) {
          this.processStatsData(res.data.data)
        } else {
          wx.showToast({
            title: res.data.message || '获取数据失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('获取统计数据失败:', err)
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    })
  },

  // 处理统计数据
  processStatsData(data) {
    const overview = {
      normal: 0,
      late: 0,
      absent: 0,
      early_leave: 0
    }
    
    const signInTimes = []
    const signOutTimes = []
    let actualDays = 0
    
    // 统计各种状态的数量
    data.forEach(item => {
      if (item.status !== 'absent') {
        actualDays++
      }
      
      if (overview.hasOwnProperty(item.status)) {
        overview[item.status]++
      }
      
      // 收集签到签退时间
      if (item.sign_in && item.sign_in.time) {
        signInTimes.push(item.sign_in.time)
      }
      if (item.sign_out && item.sign_out.time) {
        signOutTimes.push(item.sign_out.time)
      }
    })
    
    // 计算出勤率
    const totalDays = this.getWorkingDays(parseInt(this.data.selectedMonth.split('-')[0]), parseInt(this.data.selectedMonth.split('-')[1]))
    const attendanceRate = totalDays > 0 ? Math.round((actualDays / totalDays) * 100) : 0
    
    // 计算平均时间
    const avgSignInTime = this.calculateAverageTime(signInTimes)
    const avgSignOutTime = this.calculateAverageTime(signOutTimes)
    
    this.setData({
      overview,
      attendanceRate,
      detailStats: {
        totalDays,
        actualDays,
        avgSignInTime,
        avgSignOutTime
      },
      chartData: data
    })
    
    // 绘制图表
    this.drawChart()
  },

  // 获取工作日数量
  getWorkingDays(year, month) {
    const startDate = new Date(year, month - 1, 1)
    const endDate = new Date(year, month, 0)
    let workingDays = 0
    
    for (let date = new Date(startDate); date <= endDate; date.setDate(date.getDate() + 1)) {
      const dayOfWeek = date.getDay()
      // 排除周末
      if (dayOfWeek !== 0 && dayOfWeek !== 6) {
        workingDays++
      }
    }
    
    return workingDays
  },

  // 计算平均时间
  calculateAverageTime(times) {
    if (times.length === 0) return '--:--'
    
    let totalMinutes = 0
    times.forEach(time => {
      const [hours, minutes] = time.split(':').map(Number)
      totalMinutes += hours * 60 + minutes
    })
    
    const avgMinutes = Math.round(totalMinutes / times.length)
    const hours = Math.floor(avgMinutes / 60)
    const minutes = avgMinutes % 60
    
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
  },

  // 绘制图表
  drawChart() {
    const ctx = wx.createCanvasContext('attendanceChart')
    const chartData = this.data.chartData
    
    if (chartData.length === 0) {
      // 绘制空状态
      ctx.setFillStyle('rgba(255, 255, 255, 0.3)')
      ctx.fillText('暂无数据', 150, 200)
      ctx.draw()
      return
    }
    
    const canvasWidth = 300
    const canvasHeight = 200
    const padding = 40
    const chartWidth = canvasWidth - padding * 2
    const chartHeight = canvasHeight - padding * 2
    
    // 清空画布
    ctx.clearRect(0, 0, canvasWidth, canvasHeight)
    
    // 绘制坐标轴
    ctx.setStrokeStyle('rgba(255, 255, 255, 0.3)')
    ctx.setLineWidth(1)
    
    // X轴
    ctx.beginPath()
    ctx.moveTo(padding, canvasHeight - padding)
    ctx.lineTo(canvasWidth - padding, canvasHeight - padding)
    ctx.stroke()
    
    // Y轴
    ctx.beginPath()
    ctx.moveTo(padding, padding)
    ctx.lineTo(padding, canvasHeight - padding)
    ctx.stroke()
    
    // 绘制数据点
    const maxValue = Math.max(...chartData.map(item => {
      if (item.status === 'normal') return 4
      if (item.status === 'late') return 3
      if (item.status === 'early_leave') return 2
      if (item.status === 'absent') return 1
      return 0
    }))
    
    chartData.forEach((item, index) => {
      const x = padding + (index / (chartData.length - 1)) * chartWidth
      const value = item.status === 'normal' ? 4 : 
                   item.status === 'late' ? 3 : 
                   item.status === 'early_leave' ? 2 : 
                   item.status === 'absent' ? 1 : 0
      const y = canvasHeight - padding - (value / maxValue) * chartHeight
      
      // 设置颜色
      let color = 'rgba(255, 255, 255, 0.5)'
      if (item.status === 'normal') color = '#4CAF50'
      else if (item.status === 'late') color = '#FF9800'
      else if (item.status === 'early_leave') color = '#9C27B0'
      else if (item.status === 'absent') color = '#F44336'
      
      ctx.setFillStyle(color)
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, 2 * Math.PI)
      ctx.fill()
    })
    
    ctx.draw()
  },

  // 刷新数据
  refreshData() {
    this.loadStatsData()
    wx.showToast({
      title: '刷新成功',
      icon: 'success'
    })
  },

  // 导出数据
  exportData() {
    wx.showToast({
      title: '导出功能开发中',
      icon: 'none'
    })
  }
}) 