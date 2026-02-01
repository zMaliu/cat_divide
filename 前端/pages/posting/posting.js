const config = require('../../utils/config.js')

Page({
  data: {
    postingForm: {
      title: '',
      content: '',
      imageUrl: '' // 新增：存储图片路径
    },
    titleLength: 0,
    contentLength: 0,
    canPublish: false,
    isPublishing: false,
    // 新增：图片上传相关配置
    defaultImage: '/images/default-note.png', // 默认图片路径
    isUploadingImage: false // 图片上传状态
  },

  onLoad: function () {
    // 页面初始化
    this.updatePublishState();
  },

  // 返回按钮
  goBack: function () {
    this.checkUnsavedChanges(() => {
      wx.navigateBack();
    });
  },

  // 取消按钮 - 显示确认弹窗
  showCancelConfirm: function () {
    const hasContent = this.data.postingForm.title.trim() || this.data.postingForm.content.trim();
    
    if (hasContent) {
      wx.showModal({
        title: '确认取消',
        content: '当前内容尚未保存，确定要取消发布吗？',
        confirmText: '确定取消',
        cancelText: '继续编辑',
        confirmColor: '#FF6B6B',
        success: (res) => {
          if (res.confirm) {
            wx.navigateBack();
          }
        }
      });
    } else {
      wx.navigateBack();
    }
  },

  // 检查未保存的更改
  checkUnsavedChanges: function (callback) {
    const hasContent = this.data.postingForm.title.trim() || this.data.postingForm.content.trim();
    
    if (hasContent) {
      wx.showModal({
        title: '提示',
        content: '你有未保存的内容，确定要离开吗？',
        confirmText: '离开',
        cancelText: '留下',
        confirmColor: '#FF6B6B',
        success: (res) => {
          if (res.confirm && callback) {
            callback();
          }
        }
      });
    } else if (callback) {
      callback();
    }
  },

  // 标题输入处理
  onPostingTitleInput: function (e) {
    const value = e.detail.value;
    const length = value.length;
    
    this.setData({
      'postingForm.title': value,
      titleLength: length
    });
    
    this.updatePublishState();
  },

  // 内容输入处理
  onPostingContentInput: function (e) {
    const value = e.detail.value;
    const length = value.length;
    
    this.setData({
      'postingForm.content': value,
      contentLength: length
    });
    
    this.updatePublishState();
  },

  // 更新发布按钮状态
  updatePublishState: function () {
    const { title, content } = this.data.postingForm;
    const titleLen = this.data.titleLength;
    const contentLen = this.data.contentLength;
    
    // 检查是否可以发布：标题和内容不为空，且不超过字数限制
    const canPublish = title.trim().length > 0 && 
                      content.trim().length > 0 && 
                      titleLen <= 50 && 
                      contentLen <= 500 &&
                      !this.data.isPublishing &&
                      !this.data.isUploadingImage; // 上传图片时禁用发布
    
    this.setData({
      canPublish: canPublish
    });
  },

  // 获取状态文本
  getStatusText: function () {
    const { titleLength, contentLength, canPublish, isUploadingImage } = this.data;
    
    // 新增：图片上传中状态提示
    if (isUploadingImage) {
      return '图片上传中...';
    }
    
    if (titleLength > 50 || contentLength > 500) {
      return '字数超出限制';
    } else if (!this.data.postingForm.title.trim()) {
      return '请输入笔记标题';
    } else if (!this.data.postingForm.content.trim()) {
      return '请输入笔记内容';
    } else if (canPublish) {
      return '可以发布';
    } else {
      return '请完善信息';
    }
  },

  // 表单验证
  validateForm: function () {
    const { title, content } = this.data.postingForm;
    const { titleLength, contentLength } = this.data;
    
    // 检查必填项
    if (!title.trim()) {
      wx.showToast({
        title: '请输入笔记标题',
        icon: 'none'
      });
      return false;
    }
    
    if (!content.trim()) {
      wx.showToast({
        title: '请输入笔记内容',
        icon: 'none'
      });
      return false;
    }
    
    // 检查字数限制
    if (titleLength > 50) {
      wx.showToast({
        title: '标题不能超过50字',
        icon: 'none'
      });
      return false;
    }
    
    if (contentLength > 500) {
      wx.showToast({
        title: '内容不能超过500字',
        icon: 'none'
      });
      return false;
    }
    
    return true;
  },

  // 新增：选择并上传图片
  chooseAndUploadImage: function () {
    // 防止重复上传
    if (this.data.isUploadingImage) return;
    
    const that = this;
    
    // 选择图片
    wx.chooseImage({
      count: 1, // 仅允许选择一张图片
      sizeType: ['compressed'], // 仅压缩图
      sourceType: ['album', 'camera'], // 相册和相机
      success: function (res) {
        // 设置上传状态
        that.setData({
          isUploadingImage: true
        });
        
        // 显示加载提示
        wx.showLoading({
          title: '图片上传中...',
          mask: true
        });
        
        const tempFilePath = res.tempFilePaths[0];
        const token = wx.getStorageSync('token');
        
        // 上传图片到服务器
        wx.uploadFile({
          url: config.apiURL + '/upload/image', // 图片上传接口
          filePath: tempFilePath,
          name: 'file',
          header: {
            'Authorization': 'Bearer ' + token
          },
          success: function (uploadRes) {
            try {
              const data = JSON.parse(uploadRes.data);
              if (data.code === 200 && data.data && data.data.url) {
                // 上传成功，保存图片URL
                that.setData({
                  'postingForm.imageUrl': data.data.url
                });
                wx.showToast({
                  title: '图片上传成功',
                  icon: 'success'
                });
              } else {
                // 上传失败，使用默认图片
                that.setData({
                  'postingForm.imageUrl': that.data.defaultImage
                });
                wx.showToast({
                  title: '图片上传失败，使用默认图片',
                  icon: 'none'
                });
              }
            } catch (e) {
              // 解析失败，使用默认图片
              that.setData({
                'postingForm.imageUrl': that.data.defaultImage
              });
              wx.showToast({
                title: '图片上传失败，使用默认图片',
                icon: 'none'
              });
            }
          },
          fail: function (err) {
            console.error('图片上传失败:', err);
            // 上传失败，使用默认图片
            that.setData({
              'postingForm.imageUrl': that.data.defaultImage
            });
            wx.showToast({
              title: '图片上传失败，使用默认图片',
              icon: 'none'
            });
          },
          complete: function () {
            wx.hideLoading();
            // 恢复状态
            that.setData({
              isUploadingImage: false
            });
            that.updatePublishState();
          }
        });
      },
      fail: function (err) {
        console.error('选择图片失败:', err);
        wx.showToast({
          title: '取消图片选择',
          icon: 'none'
        });
      }
    });
  },

  // 新增：预览图片
  previewImage: function () {
    const { imageUrl, defaultImage } = this.data;
    const currentUrl = imageUrl || defaultImage;
    
    wx.previewImage({
      current: currentUrl,
      urls: [currentUrl]
    });
  },

  // 新增：移除图片
  removeImage: function () {
    this.setData({
      'postingForm.imageUrl': ''
    });
  },

  // 发布笔记
  handlePosting: function () {
    // 如果正在发布中，直接返回
    if (this.data.isPublishing) return;
    
    // 表单验证
    if (!this.validateForm()) return;
    
    const token = wx.getStorageSync('token');
    
    // 检查登录状态
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再发布笔记',
        showCancel: false,
        success: () => {
          wx.switchTab({
            url: '/pages/mine/mine'
          });
        }
      });
      return;
    }

    // 设置发布中状态
    this.setData({
      isPublishing: true,
      canPublish: false
    });

    // 显示加载提示
    wx.showLoading({
      title: '发布中...',
      mask: true
    });

    const { title, content, imageUrl } = this.data.postingForm;
    // 使用默认图片（如果没有上传图片或上传失败）
    const finalImageUrl = imageUrl || this.data.defaultImage;
    
    wx.request({
      url: config.apiURL + '/post/create',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      data: {
        title: title.trim(),
        content: content.trim(),
        imageUrl: finalImageUrl // 新增：提交图片URL
      },
      success: (res) => {
        wx.hideLoading();
        
        if (res.data.code === 200) {
          wx.showToast({
            title: '发布成功',
            icon: 'success',
            duration: 2000
          });
          
          // 清空表单
          this.setData({
            postingForm: {
              title: '',
              content: '',
              imageUrl: '' // 新增：清空图片
            },
            titleLength: 0,
            contentLength: 0
          });
          
          // 跳转到我的页面
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/mine/mine'
            });
          }, 2000);
          
        } else {
          wx.showToast({
            title: res.data.msg || '发布失败',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('发布请求失败:', err);
        wx.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none',
          duration: 2000
        });
      },
      complete: () => {
        // 恢复发布状态
        this.setData({
          isPublishing: false
        });
        this.updatePublishState();
      }
    });
  }
});