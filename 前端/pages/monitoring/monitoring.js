Page({
  data: {
    tempImagePath: '',      // 临时图片路径
    isUploading: false,     // 上传状态
    result: null,           // 上传结果
    history: []             // 历史记录
  },

  onLoad() {
    const history = wx.getStorageSync('upload_history') || []
    this.setData({ history })
    
    // 获取token
    this.token = wx.getStorageSync('token') || '你的实际token值'
    console.log('Token:', this.token)
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
        this.setData({
          tempImagePath: tempFilePath,
          result: null
        })
      },
      fail: (err) => {
        wx.showToast({
          title: '选择图片失败',
          icon: 'error'
        })
      }
    })
  },

  // 上传图片 - 使用 Promise 包装
  uploadImage() {
    if (!this.data.tempImagePath) {
      wx.showToast({
        title: '请先选择图片',
        icon: 'none'
      })
      return
    }

    this.setData({ isUploading: true })
    
    // 创建一个 Promise 包装的 uploadFile
    const uploadPromise = () => {
      return new Promise((resolve, reject) => {
        const uploadTask = wx.uploadFile({
          url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/cat/upload-image',
          filePath: this.data.tempImagePath,
          name: 'image',
          header: {
            'Authorization': this.token
          },
          formData: {
            'user_id': '小程序用户'
          },
          success: (res) => {
            console.log('上传成功回调:', res)
            resolve(res)
          },
          fail: (err) => {
            console.log('上传失败回调:', err)
            reject(err)
          }
        })
        
        // 可选：监听上传进度
        uploadTask.onProgressUpdate((res) => {
          console.log('上传进度:', res.progress + '%')
        })
      })
    }
    
    // 执行上传
    uploadPromise()
      .then(res => {
        console.log('Promise resolved, res:', res)
        return this.handleUploadResponse(res)
      })
      .then(result => {
        console.log('处理后的结果:', result)
        
        // 更新数据和历史记录
        this.setData({ result })
        
        const newHistory = [result, ...this.data.history.slice(0, 9)]
        this.setData({ history: newHistory })
        wx.setStorageSync('upload_history', newHistory)
        
        wx.showToast({
          title: result.success ? '上传成功' : '上传失败',
          icon: result.success ? 'success' : 'error'
        })
      })
      .catch(error => {
        console.error('上传过程出错:', error)
        
        const errorResult = {
          success: false,
          message: '上传失败: ' + (error.errMsg || error.message),
          timestamp: this.formatTime(new Date())
        }
        
        this.setData({ result: errorResult })
        
        const newHistory = [errorResult, ...this.data.history.slice(0, 9)]
        this.setData({ history: newHistory })
        wx.setStorageSync('upload_history', newHistory)
        
        wx.showToast({
          title: '上传失败',
          icon: 'error'
        })
      })
      .finally(() => {
        this.setData({ isUploading: false })
      })
  },

  // 处理上传响应
  handleUploadResponse(res) {
    console.log('开始处理响应，状态码:', res.statusCode)
    
    let result = {
      timestamp: this.formatTime(new Date())
    }
    
    // 检查状态码
    if (res.statusCode === 200) {
      try {
        // 尝试解析JSON
        let responseData
        if (typeof res.data === 'string') {
          responseData = JSON.parse(res.data)
        } else {
          responseData = res.data
        }
        
        console.log('解析的响应数据:', responseData)
        
        result.success = responseData.code === 200
        result.message = responseData.msg || '上传成功'
        
        if (responseData.data) {
          result.filename = responseData.data.filename
          result.image_url = responseData.data.image_url
          result.full_url = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev' + responseData.data.image_url
          
          // 添加模拟的猫咪识别结果
          result.cat_id = 'CAT_' + Math.random().toString(36).substr(2, 9).toUpperCase()
          result.similarityText = (Math.random() * 100).toFixed(1) + '%'
          result.isNew = Math.random() > 0.5
        }
      } catch (e) {
        console.error('解析响应失败:', e)
        result.success = false
        result.message = '响应格式错误: ' + e.message
      }
    } else {
      result.success = false
      result.message = `上传失败，HTTP状态码: ${res.statusCode}`
    }
    
    return result
  },

  // 测试基础请求
  testBasicRequest() {
    wx.showLoading({ title: '测试中...' })
    
    wx.request({
      url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/',
      method: 'GET',
      success: (res) => {
        console.log('基础请求测试:', res)
        wx.hideLoading()
        wx.showModal({
          title: '服务器可访问',
          content: `状态码: ${res.statusCode}`,
          showCancel: false
        })
      },
      fail: (err) => {
        console.error('基础请求失败:', err)
        wx.hideLoading()
        wx.showModal({
          title: '无法连接服务器',
          content: '请检查网络和域名配置',
          showCancel: false
        })
      }
    })
  },

  // 使用 wx.request 模拟文件上传（用于调试）
  testRequestUpload() {
    // 注意：实际文件上传应该用 wx.uploadFile，这里只是调试
    wx.showLoading({ title: '测试上传...' })
    
    wx.request({
      url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/cat/upload-image',
      method: 'POST',
      header: {
        'Authorization': this.token,
        'Content-Type': 'application/json'
      },
      data: {
        test: '模拟上传请求',
        timestamp: new Date().getTime()
      },
      success: (res) => {
        console.log('POST请求测试:', res)
        wx.hideLoading()
        wx.showModal({
          title: 'POST测试结果',
          content: `状态码: ${res.statusCode}\n数据: ${JSON.stringify(res.data)}`,
          showCancel: false
        })
      },
      fail: (err) => {
        console.error('POST请求失败:', err)
        wx.hideLoading()
        wx.showModal({
          title: 'POST测试失败',
          content: `错误: ${err.errMsg}`,
          showCancel: false
        })
      }
    })
  },

  // 格式化时间
  formatTime(date) {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')
    const second = date.getSeconds().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`
  }
})