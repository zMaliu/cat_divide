Page({
  data: {
    userInfo: {
      user_id: '',
      user_name: '',
      post_count: 0,
      like_count: 0,
      follower_count: 0,
      following_count: 0
    },
    isLoading: true
  },

  onLoad: function() {
    this.getUserInfo();
  },
  
  onShow: function() {
    this.getUserInfo();
  },

  getUserInfo: function() {
    const token = wx.getStorageSync('token');
    if (!token) {
      console.log("用户未登录，跳转至登录页");
      wx.navigateTo({
        url: '/pages/login/login'
      });
      return;
    }

    this.setData({ isLoading: true });
    console.log("获取用户信息，使用token:", token);

    wx.request({
      url: 'http://localhost:5001/api/auth/userinfo',
      method: 'GET',
      header: {
        'Authorization': token
      },
      success: (res) => {
        console.log("用户信息API响应:", res.data);
        
        if (res.data && res.data.code === 200 && res.data.data && res.data.data.user) {
          const userInfo = res.data.data.user;
          
          // 确保所有需要的字段都有默认值
          const safeUserInfo = {
            user_id: userInfo.user_id || '未知ID',
            user_name: userInfo.user_name || '用户',
            post_count: userInfo.post_count || 0,
            like_count: userInfo.like_count || 0,
            follower_count: userInfo.follower_count || 0,
            following_count: userInfo.following_count || 0
          };
          
          this.setData({
            userInfo: safeUserInfo,
            isLoading: false
          });
          
          wx.setStorageSync('user_id', userInfo.user_id);
          console.log("用户信息获取成功:", safeUserInfo);
        } else {
          console.error("获取用户信息失败:", res.data);
          
          // 设置默认用户信息，避免页面错误
          this.setData({
            isLoading: false
          });
          
          // 仅在确认token真的无效时才清除
          if (res.data && res.data.code === 401) {
            console.log("token已过期，清除并重新登录");
            wx.showToast({
              title: '登录已过期，请重新登录',
              icon: 'none'
            });
            wx.removeStorageSync('token');
            wx.removeStorageSync('user_id');
            setTimeout(() => {
              wx.navigateTo({
                url: '/pages/login/login'
              });
            }, 1500);
          } else {
            wx.showToast({
              title: res.data.msg || '获取信息失败，请重试',
              icon: 'none'
            });
          }
        }
      },
      fail: (err) => {
        console.error("请求失败:", err);
        this.setData({ isLoading: false });
        wx.showToast({
          title: '网络错误，请检查连接',
          icon: 'none'
        });
      }
    });
  },

  // 编辑个人资料
  editProfile: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 退出登录，清除本地存储并跳转到登录页面
  handleLogout: function() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      confirmColor: '#5B5FEF',
      success: (res) => {
        if (res.confirm) {
          console.log("用户确认退出登录，清除token和user_id");
          wx.removeStorageSync('token');
          wx.removeStorageSync('user_id');
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
          setTimeout(() => {
            wx.navigateTo({
              url: '/pages/login/login'
            });
          }, 1500);
        }
      }
    });
  },

  // 跳转到发表作品页面
  onPosting: function() {
    wx.navigateTo({
      url: '/pages/posting/posting'
    });
  },

  // 跳转到我的作品页面
  goToMyPosts: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 跳转到我点赞的作品页面
  goToLikedPosts: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 跳转到我的粉丝页面
  goToFollowers: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 跳转到我的关注页面
  goToFollowing: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 跳转到账号设置页面
  goToSettings: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 跳转到帮助与反馈页面
  goToHelp: function() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  }
});