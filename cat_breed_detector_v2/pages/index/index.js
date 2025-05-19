const app = getApp()

Page({
  data: {
    imagePath: '',
    result: null
  },

  onLoad: function() {
    // 检查相机权限
    wx.authorize({
      scope: 'scope.camera',
      success() {
        console.log('已获得相机权限')
      },
      fail() {
        wx.showModal({
          title: '提示',
          content: '需要相机权限才能使用拍照功能',
          showCancel: false
        })
      }
    })
  },

  takePhoto: function() {
    const ctx = wx.createCameraContext()
    ctx.takePhoto({
      quality: 'high',
      success: (res) => {
        this.setData({
          imagePath: res.tempImagePath
        })
      },
      fail: (err) => {
        console.error('拍照失败：', err)
        wx.showToast({
          title: '拍照失败',
          icon: 'none'
        })
      }
    })
  },

  chooseImage: function() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album'],
      success: (res) => {
        this.setData({
          imagePath: res.tempFilePaths[0]
        })
      }
    })
  },

  retake: function() {
    this.setData({
      imagePath: '',
      result: null
    })
  },

  analyzeImage: function() {
    if (!this.data.imagePath) {
      wx.showToast({
        title: '请先选择图片',
        icon: 'none'
      })
      return
    }

    wx.showLoading({
      title: '识别中...',
    })

    // 上传图片到服务器
    wx.uploadFile({
      url: 'http://10.45.150.95:5001/analyze',
      filePath: this.data.imagePath,
      name: 'image',
      success: (res) => {
        try {
          const result = JSON.parse(res.data)
          this.setData({
            result: {
              breed: result.breed,
              confidence: (result.confidence * 100).toFixed(2),
              description: result.description
            }
          })
        } catch (e) {
          console.error('解析结果失败：', e)
          wx.showToast({
            title: '解析结果失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('上传失败：', err)
        wx.showToast({
          title: '上传失败',
          icon: 'none'
        })
      },
      complete: () => {
        wx.hideLoading()
      }
    })
  },

  error: function(e) {
    console.error('相机错误：', e)
    wx.showToast({
      title: '相机错误',
      icon: 'none'
    })
  }
}) 