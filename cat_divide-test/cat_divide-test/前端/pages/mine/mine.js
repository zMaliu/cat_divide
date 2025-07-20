Page({
  data: {
    userInfo: {},
    userPosts: []
  },

  onLoad: function() {
    this.getUserInfo();
  },

  onShow: function() {
    this.getUserInfo();
    if (wx.getStorageSync('token')) {
      this.getUserPosts();
    }
  },

  // 获取用户信息
  getUserInfo: function() {
    const userInfo = wx.getStorageSync('userInfo') || {};
    this.setData({ userInfo });
  },

  // 获取用户发布的作品
  getUserPosts: function() {
    const token = wx.getStorageSync('token');
    if (!token) return;

    wx.showLoading({ title: '加载中...' });

    wx.request({
      url: 'http://localhost:5001/api/user/posts',
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token
      },
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({
            userPosts: res.data.data.posts || []
          });
        } else {
          wx.showToast({
            title: res.data.msg || '获取作品失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none'
        });
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  },

  // 前往登录页
  goLogin: function() {
    wx.navigateTo({
      url: '/pages/login/login'
    });
  },

  // 前往发布页
  onPosting: function() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      setTimeout(() => {
        this.goLogin();
      }, 1500);
      return;
    }
    
    wx.switchTab({
      url: '/pages/posting/posting'
    });
  },

  // 查看发布的作品
  viewPost: function(e) {
    const postId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/post-detail/post-detail?id=${postId}`
    });
  },

  // 打开设置页面
  openSettings: function() {
    wx.showToast({
      title: '设置功能开发中',
      icon: 'none'
    });
  },

  // 退出登录
  logout: function() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除用户信息和令牌
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          
          this.setData({
            userInfo: {},
            userPosts: []
          });
          
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
        }
      }
    });
  }
});