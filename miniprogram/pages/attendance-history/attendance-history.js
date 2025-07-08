const app = getApp()

Page({
  data: {
    // 日期选择
    startDate: '',
    endDate: '',
    today: '',
    
    // 查询结果
    records: [],
    stats: {
      total: 0,
      normal_sign_in: 0,
      normal_sign_out: 0,
      late: 0,
      absent: 0,
      early_leave: 0,
      late_leave: 0
    },
    
    // 加载状态
    loading: false
  },

  onLoad() {
    this.initPage()
  },

  // 初始化页面
  initPage() {
    const today = new Date().toISOString().slice(0, 10)
    this.setData({
      today: today,
      startDate: today,
      endDate: today
    })
    
    // 默认查询今天的记录
    this.queryRecords()
  },

  // 开始日期选择
  onStartDateChange(e) {
    this.setData({
      startDate: e.detail.value
    })
  },

  // 结束日期选择
  onEndDateChange(e) {
    this.setData({
      endDate: e.detail.value
    })
  },

  // 设置快捷日期范围
  setDateRange(e) {
    const range = e.currentTarget.dataset.range
    const today = new Date()
    const todayStr = today.toISOString().slice(0, 10)
    
    let startDate, endDate
    
    switch (range) {
      case 'today':
        startDate = todayStr
        endDate = todayStr
        break
      case 'yesterday':
        const yesterday = new Date(today)
        yesterday.setDate(today.getDate() - 1)
        startDate = yesterday.toISOString().slice(0, 10)
        endDate = startDate
        break
      case 'thisWeek':
        const thisWeekStart = new Date(today)
        thisWeekStart.setDate(today.getDate() - today.getDay())
        startDate = thisWeekStart.toISOString().slice(0, 10)
        endDate = todayStr
        break
      case 'lastWeek':
        const lastWeekStart = new Date(today)
        lastWeekStart.setDate(today.getDate() - today.getDay() - 7)
        const lastWeekEnd = new Date(lastWeekStart)
        lastWeekEnd.setDate(lastWeekStart.getDate() + 6)
        startDate = lastWeekStart.toISOString().slice(0, 10)
        endDate = lastWeekEnd.toISOString().slice(0, 10)
        break
      case 'thisMonth':
        const thisMonthStart = new Date(today.getFullYear(), today.getMonth(), 1)
        startDate = thisMonthStart.toISOString().slice(0, 10)
        endDate = todayStr
        break
      case 'lastMonth':
        const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1)
        const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0)
        startDate = lastMonthStart.toISOString().slice(0, 10)
        endDate = lastMonthEnd.toISOString().slice(0, 10)
        break
      default:
        return
    }
    
    this.setData({
      startDate: startDate,
      endDate: endDate
    })
    
    this.queryRecords()
  },

  // 查询考勤记录
  queryRecords() {
    const { startDate, endDate } = this.data
    
    if (!startDate || !endDate) {
      wx.showToast({
        title: '请选择日期范围',
        icon: 'none'
      })
      return
    }
    
    if (startDate > endDate) {
      wx.showToast({
        title: '开始日期不能晚于结束日期',
        icon: 'none'
      })
      return
    }
    
    this.setData({ loading: true })
    
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      this.setData({ loading: false })
      return
    }
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/attendance/records`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        start_date: startDate,
        end_date: endDate
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const records = res.data.records || []
          
          // 处理记录数据
          const processedRecords = this.processRecords(records)
          
          // 计算统计信息
          const stats = this.calculateStats(records)
          
          this.setData({
            records: processedRecords,
            stats: stats
          })
        } else {
          wx.showToast({
            title: res.data.msg || '查询失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('查询考勤记录失败:', err)
        wx.showToast({
          title: '查询失败',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({ loading: false })
      }
    })
  },

  // 重置查询条件
  resetQuery() {
    const today = new Date().toISOString().slice(0, 10)
    this.setData({
      startDate: today,
      endDate: today,
      records: [],
      stats: {
        total: 0,
        normal_sign_in: 0,
        normal_sign_out: 0,
        late: 0,
        absent: 0,
        early_leave: 0,
        late_leave: 0
      }
    })
  },

  // 计算统计信息
  calculateStats(records) {
    const stats = {
      total: records.length,
      normal_sign_in: 0,
      normal_sign_out: 0,
      late: 0,
      absent: 0,
      early_leave: 0,
      late_leave: 0
    }
    
    records.forEach(record => {
      if (record.status === 'normal') {
        if (record.check_type === 'sign_in') {
          stats.normal_sign_in++
        } else if (record.check_type === 'sign_out') {
          stats.normal_sign_out++
        }
      } else if (stats.hasOwnProperty(record.status)) {
        stats[record.status]++
      }
    })
    
    return stats
  },

  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      'normal': '正常',
      'late': '迟到',
      'absent': '缺勤',
      'early_leave': '早退',
      'late_leave': '晚退',
      'not_yet_time': '未到时间'
    }
    return statusMap[status] || status
  },

  // 获取操作类型文本
  getCheckTypeText(checkType) {
    const typeMap = {
      'sign_in': '签到',
      'sign_out': '签退'
    }
    return typeMap[checkType] || checkType
  },

  // 处理记录数据
  processRecords(records) {
    return records.map(record => ({
      ...record,
      statusText: this.getStatusText(record.status),
      checkTypeText: this.getCheckTypeText(record.check_type),
      time_display: record.time ? record.time.split(' ')[1] : '', // 只显示时间部分
      location_display: record.location || '未知位置'
    }))
  }
}) 