const app = getApp()

Page({
  data: {
    // 用户信息
    userInfo: null,
    
    // 时间显示
    currentTime: '',
    today: '',
    checkInTime: '',
    checkOutTime: '',
    checkInStatus: '',
    checkOutStatus: '',
    loading: false,
    
    // 考勤状态
    checkType: 'sign_in', // sign_in 或 sign_out
    isProcessing: false,
    isReady: false,
    processingText: '',
    
    // 状态提示
    statusTip: null,
    
    // 今日考勤状态
    todayStatus: null,
    
    // 位置信息
    location: {
      latitude: 0,
      longitude: 0,
      address: ''
    },
    
    // 新增地图相关数据
    latitude: 39.90923,
    longitude: 116.397428,
    markers: [],
    circles: [],
    inRange: null,
    distanceInfo: '',
    showMap: false,
    departmentLocation: null,
    distanceThreshold: 100,
    // 地图搜索相关
    searchKeyword: '',
    searchResults: [],
    showSearch: false,
    showFaceModal: false, // 是否显示人脸打卡弹窗
    faceCheckStatus: 'pending', // pending/success/fail
    faceCheckTimer: 0, // 秒数
    faceCheckInterval: null,
    
    // 人脸检测相关
    faceDetectionCanvas: null,
    faceBoxes: [], // 检测到的人脸框
    isDetecting: false, // 是否正在检测
    detectionInterval: null, // 检测定时器
    isVerifying: false, // 是否正在验证
  },

  onLoad() {
    console.log('[调试] onLoad 被调用')
    this.initPage()
    this.getUserInfo()
    this.updateTime()
    this.getTodayAttendance()
    
    // 启动定时器
    this.timer = setInterval(() => {
      this.updateTime()
    }, 1000)
  },

  onShow() {
    console.log('[调试] onShow 被调用')
    this.startTimeUpdate()
    this.getTodayStatus()
    this.getTodayAttendance()
    this.checkLocation()
    this.checkFaceRegistration()
    
    // 延迟检查按钮状态，确保所有数据都已加载
    setTimeout(() => {
      this.checkButtonAvailability()
      this.debugButtonStatus()
    }, 1000)
  },

  onHide() {
    this.stopTimeUpdate()
  },

  onUnload() {
    this.stopTimeUpdate()
    if (this.timer) {
      clearInterval(this.timer)
    }
  },

  // 初始化页面
  initPage() {
    console.log('[调试] initPage 被调用')
    // 获取用户信息
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({
        userInfo: {
          name: userInfo.name,
          department: userInfo.department ? userInfo.department.name : ''
        }
      })
    }

    // 获取位置信息
    this.getLocation()
    
    // 检查人脸注册状态
    this.checkFaceRegistration()
  },

  // 开始时间更新
  startTimeUpdate() {
    this.updateTime()
    this.timeInterval = setInterval(() => {
      this.updateTime()
    }, 1000)
  },

  // 停止时间更新
  stopTimeUpdate() {
    if (this.timeInterval) {
      clearInterval(this.timeInterval)
      this.timeInterval = null
    }
  },

  // 获取用户信息
  getUserInfo() {
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({
        userInfo: {
          name: userInfo.name,
          department: userInfo.department ? userInfo.department.name : ''
        }
      })
    }
  },

  // 更新当前时间
  updateTime() {
    const now = new Date()
    const currentTime = now.toLocaleTimeString('zh-CN', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
    const today = now.toLocaleDateString('zh-CN')
    
    this.setData({
      currentTime,
      today
    })
  },

  // 获取位置信息
  getLocation() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        console.log('[调试] 获取到位置坐标:', res)
        this.setData({
          location: {
            latitude: res.latitude,
            longitude: res.longitude,
            address: '正在获取地址...'
          }
        })
        // 获取地址信息
        this.getAddressFromCoords(res.latitude, res.longitude)
      },
      fail: (err) => {
        console.error('获取位置失败:', err)
        
        // 根据错误类型提供不同的处理
        if (err.errMsg && err.errMsg.includes('auth deny')) {
          // 用户拒绝权限
          wx.showModal({
            title: '位置权限被拒绝',
            content: '需要位置权限来记录打卡位置，请在设置中开启位置权限',
            confirmText: '去设置',
            cancelText: '取消',
            success: (res) => {
              if (res.confirm) {
                // 打开设置页面
                wx.openSetting({
                  success: (settingRes) => {
                    console.log('[调试] 设置页面结果:', settingRes)
                    if (settingRes.authSetting['scope.userLocation']) {
                      // 用户开启了权限，重新获取位置
                      this.getLocation()
                    }
                  }
                })
              }
            }
          })
        } else {
          wx.showToast({
            title: '获取位置失败',
            icon: 'none'
          })
        }
      }
    })
  },

  // 根据坐标获取地址
  getAddressFromCoords(latitude, longitude) {
    console.log('[调试] 开始获取地址信息:', latitude, longitude)
    
    // 直接使用坐标作为地址，避免依赖外部API
    const address = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`
    console.log('[调试] 使用坐标作为地址:', address)
    this.setData({
      'location.address': address
    })
    
    // 可选：尝试获取更详细的地址信息（如果网络可用）
    this.tryGetDetailedAddress(latitude, longitude)
  },

  // 尝试获取详细地址（可选）
  tryGetDetailedAddress(latitude, longitude) {
    // 当前Key为JS API Key，无法用于Web服务API
    const apiKey = '5c3066c36f6fa333afc7f55f78c33ff0'  // 需要替换为实际的Web服务API Key
    
         // API Key已配置，继续调用高德API
    
    // 使用高德地图API获取地址
    wx.request({
      url: 'https://restapi.amap.com/v3/geocode/regeo',
      data: {
        key: apiKey,
        location: `${longitude},${latitude}`, // 高德API格式：经度,纬度
        poitype: '',
        radius: 1000,
        extensions: 'all',
        batch: false,
        roadlevel: 0
      },
      success: (res) => {
        console.log('[调试] 高德地图API响应:', res)
        if (res.data && res.data.status === '1' && res.data.regeocode) {
          const regeocode = res.data.regeocode
          let detailedAddress = regeocode.formatted_address || ''
          
          // 如果没有formatted_address，尝试组合地址
          if (!detailedAddress && regeocode.addressComponent) {
            const addr = regeocode.addressComponent
            const addressParts = [
              addr.province || '',
              addr.city || '',
              addr.district || '',
              addr.township || '',
              addr.streetNumber?.street || '',
              addr.streetNumber?.number || ''
            ]
            detailedAddress = addressParts.filter(part => part).join('')
          }
          
          if (detailedAddress) {
            console.log('[调试] 获取到详细地址:', detailedAddress)
            this.setData({
              'location.address': detailedAddress
            })
          } else {
            // API调用成功但没有地址信息，显示坐标
            const coordinateAddress = `经纬度: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`
            this.setData({
              'location.address': coordinateAddress
            })
          }
        } else {
          console.log('[调试] 高德API错误:', res.data?.info || '未知错误')
          // API调用失败，显示坐标
          const coordinateAddress = `经纬度: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`
          this.setData({
            'location.address': coordinateAddress
          })
        }
      },
      fail: (err) => {
        console.log('[调试] 获取详细地址失败，继续使用坐标地址:', err)
        // 网络请求失败，显示坐标
        const coordinateAddress = `经纬度: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`
        this.setData({
          'location.address': coordinateAddress
        })
      }
    })
  },

  // 检查人脸注册状态（简化版本，不再强制要求人脸注册）
  checkFaceRegistration() {
    console.log('[调试] checkFaceRegistration 被调用')
    const token = wx.getStorageSync('token')
    if (!token) {
      console.log('[调试] 没有token，设置isReady为false')
      this.setData({
        isReady: false,
        statusTip: {
          type: 'error',
          message: '请先登录'
        }
      })
      return
    }

    // 直接设置isReady为true，不再检查人脸注册状态
    console.log('[调试] 跳过人脸注册检查，直接设置isReady为true')
    this.setData({
      isReady: true,
      statusTip: null
    })
    // 调用按钮状态调试
    this.debugButtonStatus()
    // 检查按钮可用性
    this.checkButtonAvailability()
  },

  // 获取今日考勤状态
  getTodayStatus() {
    const token = wx.getStorageSync('token')
    if (!token) return

    const today = new Date().toISOString().slice(0, 10)
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/user/attendance/today`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        date: today
      },
      success: (res) => {
        if (res.data.success) {
          const data = res.data.data
          let checkType = 'sign_in'
          let todayStatus = null

          if (data.sign_in && !data.sign_out) {
            checkType = 'sign_out'
            todayStatus = {
              sign_in: data.sign_in.time,
              status: data.sign_in.status,
              statusText: this.getStatusText(data.sign_in.status)
            }
          } else if (data.sign_in && data.sign_out) {
            checkType = 'sign_in'
            todayStatus = {
              sign_in: data.sign_in.time,
              sign_out: data.sign_out.time,
              status: data.sign_out.status,
              statusText: this.getStatusText(data.sign_out.status)
            }
          }

          this.setData({
            checkType,
            todayStatus
          })
        }
      },
      fail: (err) => {
        console.error('获取今日考勤状态失败:', err)
      }
    })
  },

  // 获取今日考勤记录
  async getTodayAttendance() {
    console.log('[调试] getTodayAttendance 被调用')
    try {
      const token = wx.getStorageSync('token')
      if (!token) {
        console.log('[调试] 没有token，退出getTodayAttendance')
        wx.showToast({
          title: '请先登录',
          icon: 'none'
        })
        return
      }

      console.log('[调试] 开始请求今日考勤数据')
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/attendance/today`,
          method: 'GET',
          header: {
            'Authorization': `Bearer ${token}`
          },
          success: resolve,
          fail: reject
        })
      })

      console.log('[调试] 考勤请求响应:', response.statusCode, response.data)
      if (response.statusCode === 200) {
        const data = response.data
        const newData = {
          checkInTime: data.check_in?.time || '',
          checkOutTime: data.check_out?.time || '',
          checkInStatus: data.check_in?.status || '',
          checkOutStatus: data.check_out?.status || ''
        }
        console.log('[调试] 设置考勤数据:', newData)
        this.setData(newData, () => {
          console.log('[调试] getTodayAttendance setData回调后的inRange:', this.data.inRange)
        })
        // 调试输出
        console.log('[考勤] checkInTime:', this.data.checkInTime, 'checkOutTime:', this.data.checkOutTime)
        console.log('[考勤] inRange:', this.data.inRange, 'isReady:', this.data.isReady)
        // 调用按钮状态调试
        this.debugButtonStatus()
        // 检查按钮可用性
        this.checkButtonAvailability()
      }
    } catch (error) {
      console.error('[调试] 获取考勤记录失败:', error)
    }
  },

  // 检查位置
  async checkLocation() {
    console.log('[调试] checkLocation 被调用')
    try {
      // 首先检查位置权限
      const setting = await wx.getSetting()
      console.log('[调试] 位置权限设置:', setting.authSetting)
      
      if (!setting.authSetting['scope.userLocation']) {
        // 没有位置权限，引导用户开启
        console.log('[调试] 没有位置权限，请求权限')
        const authResult = await wx.authorize({
          scope: 'scope.userLocation'
        })
        console.log('[调试] 权限请求结果:', authResult)
      }
      
      // 获取当前位置
      console.log('[调试] 开始获取位置')
      const locationRes = await wx.getLocation({
        type: 'gcj02'
      })
      console.log('[调试] 获取到位置:', locationRes)

      console.log('[调试] 设置位置前的inRange:', this.data.inRange)
      
      // 只更新位置信息，不覆盖其他数据
      this.setData({
        latitude: locationRes.latitude,
        longitude: locationRes.longitude
      })
      
      console.log('[调试] 设置位置后的inRange:', this.data.inRange)

      // 检查是否在打卡范围内
      await this.checkDistance(locationRes.latitude, locationRes.longitude)
      
      // 更新地图标记
      this.updateMapMarkers()
      // 调试输出
      console.log('[位置] checkInTime:', this.data.checkInTime, 'checkOutTime:', this.data.checkOutTime)
      console.log('[位置] inRange:', this.data.inRange, 'isReady:', this.data.isReady)
    } catch (error) {
      console.error('[调试] 获取位置失败:', error)
      
      // 根据错误类型提供不同的处理
      if (error.errMsg && error.errMsg.includes('auth deny')) {
        // 用户拒绝权限
        wx.showModal({
          title: '位置权限被拒绝',
          content: '需要位置权限来记录打卡位置，请在设置中开启位置权限',
          confirmText: '去设置',
          cancelText: '取消',
          success: (res) => {
            if (res.confirm) {
              // 打开设置页面
              wx.openSetting({
                success: (settingRes) => {
                  console.log('[调试] 设置页面结果:', settingRes)
                  if (settingRes.authSetting['scope.userLocation']) {
                    // 用户开启了权限，重新获取位置
                    this.checkLocation()
                  }
                }
              })
            }
          }
        })
      } else if (error.errMsg && error.errMsg.includes('timeout')) {
        // 超时错误
        wx.showToast({
          title: '获取位置超时，请检查网络',
          icon: 'none',
          duration: 2000
        })
      } else {
        // 其他错误
        wx.showToast({
          title: '获取位置失败，请重试',
          icon: 'none',
          duration: 2000
        })
      }
    }
  },

  // 检查距离
  async checkDistance(latitude, longitude) {
    console.log('[调试] checkDistance 被调用，参数:', latitude, longitude)
    try {
      const token = wx.getStorageSync('token')
      if (!token) {
        console.log('[调试] 没有token，退出checkDistance')
        return
      }

      console.log('[调试] 开始请求距离检查')
      console.log('[调试] 请求URL:', `${app.globalData.baseUrl}/api/attendance/check_distance`)
      console.log('[调试] 请求数据:', { latitude, longitude })
      
      // 使用Promise包装wx.request
      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/attendance/check_distance`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          data: {
            latitude,
            longitude
          },
          success: resolve,
          fail: reject
        })
      })

      console.log('[调试] 距离检查响应:', response.statusCode, response.data)
      console.log('[调试] 响应数据类型:', typeof response.data)
      console.log('[调试] 响应数据字符串:', JSON.stringify(response.data))
      
      if (response.statusCode === 200) {
        const data = response.data
        console.log('[调试] 原始响应数据:', data)
        console.log('[调试] in_range类型:', typeof data.in_range, '值:', data.in_range)
        console.log('[调试] message:', data.message)
        console.log('[调试] department_location:', data.department_location)
        console.log('[调试] distance_threshold:', data.distance_threshold)
        
        const newData = {
          inRange: data.in_range,
          distanceInfo: data.message,
          departmentLocation: data.department_location,
          distanceThreshold: data.distance_threshold || 100
        }
        console.log('[调试] 设置距离数据:', newData)
        console.log('[调试] inRange类型:', typeof newData.inRange, '值:', newData.inRange)
        
        // 设置前的状态
        console.log('[调试] 设置前的inRange:', this.data.inRange)
        
        this.setData(newData, () => {
          console.log('[调试] setData回调后的inRange:', this.data.inRange)
        })
        
        // 设置后再次检查
        console.log('[调试] 设置后的inRange:', this.data.inRange)
        
        // 调用按钮状态调试
        this.debugButtonStatus()
        // 检查按钮可用性
        this.checkButtonAvailability()

        // 如果部门设置了位置，解析并显示在地图上
        if (data.department_location) {
          this.parseDepartmentLocation(data.department_location)
        }
      } else {
        console.error('[调试] 距离检查请求失败，状态码:', response.statusCode)
        console.error('[调试] 错误响应:', response.data)
      }
    } catch (error) {
      console.error('[调试] 检查距离失败:', error)
    }
  },

  // 解析部门位置
  parseDepartmentLocation(locationStr) {
    try {
      console.log('[调试] 解析部门位置:', locationStr)
      // 格式: "latitude,longitude (address)"
      const coordsPart = locationStr.split(' (')[0]
      const [lat, lng] = coordsPart.split(',').map(Number)
      
      const departmentLocation = {
        latitude: lat,
        longitude: lng,
        address: locationStr.split(' (')[1]?.replace(')', '') || '未知地址'
      }
      
      console.log('[调试] 解析后的部门位置:', departmentLocation)
      console.log('[调试] 设置前的inRange:', this.data.inRange)
      
      // 只更新departmentLocation，不覆盖inRange
      this.setData({
        departmentLocation: departmentLocation
      }, () => {
        console.log('[调试] parseDepartmentLocation setData回调后的inRange:', this.data.inRange)
      })
      
      console.log('[调试] 设置后的inRange:', this.data.inRange)
    } catch (error) {
      console.error('解析部门位置失败:', error)
    }
  },

  // 更新地图标记
  updateMapMarkers() {
    console.log('[调试] updateMapMarkers被调用')
    console.log('[调试] 当前inRange:', this.data.inRange)
    
    const markers = []
    const circles = []

    // 添加当前位置标记 - 使用蓝色箭头
    markers.push({
      id: 1,
      latitude: this.data.latitude,
      longitude: this.data.longitude,
      title: '我的位置',
      iconPath: '/images/user-location-arrow.svg',
      width: 35,
      height: 35,
      callout: {
        content: '当前位置',
        color: '#1890ff',
        fontSize: 12,
        borderRadius: 6,
        bgColor: '#ffffff',
        padding: 8,
        display: 'ALWAYS'
      }
    })

    // 如果部门设置了位置，添加部门位置标记和范围圈
    if (this.data.departmentLocation) {
      markers.push({
        id: 2,
        latitude: this.data.departmentLocation.latitude,
        longitude: this.data.departmentLocation.longitude,
        title: '打卡地点',
        iconPath: '/images/work-location-arrow.svg',
        width: 35,
        height: 35,
        callout: {
          content: '打卡位置',
          color: '#ff4d4f',
          fontSize: 12,
          borderRadius: 6,
          bgColor: '#ffffff',
          padding: 8,
          display: 'ALWAYS'
        }
      })

      // 添加范围圈 - 优化颜色显示
      circles.push({
        latitude: this.data.departmentLocation.latitude,
        longitude: this.data.departmentLocation.longitude,
        color: this.data.inRange ? '#52c41a' : '#ff7875',
        fillColor: this.data.inRange ? '#52c41a30' : '#ff787530',
        radius: this.data.distanceThreshold,
        strokeWidth: 3
      })
    }

    console.log('[调试] 设置地图标记前的inRange:', this.data.inRange)
    // 只更新markers和circles，不覆盖其他数据
    this.setData({
      markers: markers,
      circles: circles
    }, () => {
      console.log('[调试] updateMapMarkers setData回调后的inRange:', this.data.inRange)
    })
    console.log('[调试] 设置地图标记后的inRange:', this.data.inRange)
  },

  // 切换地图显示
  toggleMap() {
    this.setData({
      showMap: !this.data.showMap
    })
  },

  // 切换搜索显示
  toggleSearch() {
    this.setData({
      showSearch: !this.data.showSearch
    })
  },

  // 搜索地点
  searchPlace() {
    if (!this.data.searchKeyword.trim()) {
      wx.showToast({
        title: '请输入搜索关键词',
        icon: 'none'
      })
      return
    }

    // TODO: 请替换为您的Web服务API Key
    const apiKey = '5c3066c36f6fa333afc7f55f78c33ff0'  // 需要替换为实际的Web服务API Key
    
         // API Key已配置，继续调用高德API

    wx.showLoading({
      title: '搜索中...'
    })

    console.log('开始搜索:', this.data.searchKeyword)

    // 使用高德地图API搜索地点
    wx.request({
      url: 'https://restapi.amap.com/v3/place/text',
      data: {
        key: apiKey,
        keywords: this.data.searchKeyword,
        types: '',
        city: '',
        citylimit: false,
        children: 1,
        offset: 10,
        page: 1,
        extensions: 'all'
      },
      success: (res) => {
        wx.hideLoading()
        console.log('高德搜索响应:', res.data)
        
        if (res.data && res.data.status === '1' && res.data.pois && res.data.pois.length > 0) {
          this.setData({
            searchResults: res.data.pois.map(place => {
              const [lng, lat] = place.location.split(',')
              return {
                id: place.id,
                name: place.name,
                address: place.address || place.pname + place.cityname + place.adname,
                location: `${lat},${lng}`, // 转换为纬度,经度格式
                distance: place.distance || null
              }
            })
          })
          console.log('搜索结果:', this.data.searchResults)
        } else {
          console.log('搜索失败，API响应:', res.data)
          wx.showToast({
            title: res.data?.info || '未找到相关地点',
            icon: 'none'
          })
          this.setData({
            searchResults: []
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('搜索请求失败:', err)
        wx.showToast({
          title: '搜索失败，请检查网络',
          icon: 'none'
        })
      }
    })
  },

  // 选择搜索结果
  selectSearchResult(e) {
    const index = e.currentTarget.dataset.index
    const result = this.data.searchResults[index]
    const [lng, lat] = result.location.split(',').map(Number)
    
    this.setData({
      latitude: lat,
      longitude: lng,
      searchKeyword: result.name,
      showSearch: false,
      searchResults: []
    })
    
    this.updateMapMarkers()
  },

  // 输入搜索关键词
  onSearchInput(e) {
    this.setData({
      searchKeyword: e.detail.value
    })
  },

  // 签到
  async checkIn() {
    if (this.data.loading) return

    if (!this.data.inRange) {
      wx.showToast({
        title: '不在打卡范围内',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    try {
      const token = wx.getStorageSync('token')
      if (!token) {
        wx.showToast({
          title: '请先登录',
          icon: 'none'
        })
        return
      }

      // 获取当前位置
      const locationRes = await wx.getLocation({
        type: 'gcj02'
      })

      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/attendance/check_in`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          data: {
            latitude: locationRes.latitude,
            longitude: locationRes.longitude,
            location: `${locationRes.latitude},${locationRes.longitude}`
          },
          success: resolve,
          fail: reject
        })
      })

      if (response.statusCode === 200) {
        wx.showToast({
          title: '签到成功',
          icon: 'success'
        })
        this.getTodayAttendance()
      } else {
        const errorMsg = response.data?.error || '签到失败'
        wx.showToast({
          title: errorMsg,
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('签到失败:', error)
      wx.showToast({
        title: '签到失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 签退
  async checkOut() {
    if (this.data.loading) return

    if (!this.data.inRange) {
      wx.showToast({
        title: '不在打卡范围内',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    try {
      const token = wx.getStorageSync('token')
      if (!token) {
        wx.showToast({
          title: '请先登录',
          icon: 'none'
        })
        return
      }

      // 获取当前位置
      const locationRes = await wx.getLocation({
        type: 'gcj02'
      })

      const response = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/attendance/check_out`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          data: {
            latitude: locationRes.latitude,
            longitude: locationRes.longitude,
            location: `${locationRes.latitude},${locationRes.longitude}`
          },
          success: resolve,
          fail: reject
        })
      })

      if (response.statusCode === 200) {
        wx.showToast({
          title: '签退成功',
          icon: 'success'
        })
        this.getTodayAttendance()
      } else {
        const errorMsg = response.data?.error || '签退失败'
        wx.showToast({
          title: errorMsg,
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('签退失败:', error)
      wx.showToast({
        title: '签退失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 刷新位置
  refreshLocation() {
    this.checkLocation()
    wx.showToast({
      title: '位置已刷新',
      icon: 'success'
    })
  },

  // 签到按钮点击
  onFaceSignIn() {
    this.setData({
      showFaceModal: true,
      faceCheckStatus: 'pending',
      faceCheckTimer: 0,
      checkType: 'sign_in'
    })
    this.startFaceCheck()
  },

  // 签退按钮点击
  onFaceSignOut() {
    this.setData({
      showFaceModal: true,
      faceCheckStatus: 'pending',
      faceCheckTimer: 0,
      checkType: 'sign_out'
    })
    this.startFaceCheck()
  },

  // 开始人脸检测
  startFaceCheck() {
    console.log('[调试] 开始人脸检测')
    
    this.setData({
      showFaceModal: true,
      faceCheckStatus: 'pending',
      faceCheckTimer: 0
    })
    
    // 初始化人脸检测Canvas
    setTimeout(() => {
      this.initFaceDetectionCanvas()
      // 延迟启动人脸检测
      setTimeout(() => {
        this.startFaceDetection()
      }, 500)
    }, 100)
    
    // 启动倒计时
    this.faceCheckInterval = setInterval(() => {
      this.setData({
        faceCheckTimer: this.data.faceCheckTimer + 1
      })
      
      // 30秒超时
      if (this.data.faceCheckTimer >= 30) {
        this.endFaceCheck('timeout')
      }
    }, 1000)
    
    // 延迟开始拍照检测
    setTimeout(() => {
      this.takePhotoAndCheck()
    }, 1000)
  },

  // 拍照并上传
  takePhotoAndCheck() {
    const cameraContext = wx.createCameraContext()
    cameraContext.takePhoto({
      quality: 'high', // 提高图片质量
      success: (res) => {
        // 同时进行人脸检测和验证
        this.detectFacesAndVerify(res.tempImagePath)
      },
      fail: (error) => {
        console.error('[调试] 拍照失败:', error)
        // 继续尝试下一次拍照
        console.log('[调试] 拍照失败，继续尝试下一次拍照...')
      },
    })
  },

  // 检测人脸并验证（用于打卡验证）
  async detectFacesAndVerify(imagePath) {
    try {
      const token = wx.getStorageSync('token')
      
      // 先进行人脸检测
      wx.uploadFile({
        url: `${app.globalData.baseUrl}/api/attendance/detect_faces`,
        filePath: imagePath,
        name: 'face_image',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (detectRes) => {
          const detectData = JSON.parse(detectRes.data)
          if (detectData.success && detectData.face_boxes && detectData.face_boxes.length > 0) {
            // 绘制人脸检测框
            this.drawFaceBoxes(
              detectData.face_boxes, 
              detectData.image_width, 
              detectData.image_height
            )
            
            // 延迟一下再验证，让用户看到检测框
            setTimeout(() => {
              this.verifyFace(imagePath)
            }, 500)
          } else {
            console.log('[调试] 未检测到人脸')
            // 继续尝试下一次拍照
            setTimeout(() => {
              this.takePhotoAndCheck()
            }, 1000)
          }
        },
        fail: (err) => {
          console.error('[调试] 人脸检测请求失败:', err)
          // 直接进行验证
          this.verifyFace(imagePath)
        }
      })
    } catch (error) {
      console.error('[调试] 人脸检测失败:', error)
      // 直接进行验证
      this.verifyFace(imagePath)
    }
  },

  // 验证人脸
  verifyFace(imagePath) {
    const token = wx.getStorageSync('token')
    const verifyUrl = `${app.globalData.baseUrl}/api/attendance/verify_face`
    
    console.log('[调试] 开始人脸验证:', verifyUrl)
    console.log('[调试] 检查类型:', this.data.checkType)
    console.log('[调试] 当前尝试次数:', this.data.faceCheckTimer)
    
    wx.uploadFile({
      url: verifyUrl,
      filePath: imagePath,
      name: 'face_image',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (verifyRes) => {
        console.log('[调试] 人脸验证响应:', verifyRes)
        let verifyResult = {}
        try {
          verifyResult = JSON.parse(verifyRes.data)
          console.log('[调试] 人脸验证结果:', verifyResult)
        } catch (e) {
          console.error('[调试] 解析人脸验证响应失败:', e)
          return
        }
        
        // 如果人脸验证成功，进行实际打卡
        if (verifyRes.statusCode === 200 && verifyResult.success) {
          console.log('[调试] 人脸验证成功，开始打卡')
          this.performAttendance(imagePath)
        } else {
          console.log('[调试] 人脸验证失败:', verifyResult.message)
          // 继续尝试下一次拍照
          console.log('[调试] 继续尝试下一次拍照...')
        }
      },
      fail: (error) => {
        console.error('[调试] 人脸验证上传失败:', error)
        // 继续尝试下一次拍照
        console.log('[调试] 人脸验证失败，继续尝试下一次拍照...')
      },
    })
  },

  // 执行实际打卡操作
  performAttendance(imagePath) {
    const token = wx.getStorageSync('token')
    const apiUrl = this.data.checkType === 'sign_out'
      ? `${app.globalData.baseUrl}/api/attendance/check_out`
      : `${app.globalData.baseUrl}/api/attendance/check_in`
    
    console.log('[调试] 开始实际打卡:', apiUrl)
    
    wx.uploadFile({
      url: apiUrl,
      filePath: imagePath,
      name: 'face_image',
      formData: {
        latitude: this.data.latitude,
        longitude: this.data.longitude,
        location: this.data.location?.address || ''
      },
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (uploadRes) => {
        console.log('[调试] 打卡响应:', uploadRes)
        let result = {}
        try {
          result = JSON.parse(uploadRes.data)
          console.log('[调试] 打卡结果:', result)
        } catch (e) {
          console.error('[调试] 解析打卡响应失败:', e)
        }
        
        if (uploadRes.statusCode === 200 && result && (result.message === '签到成功' || result.message === '签退成功' || result.status === '正常' || result.status === '迟到')) {
          // 打印similarity信息
          if (result.similarity !== undefined) {
            console.log(`[调试] 打卡成功，相似度: ${result.similarity.toFixed(4)}`)
          }
          
          // 立即更新本地时间数据
          if (this.data.checkType === 'sign_in' && result.time) {
            console.log('[调试] 立即更新签到时间:', result.time)
            this.setData({
              checkInTime: result.time,
              checkInStatus: result.status || '正常'
            })
          } else if (this.data.checkType === 'sign_out' && result.time) {
            console.log('[调试] 立即更新签退时间:', result.time)
            this.setData({
              checkOutTime: result.time,
              checkOutStatus: result.status || '正常'
            })
          }
          
          this.endFaceCheck('success')
        } else {
          console.log('[调试] 打卡失败，响应:', result)
          // 打卡失败，重置验证状态，继续尝试
          this.setData({ isVerifying: false })
          console.log('[调试] 打卡失败，继续尝试下一次拍照...')
        }
      },
      fail: (error) => {
        console.error('[调试] 打卡上传失败:', error)
        // 打卡失败，继续尝试
        console.log('[调试] 打卡上传失败，继续尝试下一次拍照...')
      },
    })
  },

  // 结束检测
  endFaceCheck(status) {
    clearInterval(this.faceCheckInterval)
    this.faceCheckInterval = null
    
    // 停止人脸检测
    this.stopFaceDetection()
    
    // 重置验证状态
    this.setData({ isVerifying: false })
    
    if (status === 'success') {
      this.setData({ faceCheckStatus: 'success' })
      setTimeout(() => {
        this.setData({ showFaceModal: false })
        wx.showToast({ title: '打卡成功', icon: 'success' })
        
        // 立即检查按钮状态
        console.log('[调试] 打卡成功，立即检查按钮状态')
        this.checkButtonAvailability()
        this.debugButtonStatus()
        
        // 延迟获取最新考勤数据
        setTimeout(() => {
          this.getTodayAttendance()
          this.checkLocation()
        }, 500)
      }, 1200)
    } else if (status === 'timeout') {
      this.setData({ faceCheckStatus: 'timeout' })
      setTimeout(() => {
        this.setData({ showFaceModal: false })
        wx.showToast({ 
          title: '打卡超时，请重试', 
          icon: 'none',
          duration: 2000
        })
      }, 1200)
    } else {
      this.setData({ faceCheckStatus: 'fail' })
      setTimeout(() => {
        this.setData({ showFaceModal: false })
        wx.showToast({ title: '打卡失败', icon: 'none' })
      }, 1200)
    }
  },

  // 弹窗退出按钮
  onFaceModalExit() {
    // 停止人脸检测
    this.stopFaceDetection()
    this.endFaceCheck('fail')
  },

  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      'normal': '正常',
      'late': '迟到',
      'absent': '缺勤',
      'overtime': '加班',
      'early_leave': '早退',
      'late_leave': '晚退'
    }
    return statusMap[status] || status
  },

  // 获取状态类名
  getStatusClass(status) {
    const classMap = {
      '正常': 'normal',
      '迟到': 'late',
      '缺勤': 'absent',
      '早退': 'early-leave'
    }
    return classMap[status] || status
  },

  // 调试函数：检查按钮状态
  debugButtonStatus() {
    const { checkInTime, checkOutTime, inRange, isReady } = this.data
    console.log('=== 按钮状态调试 ===')
    console.log('checkInTime:', checkInTime)
    console.log('checkOutTime:', checkOutTime)
    console.log('inRange:', inRange, '(类型:', typeof inRange, ')')
    console.log('isReady:', isReady)
    
    // 签到按钮条件：!checkInTime && inRange === true && isReady
    const signInCondition = !checkInTime && inRange === true && isReady
    console.log('签到按钮可用条件 (!checkInTime && inRange === true && isReady):', signInCondition)
    console.log('  - !checkInTime:', !checkInTime)
    console.log('  - inRange === true:', inRange === true)
    console.log('  - isReady:', isReady)
    
    // 签退按钮条件：checkInTime && !checkOutTime && inRange === true && isReady
    const signOutCondition = checkInTime && !checkOutTime && inRange === true && isReady
    console.log('签退按钮可用条件 (checkInTime && !checkOutTime && inRange === true && isReady):', signOutCondition)
    console.log('  - checkInTime:', checkInTime)
    console.log('  - !checkOutTime:', !checkOutTime)
    console.log('  - inRange === true:', inRange === true)
    console.log('  - isReady:', isReady)
    console.log('=== 调试结束 ===')
  },

  // 检查按钮是否可用
  checkButtonAvailability() {
    const { checkInTime, checkOutTime, inRange, isReady } = this.data
    
    console.log('[按钮状态] 检查参数:', { checkInTime, checkOutTime, inRange, isReady })
    
    // 如果inRange为null，表示还未初始化，暂时禁用按钮
    if (inRange === null) {
      console.log('[按钮状态] inRange为null，按钮暂时禁用')
      return { canSignIn: false, canSignOut: false }
    }
    
    // 签到按钮：未签到且在范围内且已准备就绪
    const canSignIn = !checkInTime && inRange === true && isReady
    
    // 签退按钮：已签到但未签退且在范围内且已准备就绪
    const canSignOut = checkInTime && !checkOutTime && inRange === true && isReady
    
    console.log('[按钮状态] 签到按钮可用:', canSignIn)
    console.log('[按钮状态] 签退按钮可用:', canSignOut)
    
    return { canSignIn, canSignOut }
  },

  // 初始化人脸检测Canvas
  initFaceDetectionCanvas() {
    const query = wx.createSelectorQuery()
    query.select('#faceDetectionCanvas')
      .fields({ node: true, size: true })
      .exec((res) => {
        console.log('[调试] Canvas查询结果:', res)
        if (res[0] && res[0].node) {
          const canvas = res[0].node
          const ctx = canvas.getContext('2d')
          
          // 设置canvas尺寸
          const dpr = wx.getSystemInfoSync().pixelRatio
          canvas.width = res[0].width * dpr
          canvas.height = res[0].height * dpr
          ctx.scale(dpr, dpr)
          
          this.setData({
            faceDetectionCanvas: canvas
          })
          
          console.log('[调试] 人脸检测Canvas初始化完成')
        } else {
          console.error('[调试] Canvas初始化失败，res[0]:', res[0])
          // 使用传统方式初始化Canvas
          this.initCanvasWithContext()
        }
      })
  },

  // 使用传统方式初始化Canvas
  initCanvasWithContext() {
    const ctx = wx.createCanvasContext('faceDetectionCanvas', this)
    this.setData({
      faceDetectionCanvas: ctx
    })
    console.log('[调试] 使用传统方式初始化Canvas完成')
  },

  // 开始人脸检测
  startFaceDetection() {
    if (this.data.isDetecting) return
    
    this.setData({ isDetecting: true })
    
    // 启用实时检测，每1.5秒检测一次
    this.data.detectionInterval = setInterval(() => {
      this.detectFaces()
    }, 1500)
    
    console.log('[调试] 开始实时人脸检测')
  },

  // 停止人脸检测
  stopFaceDetection() {
    if (this.data.detectionInterval) {
      clearInterval(this.data.detectionInterval)
      this.data.detectionInterval = null
    }
    
    this.setData({ 
      isDetecting: false,
      faceBoxes: []
    })
    
    // 清除canvas
    this.clearFaceDetectionCanvas()
    
    console.log('[调试] 停止人脸检测')
  },

  // 检测人脸（仅用于显示检测框）
  async detectFaces() {
    try {
      const cameraContext = wx.createCameraContext()
      
      cameraContext.takePhoto({
        quality: 'low', // 使用低质量图片以提高速度
        success: (res) => {
          this.uploadImageForDetection(res.tempImagePath)
        },
        fail: (err) => {
          console.error('[调试] 拍照失败:', err)
        }
      })
    } catch (error) {
      console.error('[调试] 人脸检测失败:', error)
    }
  },

  // 上传图片进行人脸检测（实时检测+验证）
  async uploadImageForDetection(imagePath) {
    try {
      const token = wx.getStorageSync('token')
      if (!token) {
        console.error('[调试] 未找到token')
        return
      }

      // 先进行人脸检测
      wx.uploadFile({
        url: `${app.globalData.baseUrl}/api/attendance/detect_faces`,
        filePath: imagePath,
        name: 'face_image',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (detectRes) => {
          const detectData = JSON.parse(detectRes.data)
          if (detectData.success) {
            this.setData({
              faceBoxes: detectData.face_boxes || []
            })
            // 绘制检测框
            this.drawFaceBoxes(
              detectData.face_boxes || [], 
              detectData.image_width, 
              detectData.image_height
            )
            
            // 如果检测到人脸，进行相似度验证
            if (detectData.face_boxes && detectData.face_boxes.length > 0) {
              this.verifyFaceForRealTime(imagePath)
            }
          }
        },
        fail: (err) => {
          console.error('[调试] 人脸检测请求失败:', err)
        }
      })
    } catch (error) {
      console.error('[调试] 上传图片失败:', error)
    }
  },

  // 绘制人脸检测框
  drawFaceBoxes(faceBoxes, imageWidth = 0, imageHeight = 0) {
    const canvas = this.data.faceDetectionCanvas
    if (!canvas) return
    
    console.log('[调试] 绘制人脸框，图片尺寸:', { width: imageWidth, height: imageHeight })
    
    // 检查是否是传统Canvas上下文
    if (canvas.setFillStyle) {
      // 传统Canvas API
      this.drawFaceBoxesLegacy(canvas, faceBoxes, imageWidth, imageHeight)
    } else {
      // 新Canvas API
      this.drawFaceBoxesModern(canvas, faceBoxes, imageWidth, imageHeight)
    }
  },

  // 使用传统Canvas API绘制人脸框
  drawFaceBoxesLegacy(ctx, faceBoxes, imageWidth, imageHeight) {
    // 获取Canvas实际尺寸
    const query = wx.createSelectorQuery()
    query.select('#faceDetectionCanvas')
      .boundingClientRect((rect) => {
        if (!rect) {
          console.error('[调试] 无法获取Canvas尺寸')
          return
        }
        
        const canvasWidth = rect.width
        const canvasHeight = rect.height
        
        console.log('[调试] Canvas尺寸:', { width: canvasWidth, height: canvasHeight })
        console.log('[调试] 人脸框数据:', faceBoxes)
        
        // 清除canvas
        ctx.clearRect(0, 0, canvasWidth, canvasHeight)
        
        // 绘制检测到的人脸框
        faceBoxes.forEach((faceBox, index) => {
          const box = faceBox.box
          const confidence = faceBox.confidence
          
          console.log('[调试] 原始人脸框坐标:', box)
          
          // 使用实际图片尺寸进行坐标转换
          let scaleX, scaleY
          if (imageWidth > 0 && imageHeight > 0) {
            scaleX = canvasWidth / imageWidth
            scaleY = canvasHeight / imageHeight
          } else {
            // 如果没有图片尺寸信息，使用Canvas尺寸作为基准
            scaleX = canvasWidth / 640
            scaleY = canvasHeight / 480
          }
          
          // 计算在canvas上的坐标
          const x = box[0] * scaleX
          const y = box[1] * scaleY
          const width = (box[2] - box[0]) * scaleX
          const height = (box[3] - box[1]) * scaleY
          
          console.log('[调试] 转换后坐标:', { x, y, width, height, scaleX, scaleY })
          
          // 绘制边框
          ctx.setStrokeStyle(confidence > 0.8 ? '#00ff00' : '#ffff00')
          ctx.setLineWidth(3)
          ctx.strokeRect(x, y, width, height)
          
          // 绘制背景
          ctx.setFillStyle(confidence > 0.8 ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 255, 0, 0.1)')
          ctx.fillRect(x, y, width, height)
          
          // 绘制置信度文本
          ctx.setFillStyle('#ffffff')
          ctx.setFontSize(12)
          ctx.fillText(`置信度: ${(confidence * 100).toFixed(1)}%`, x, y - 5)
        })
        
        // 绘制到Canvas
        ctx.draw()
      })
      .exec()
  },

  // 使用新Canvas API绘制人脸框
  drawFaceBoxesModern(canvas, faceBoxes, imageWidth, imageHeight) {
    const ctx = canvas.getContext('2d')
    const canvasWidth = canvas.width / wx.getSystemInfoSync().pixelRatio
    const canvasHeight = canvas.height / wx.getSystemInfoSync().pixelRatio
    
    console.log('[调试] 新Canvas API - Canvas尺寸:', { width: canvasWidth, height: canvasHeight })
    console.log('[调试] 人脸框数据:', faceBoxes)
    
    // 清除canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight)
    
    // 绘制检测到的人脸框
    faceBoxes.forEach((faceBox, index) => {
      const box = faceBox.box
      const confidence = faceBox.confidence
      
      console.log('[调试] 原始人脸框坐标:', box)
      
      // 使用实际图片尺寸进行坐标转换
      let scaleX, scaleY
      if (imageWidth > 0 && imageHeight > 0) {
        scaleX = canvasWidth / imageWidth
        scaleY = canvasHeight / imageHeight
      } else {
        // 如果没有图片尺寸信息，使用Canvas尺寸作为基准
        scaleX = canvasWidth / 640
        scaleY = canvasHeight / 480
      }
      
      // 计算在canvas上的坐标
      const x = box[0] * scaleX
      const y = box[1] * scaleY
      const width = (box[2] - box[0]) * scaleX
      const height = (box[3] - box[1]) * scaleY
      
      console.log('[调试] 转换后坐标:', { x, y, width, height, scaleX, scaleY })
      
      // 绘制边框
      ctx.strokeStyle = confidence > 0.8 ? '#00ff00' : '#ffff00'
      ctx.lineWidth = 3
      ctx.strokeRect(x, y, width, height)
      
      // 绘制背景
      ctx.fillStyle = confidence > 0.8 ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 255, 0, 0.1)'
      ctx.fillRect(x, y, width, height)
      
      // 绘制置信度文本
      ctx.fillStyle = '#ffffff'
      ctx.font = '12px Arial'
      ctx.fillText(`置信度: ${(confidence * 100).toFixed(1)}%`, x, y - 5)
    })
  },

  // 清除人脸检测Canvas
  clearFaceDetectionCanvas() {
    const canvas = this.data.faceDetectionCanvas
    if (!canvas) return
    
    // 检查是否是传统Canvas上下文
    if (canvas.setFillStyle) {
      // 传统Canvas API
      const systemInfo = wx.getSystemInfoSync()
      canvas.clearRect(0, 0, systemInfo.windowWidth, systemInfo.windowHeight)
      canvas.draw()
    } else {
      // 新Canvas API
      const ctx = canvas.getContext('2d')
      const canvasWidth = canvas.width / wx.getSystemInfoSync().pixelRatio
      const canvasHeight = canvas.height / wx.getSystemInfoSync().pixelRatio
      ctx.clearRect(0, 0, canvasWidth, canvasHeight)
    }
  },

  // Canvas触摸事件
  onCanvasTouch(e) {
    // 可以在这里添加触摸事件处理
    console.log('[调试] Canvas被触摸:', e)
  },

  // 实时验证人脸（用于实时检测）
  verifyFaceForRealTime(imagePath) {
    // 防止重复验证
    if (this.data.isVerifying) {
      console.log('[调试] 正在验证中，跳过本次验证')
      return
    }
    
    this.setData({ isVerifying: true })
    
    const token = wx.getStorageSync('token')
    const verifyUrl = `${app.globalData.baseUrl}/api/attendance/verify_face`
    
    console.log('[调试] 实时人脸验证:', verifyUrl)
    
    wx.uploadFile({
      url: verifyUrl,
      filePath: imagePath,
      name: 'face_image',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (verifyRes) => {
        console.log('[调试] 实时验证响应:', verifyRes)
        let verifyResult = {}
        try {
          verifyResult = JSON.parse(verifyRes.data)
          console.log('[调试] 实时验证结果:', verifyResult)
        } catch (e) {
          console.error('[调试] 解析实时验证响应失败:', e)
          this.setData({ isVerifying: false })
          return
        }
        
        // 如果人脸验证成功，进行实际打卡
        if (verifyRes.statusCode === 200 && verifyResult.success) {
          console.log('[调试] 实时验证成功，开始打卡')
          this.performAttendance(imagePath)
        } else {
          console.log('[调试] 实时验证失败:', verifyResult.message)
          // 实时验证失败，重置验证状态
          this.setData({ isVerifying: false })
        }
      },
      fail: (error) => {
        console.error('[调试] 实时验证上传失败:', error)
        // 实时验证失败，重置验证状态
        this.setData({ isVerifying: false })
      },
    })
  },
})