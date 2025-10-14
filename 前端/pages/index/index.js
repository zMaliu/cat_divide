
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

    // 获取认证令牌
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/mine/mine'
        })
      }, 1500)
      return
    }

    wx.showLoading({
      title: '识别中...',
    })

    wx.uploadFile({
      url: 'http://localhost:5001/api/yolo/detect-cat',
      method:'POST',
      filePath: this.data.imagePath,
      name: 'image',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        try {
          const result = JSON.parse(res.data)
          console.log('服务器返回结果:', result)
          
          if (result.code === 200 && result.data && result.data.detections) {
            const detections = result.data.detections
            
            if (detections.length > 0) {
              // 取置信度最高的检测结果
              const bestDetection = detections.reduce((prev, current) => 
                (prev.confidence > current.confidence) ? prev : current
              )
              
              // 获取品种描述
              const breedDescriptions = {
                'Abyssinian': '阿比西尼亚猫是一种活泼、聪明的短毛猫，具有独特的"刻度"毛色。',
                'Bengal': '孟加拉猫具有野生豹猫的外观，毛色斑纹独特，性格活跃。',
                'Birman': '伯曼猫是长毛猫，具有蓝色眼睛和白色手套状脚掌。',
                'Bombay': '孟买猫全身黑色，被称为"小黑豹"，性格温和友善。',
                'British_Shorthair': '英国短毛猫体型圆润，毛质厚实，性格温和稳重。',
                'Egyptian_Mau': '埃及猫是唯一天然斑点的家猫品种，速度很快。',
                'Maine_Coon': '缅因猫是大型长毛猫，性格温和，适应能力强。',
                'Persian': '波斯猫是长毛猫的代表，面部扁平，毛质柔软。',
                'Ragdoll': '布偶猫性格温顺，喜欢被抱，毛色美丽。',
                'Russian_Blue': '俄罗斯蓝猫具有银蓝色短毛，性格安静优雅。',
                'Siamese': '暹罗猫具有独特的重点色，性格活跃，喜欢交流。',
                'Sphynx': '斯芬克斯猫是无毛猫品种，皮肤温暖，性格外向。'
              }
              
              this.setData({
                result: {
                  breed: bestDetection.class || '未知品种',
                  confidence: (bestDetection.confidence * 100).toFixed(2),
                  description: breedDescriptions[bestDetection.class] || '这是一只可爱的猫咪！',
                  bbox: bestDetection.bbox,
                  allDetections: detections
                }
              })
            } else {
              wx.showToast({
                title: '未检测到猫咪',
                icon: 'none'
              })
              this.setData({
                result: null
              })
            }
          } else {
            console.error('识别失败:', result.msg)
            wx.showToast({
              title: result.msg || '识别失败',
              icon: 'none'
            })
            this.setData({
              result: null
            })
          }
        } catch (e) {
          console.error('解析结果失败：', e)
          wx.showToast({
            title: '解析结果失败',
            icon: 'none'
          })
          this.setData({
            result: null
          })
        }
      },
      fail: (err) => {
        console.error('上传失败：', err)
        wx.showToast({
          title: '上传失败',
          icon: 'none'
        })
        this.setData({
          result: null
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