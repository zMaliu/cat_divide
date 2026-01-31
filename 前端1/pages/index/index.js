
// const app = getApp()

// Page({
//   data: {
//     imagePath: '',
//     result: null
//   },

//   onLoad: function() {
//     // 检查相机权限
//     wx.authorize({
//       scope: 'scope.camera',
//       success() {
//         console.log('已获得相机权限')
//       },
//       fail() {
//         wx.showModal({
//           title: '提示',
//           content: '需要相机权限才能使用拍照功能',
//           showCancel: false
//         })
//       }
//     })
//   },

//   takePhoto: function() {
//     const ctx = wx.createCameraContext()
//     ctx.takePhoto({
//       quality: 'high',
//       success: (res) => {
//         this.setData({
//           imagePath: res.tempImagePath
//         })
//       },
//       fail: (err) => {
//         console.error('拍照失败：', err)
//         wx.showToast({
//           title: '拍照失败',
//           icon: 'none'
//         })
//       }
//     })
//   },

//   chooseImage: function() {
//     wx.chooseImage({
//       count: 1,
//       sizeType: ['compressed'],
//       sourceType: ['album'],
//       success: (res) => {
//         this.setData({
//           imagePath: res.tempFilePaths[0]
//         })
//       }
//     })
//   },

//   retake: function() {
//     this.setData({
//       imagePath: '',
//       result: null
//     })
//   },

//   analyzeImage: function() {
//     if (!this.data.imagePath) {
//       wx.showToast({
//         title: '请先选择图片',
//         icon: 'none'
//       })
//       return
//     }

//     // 获取认证令牌
//     const token = wx.getStorageSync('token')
//     if (!token) {
//       wx.showToast({
//         title: '请先登录',
//         icon: 'none'
//       })
//       setTimeout(() => {
//         wx.switchTab({
//           url: '/pages/mine/mine'
//         })
//       }, 1500)
//       return
//     }

//     wx.showLoading({
//       title: '识别中...',
//     })

//     wx.uploadFile({
//       url: config.apiURL + '/yolo/detect-cat',
//       method:'POST',
//       filePath: this.data.imagePath,
//       name: 'image',
//       header: {
//         'Authorization': `Bearer ${token}`
//       },
//       success: (res) => {
//         try {
//           const result = JSON.parse(res.data)
//           console.log('服务器返回结果:', result)
          
//           if (result.code === 200 && result.data) {
//             this.setData({
//               result: {
//                 breed: result.data.breed || '未知品种',
//                 confidence: result.data.confidence ? (result.data.confidence * 100).toFixed(2) : '0.00',
//                 description: result.data.description || '暂无描述'
//               }
//             })
//           } else {
//             console.error('识别失败:', result.msg)
//             wx.showToast({
//               title: result.msg || '识别失败',
//               icon: 'none'
//             })
//             this.setData({
//               result: null
//             })
//           }
//         } catch (e) {
//           console.error('解析结果失败：', e)
//           wx.showToast({
//             title: '解析结果失败',
//             icon: 'none'
//           })
//           this.setData({
//             result: null
//           })
//         }
//       },
//       fail: (err) => {
//         console.error('上传失败：', err)
//         wx.showToast({
//           title: '上传失败',
//           icon: 'none'
//         })
//         this.setData({
//           result: null
//         })
//       },
//       complete: () => {
//         wx.hideLoading()
//       }
//     })
//   },

//   error: function(e) {
//     console.error('相机错误：', e)
//     wx.showToast({
//       title: '相机错误',
//       icon: 'none'
//     })
//   }
// })






const app = getApp()

const config = require('../../utils/config.js')

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
      url: config.apiURL + '/yolo/detect-cat',
      method: 'POST',
      filePath: this.data.imagePath,
      name: 'image',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        try {
          const result = JSON.parse(res.data)
          console.log('服务器返回结果:', result)
          
          if (result.code === 200 && result.data) {
            const detections = result.data.detections || []
            
            if (detections.length === 0) {
              // 未检测到猫咪
              wx.showToast({
                title: '未检测到猫咪',
                icon: 'none'
              })
              this.setData({
                result: {
                  breed: '未检测到',
                  confidence: '0.00',
                  description: '图片中未检测到猫咪，请尝试更换一张图片或确保图片中有清晰的猫咪。'
                }
              })
            } else {
              // 检测到猫咪，取第一只或平均值
              const firstCat = detections[0]
              const avgConfidence = detections.reduce((sum, det) => sum + det.confidence, 0) / detections.length
              
              // 生成描述
              let description = ''
              if (detections.length === 1) {
                description = '成功识别到1只猫咪！这是一只可爱的猫咪，具有独特的外貌特征。'
              } else {
                description = `成功识别到${detections.length}只猫咪！图片中有多只猫咪，它们都很可爱。`
              }
              
              this.setData({
                result: {
                  breed: firstCat.class || '猫咪',
                  confidence: (avgConfidence * 100).toFixed(2),
                  description: description
                }
              })
              
              wx.showToast({
                title: '识别成功',
                icon: 'success'
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