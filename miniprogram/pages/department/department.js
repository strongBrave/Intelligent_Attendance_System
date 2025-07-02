const app = getApp()

Page({
  data: {
    departments: [],
    loading: false,
    submitting: false,
    showModal: false,
    isEdit: false,
    form: {
      id: null,
      name: '',
      sign_in_time: '09:00',
      sign_out_time: '18:00',
      late_threshold: '09:30',
      absent_threshold: '10:00',
      early_leave_threshold: '17:30',
      location: ''
    }
  },

  onLoad() {
    this.loadDepartments()
  },

  onShow() {
    this.loadDepartments()
  },

  // 加载部门列表
  loadDepartments() {
    this.setData({ loading: true })
    
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    wx.request({
      url: `${app.globalData.baseUrl}/api/admin/departments`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            departments: res.data.departments || []
          })
        } else {
          wx.showToast({
            title: res.data.error || '获取部门列表失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('获取部门列表失败:', err)
        wx.showToast({
          title: '获取部门列表失败',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({ loading: false })
      }
    })
  },

  // 显示新增对话框
  showAddDialog() {
    this.setData({
      showModal: true,
      isEdit: false,
      form: {
        id: null,
        name: '',
        sign_in_time: '09:00',
        sign_out_time: '18:00',
        late_threshold: '09:30',
        absent_threshold: '10:00',
        early_leave_threshold: '17:30',
        location: ''
      }
    })
  },

  // 编辑部门
  editDepartment(e) {
    const dept = e.currentTarget.dataset.dept
    this.setData({
      showModal: true,
      isEdit: true,
      form: {
        id: dept.id,
        name: dept.name,
        sign_in_time: dept.sign_in_time || '09:00',
        sign_out_time: dept.sign_out_time || '18:00',
        late_threshold: dept.late_threshold || '09:30',
        absent_threshold: dept.absent_threshold || '10:00',
        early_leave_threshold: dept.early_leave_threshold || '17:30',
        location: dept.location || ''
      }
    })
  },

  // 删除部门
  deleteDepartment(e) {
    const dept = e.currentTarget.dataset.dept
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除部门"${dept.name}"吗？`,
      success: (res) => {
        if (res.confirm) {
          this.confirmDelete(dept.id)
        }
      }
    })
  },

  // 确认删除
  confirmDelete(deptId) {
    const token = wx.getStorageSync('token')
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/admin/departments/${deptId}`,
      method: 'DELETE',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          })
          this.loadDepartments()
        } else {
          wx.showToast({
            title: res.data.error || '删除失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('删除部门失败:', err)
        wx.showToast({
          title: '删除失败',
          icon: 'none'
        })
      }
    })
  },

  // 时间选择器变化
  onTimeChange(e) {
    const type = e.currentTarget.dataset.type
    const value = e.detail.value
    
    this.setData({
      [`form.${type}`]: value
    })
  },

  // 地图选点
  chooseLocation() {
    wx.chooseLocation({
      success: (res) => {
        const location = `${res.latitude},${res.longitude} (${res.name || res.address})`
        this.setData({
          'form.location': location
        })
      },
      fail: (err) => {
        console.error('选择位置失败:', err)
        if (err.errMsg.includes('auth deny')) {
          wx.showModal({
            title: '位置权限',
            content: '需要获取位置权限才能选择打卡位置，请在设置中开启位置权限',
            showCancel: false
          })
        } else {
          wx.showToast({
            title: '选择位置失败',
            icon: 'none'
          })
        }
      }
    })
  },

  // 提交表单
  submitForm(e) {
    const formData = e.detail.value
    
    // 验证表单
    if (!formData.name.trim()) {
      wx.showToast({
        title: '请输入部门名称',
        icon: 'none'
      })
      return
    }

    this.setData({ submitting: true })
    
    const token = wx.getStorageSync('token')
    const url = this.data.isEdit 
      ? `${app.globalData.baseUrl}/api/admin/departments/${this.data.form.id}`
      : `${app.globalData.baseUrl}/api/admin/departments`
    
    const method = this.data.isEdit ? 'PUT' : 'POST'
    
    const submitData = {
      name: formData.name,
      sign_in_time: this.data.form.sign_in_time,
      sign_out_time: this.data.form.sign_out_time,
      late_threshold: this.data.form.late_threshold,
      absent_threshold: this.data.form.absent_threshold,
      early_leave_threshold: this.data.form.early_leave_threshold,
      location: this.data.form.location
    }

    wx.request({
      url: url,
      method: method,
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: submitData,
      success: (res) => {
        if (res.statusCode === 200 || res.statusCode === 201) {
          wx.showToast({
            title: this.data.isEdit ? '更新成功' : '添加成功',
            icon: 'success'
          })
          this.hideModal()
          this.loadDepartments()
        } else {
          wx.showToast({
            title: res.data.error || '操作失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('提交表单失败:', err)
        wx.showToast({
          title: '操作失败',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({ submitting: false })
      }
    })
  },

  // 隐藏弹窗
  hideModal() {
    this.setData({ showModal: false })
  },

  // 阻止事件冒泡
  stopPropagation() {
    // 阻止事件冒泡
  }
}) 