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
    },
    // 人脸更新申请相关
    showFaceUpdateModal: false,
    faceUpdateForm: {
      imageUrl: '',
      tempFilePath: '',
      reason: ''
    },
    submitting: false,
    // 添加一个计算属性来控制按钮状态
    canSubmit: false,
    faceRequestStatus: {
      has_request: false,
      request: null
    }
  },

  onLoad() {
    this.initPage()
  },

  onShow() {
    this.loadUserInfo()
    this.loadUserAvatar()
    this.checkTodayStatus()
    this.checkFaceUpdateRequestStatus()
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
  },

  // ==================== 人脸更新申请相关方法 ====================

  // 检查人脸更新申请状态
  checkFaceUpdateRequestStatus() {
    const token = wx.getStorageSync('token')
    if (!token) return

    wx.request({
      url: `${app.globalData.baseUrl}/api/user/face-update-request/status`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.success) {
          this.setData({
            faceRequestStatus: res.data
          })
        }
      },
      fail: (err) => {
        console.error('获取人脸更新申请状态失败:', err)
      }
    })
  },

  // 显示人脸更新申请弹窗
  showFaceUpdateDialog() {
    // 检查是否有待处理的申请
    if (this.data.faceRequestStatus.has_request && 
        this.data.faceRequestStatus.request.status === 'pending') {
      wx.showToast({
        title: '您已有待处理的申请',
        icon: 'none'
      })
      return
    }

    this.setData({
      showFaceUpdateModal: true,
      faceUpdateForm: {
        imageUrl: '',
        tempFilePath: '',
        reason: ''
      },
      canSubmit: false
    })
  },

  // 隐藏人脸更新申请弹窗
  hideFaceUpdateDialog() {
    this.setData({
      showFaceUpdateModal: false,
      faceUpdateForm: {
        imageUrl: '',
        tempFilePath: '',
        reason: ''
      },
      canSubmit: false
    })
  },

  // 选择图片
  chooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      maxDuration: 30,
      camera: 'back',
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath
        console.log('原始临时文件路径:', tempFilePath)
        
        // 使用文件系统管理器读取文件并转换为base64
        const fs = wx.getFileSystemManager()
        try {
          const fileData = fs.readFileSync(tempFilePath, 'base64')
          const base64Url = `data:image/jpeg;base64,${fileData}`
          
          console.log('文件转换为base64成功，长度:', fileData.length)
          
          this.setData({
            'faceUpdateForm.imageUrl': base64Url,       // 用于显示的base64路径
            'faceUpdateForm.tempFilePath': tempFilePath // 用于上传的原始路径
          })
          
          console.log('图片设置成功')
          
          // 更新按钮状态
          this.updateCanSubmit()
        } catch (error) {
          console.error('读取文件失败:', error)
          
          // 如果base64转换失败，尝试直接使用文件路径
          let displayPath = tempFilePath
          
          // 处理HTTP协议问题
          if (tempFilePath.startsWith('http://tmp/')) {
            displayPath = tempFilePath.replace('http://tmp/', 'wxfile://tmp_')
          } else if (tempFilePath.startsWith('http://')) {
            displayPath = tempFilePath.replace('http://', 'wxfile://')
          }
          
          console.log('使用备用方案，显示路径:', displayPath)
          
          this.setData({
            'faceUpdateForm.imageUrl': displayPath,
            'faceUpdateForm.tempFilePath': tempFilePath
          })
          
          // 更新按钮状态
          this.updateCanSubmit()
        }
      },
      fail: (err) => {
        console.error('选择图片失败:', err)
        wx.showToast({
          title: '选择图片失败',
          icon: 'none'
        })
      }
    })
  },

  // 申请原因输入
  onReasonInput(e) {
    const reason = e.detail.value
    this.setData({
      'faceUpdateForm.reason': reason
    })
    
    // 更新按钮状态
    this.updateCanSubmit()
  },

  // 更新提交按钮状态
  updateCanSubmit() {
    const { imageUrl, reason } = this.data.faceUpdateForm
    const canSubmit = !!(imageUrl && reason && reason.trim())
    this.setData({ canSubmit })
  },

  // 提交人脸更新申请
  submitFaceUpdateRequest() {
    const { imageUrl, tempFilePath, reason } = this.data.faceUpdateForm

    if (!imageUrl) {
      wx.showToast({
        title: '请上传人脸照片',
        icon: 'none'
      })
      return
    }

    if (!reason.trim()) {
      wx.showToast({
        title: '请填写申请原因',
        icon: 'none'
      })
      return
    }

    this.setData({ submitting: true })

    const token = wx.getStorageSync('token')
    if (!token) {
      this.setData({ submitting: false })
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    // 上传文件
    wx.uploadFile({
      url: `${app.globalData.baseUrl}/api/user/face-update-request`,
      filePath: tempFilePath,
      name: 'face_image',
      formData: {
        reason: reason.trim()
      },
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          if (data.success) {
            wx.showToast({
              title: '申请提交成功',
              icon: 'success'
            })
            this.hideFaceUpdateDialog()
            // 重新检查申请状态
            this.checkFaceUpdateRequestStatus()
          } else {
            wx.showToast({
              title: data.message || data.error || '提交失败',
              icon: 'none'
            })
          }
        } catch (e) {
          console.error('解析响应失败:', e)
          wx.showToast({
            title: '提交失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('提交人脸更新申请失败:', err)
        wx.showToast({
          title: '网络错误，提交失败',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({ submitting: false })
      }
    })
  }
}) 