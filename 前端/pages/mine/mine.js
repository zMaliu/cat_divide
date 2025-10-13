Page({
  data: {
    // 用户信息（占位数据）
    userInfo: {
      avatar: '../../assets/avatar1.jpg',
      nickname: '明明',
      intro: '专业铲屎官',
      loveLevel: '8☆',
      postCount: 65,
      recordCount: 98, 
      fansCount: '45K',
      followingCount: 128
    },
    
    // 标签状态
    activeTab: 'publish', // publish, like, collect
    
    // 喜欢标签的子选项
    likeSubTab: 'post', // post, record
    showLikeDropdown: false,
    
    // 空状态显示
    showEmptyState: false,
    
    // 占位数据
    publishedPosts: [
      {
        id: 1,
        title: '我家小橘今天又胖了',
        image: '../../assets/demo1.jpg',
        likeCount: 42,
        time: '2小时前'
      },
      {
        id: 2, 
        title: '猫咪睡觉的100种姿势',
        image: '../../assets/Abyssinian_11.jpg',
        likeCount: 38,
        time: '1天前'
      }
    ],
    
    likedPosts: [
      {
        id: 3,
        title: '如何正确抱猫咪',
        author: '猫咪专家',
        image: '../../assets/demo1.jpg',
        time: '3小时前'
      }
    ],
    
    feedRecords: [
      {
        id: 1,
        content: '给小橘喂了猫粮',
        time: '今天 08:00',
        author: '爱猫人士'
      },
      {
        id: 2,
        content: '补充了维生素',
        time: '昨天 19:30', 
        author: '宠物医生'
      }
    ],
    
    healthRecords: [
      {
        id: 1,
        content: '体重检查：4.2kg',
        time: '2025年1月15日',
        author: '动物医院'
      }
    ],
    
    collections: [
      {
        id: 1,
        title: '猫咪护理指南',
        type: '文章',
        time: '收藏于昨天'
      }
    ]
  },

  onLoad: function() {
    // 页面加载
    this.updateEmptyState();
  },

  onShow: function() {
    // 页面显示
    this.updateEmptyState();
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