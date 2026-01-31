const config = require('../../utils/config.js')

Page({
  data: {
    // 用户信息（初始为空）
    userInfo: {
      avatar: '../../assets/avatar2.jpg',
      nickname: '明明',
      intro: '',
      loveLevel: '0☆',
      postCount: 0,
      recordCount: 0, 
      fansCount: 0,
      followingCount: 0
    },
    isLoggedIn: false,
    
    // 标签状态
    activeTab: 'publish', // publish, like, collect
    
    // 喜欢标签的子选项
    likeSubTab: 'post', // post, record
    showLikeDropdown: false,
    
    // 空状态显示
    showEmptyState: false,
    
    // 占位数据
    // publishedPosts: [
    //   {
    //     id: 1,
    //     title: '我家小橘今天又胖了',
    //     image: '../../assets/demo1.jpg',
    //     likeCount: 42,
    //     time: '2小时前'
    //   },
    //   {
    //     id: 2, 
    //     title: '猫咪睡觉的100种姿势',
    //     image: '../../assets/Abyssinian_11.jpg',
    //     likeCount: 38,
    //     time: '1天前'
    //   }
    // ],
    
    // likedPosts: [
    //   {
    //     id: 3,
    //     title: '如何正确抱猫咪',
    //     author: '猫咪专家',
    //     image: '../../assets/demo1.jpg',
    //     time: '3小时前'
    //   }
    // ],
    
    // feedRecords: [
    //   {
    //     id: 1,
    //     content: '给小橘喂了猫粮',
    //     time: '今天 08:00',
    //     author: '爱猫人士'
    //   },
    //   {
    //     id: 2,
    //     content: '补充了维生素',
    //     time: '昨天 19:30', 
    //     author: '宠物医生'
    //   }
    // ],
    
    // healthRecords: [
    //   {
    //     id: 1,
    //     content: '体重检查：4.2kg',
    //     time: '2025年1月15日',
    //     author: '动物医院'
    //   }
    // ],
    
    // collections: [
    //   {
    //     id: 1,
    //     title: '猫咪护理指南',
    //     type: '文章',
    //     time: '收藏于昨天'
    //   }
    // ]
  },

  onLoad: function() {
    // 页面加载
    this.loadUserInfo();
    this.updateEmptyState();
  },

  onShow: function() {
    // 页面显示时重新加载（可能修改了资料）
    this.loadUserInfo();
    this.updateEmptyState();
  },

  // 加载用户信息
  loadUserInfo: function() {
    const token = wx.getStorageSync('token');
    const userId = wx.getStorageSync('user_id');
    
    if (!token || !userId) {
      // 未登录
      this.setData({
        isLoggedIn: false,
        userInfo: {
          avatar: '../../assets/avatar2.png',
          nickname: '明明',
        //   intro: '点击登录',
          loveLevel: '0☆',
          postCount: 0,
          recordCount: 0,
          fansCount: 0,
          followingCount: 0
        }
      });
      return;
    }

    this.setData({ isLoggedIn: true });

    // 获取用户基本信息
    wx.request({
      url: config.apiURL + '/auth/get_user_info',
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token
      },
      success: (res) => {
        if (res.data.code === 200) {
          const userData = res.data.data;
          
          // 映射到页面数据格式
          this.setData({
            'userInfo.nickname': userData.user_name || '用户',
            'userInfo.avatar': userData.user_avatar || '../../assets/avatar2.png',
            'userInfo.intro': userData.user_bio || '这个人很懒，什么都没写',
            'userInfo.loveLevel': '0☆'  // 暂时固定，可以后续从其他API获取
          });

          // 获取用户统计数据
          this.loadUserStats(userId, token);
        } else if (res.data.code === 401) {
          // token失效，清除登录状态
          wx.removeStorageSync('token');
          wx.removeStorageSync('user_id');
          this.setData({ isLoggedIn: false });
        }
      },
      fail: (err) => {
        console.error('获取用户信息失败:', err);
      }
    });
  },

  // 加载用户统计数据
  loadUserStats: function(userId, token) {
    // 获取用户发布的帖子数、粉丝数、关注数
    wx.request({
      url: config.apiURL + '/user/stats/' + userId,
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token
      },
      success: (res) => {
        if (res.data.code === 200) {
          const stats = res.data.data;
          this.setData({
            'userInfo.postCount': stats.post_count || 0,
            'userInfo.fansCount': stats.follower_count || 0,
            'userInfo.followingCount': stats.following_count || 0,
            'userInfo.recordCount': stats.like_count || 0
          });
        }
      },
      fail: (err) => {
        console.error('获取用户统计失败:', err);
        // 失败时使用默认值
        this.setData({
          'userInfo.postCount': 0,
          'userInfo.fansCount': 0,
          'userInfo.followingCount': 0,
          'userInfo.recordCount': 0
        });
      }
    });
  },

  // 更新空状态
  updateEmptyState: function() {
    let showEmpty = false;
    
    if (this.data.activeTab === 'publish') {
      showEmpty = this.data.publishedPosts.length === 0;
    } else if (this.data.activeTab === 'like') {
      if (this.data.likeSubTab === 'post') {
        showEmpty = this.data.likedPosts.length === 0;
      } else if (this.data.likeSubTab === 'record') {
        showEmpty = this.data.feedRecords.length === 0 && this.data.healthRecords.length === 0;
      }
    } else if (this.data.activeTab === 'collect') {
      showEmpty = this.data.collections.length === 0;
    }
    
    this.setData({
      showEmptyState: showEmpty
    });
  },

  // 标签切换
  onTabChange: function(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({
      activeTab: tab,
      showLikeDropdown: false
    });
    this.updateEmptyState();
  },

  // 喜欢标签的下拉切换
  onLikeDropdownToggle: function() {
    this.setData({
      showLikeDropdown: !this.data.showLikeDropdown
    });
  },

  onLikeSubTabChange: function(e) {
    const subTab = e.currentTarget.dataset.subtab;
    this.setData({
      likeSubTab: subTab,
      showLikeDropdown: false
    });
    this.updateEmptyState();
  },

  // 头像点击
  onAvatarTap: function() {
    wx.showToast({
      title: '头像功能开发中',
      icon: 'none'
    });
  },

  // 编辑个人资料
  onEditProfile: function() {
    wx.navigateTo({
      url: '/pages/editProfile/editProfile'
    });
  },

  // 设置
  onSettings: function() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    });
  },

  // 关注列表
  onFollowingList: function() {
    wx.showModal({
      title: '我的关注',
      content: '关注列表功能开发中\n\n当前关注：' + this.data.userInfo.followingCount + '人',
      showCancel: false
    });
  },

  // 粉丝、帖子、记录点击
  onStatsClick: function(e) {
    const type = e.currentTarget.dataset.type;
    wx.showToast({
      title: type + '详情开发中',
      icon: 'none'
    });
  },

  // 发布作品
  onPosting: function() {
    wx.navigateTo({
      url: '/pages/posting/posting'
    });
  },

  // 帖子详情
  onPostDetail: function(e) {
    const post = e.currentTarget.dataset.post;
    wx.navigateTo({
      url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`
    });
  }
});