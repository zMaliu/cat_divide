const config = require('../../utils/config.js')

Page({
  data: {
    postingForm: {
      title: '',
      content: ''
    },
    titleLength: 0,
    contentLength: 0,
    canPublish: false,
    isPublishing: false
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
                      !this.data.isPublishing;
    
    this.setData({
      canPublish: canPublish
    });
  },

  // 获取状态文本
  getStatusText: function () {
    const { titleLength, contentLength, canPublish } = this.data;
    
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

    const { title, content } = this.data.postingForm;
    
    wx.request({
      url: config.apiURL + '/post/create',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      data: {
        title: title.trim(),
        content: content.trim()
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
              content: ''
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