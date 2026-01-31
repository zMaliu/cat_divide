const config = require('../../utils/config.js')

Page({
    data: {
    // 分类相关
    activeCategory: 'share', // share, help, knowledge
    categories: [
      { key: 'share', name: '分享' },
      { key: 'help', name: '求助' },
      { key: 'knowledge', name: '科普' }
    ],
    
    // 排序相关
    currentSort: 'hot', // hot, time
    showSortDropdown: false,
    sortOptions: [
      { key: 'hot', name: '按热度' },
      { key: 'time', name: '按时间' }
    ],
    
    // 数据相关
    discussions: [],
    isLoading: false,
    loadError: false,
    isLoadingMore: false,
    noMoreData: false,
    currentPage: 1,
    
    // 用户token（用于点赞功能）
    userToken: ''
  },

  onLoad: function () {
    // 获取用户token
    const token = wx.getStorageSync('userToken');
    this.setData({ userToken: token });
    
    this.loadDiscussions();
  },

  onShow: function () {
    // 页面显示时可以刷新数据
  },

  onPullDownRefresh: function () {
    this.refreshDiscussions();
  },

  // 触底加载更多
  onReachBottom: function() {
    this.loadMoreDiscussions();
  },

  loadDiscussions: function (isRefresh = false) {
    if (!isRefresh) {
      this.setData({
        isLoading: true,
        loadError: false
      });
    }

    // TODO: 实现真实API调用，当前使用模拟数据
    const mockData = this.getMockDiscussions();
    
    setTimeout(() => {
      const sortedData = this.sortDiscussions(mockData);
      this.setData({
        isLoading: false,
        discussions: sortedData,
        currentPage: 1,
        noMoreData: false
      });
      
      if (isRefresh) {
        wx.stopPullDownRefresh();
      }
    }, 800);
  },

  // 刷新数据
  refreshDiscussions: function() {
    this.loadDiscussions(true);
  },

  // 加载更多
  loadMoreDiscussions: function() {
    if (this.data.isLoadingMore || this.data.noMoreData) return;
    
    this.setData({ isLoadingMore: true });
    
    // 模拟加载更多数据
    setTimeout(() => {
      const currentDiscussions = [...this.data.discussions];
      const newData = this.getMockDiscussions(this.data.currentPage + 1);
      
      if (newData.length === 0) {
        this.setData({
          isLoadingMore: false,
          noMoreData: true
        });
      } else {
        const sortedNewData = this.sortDiscussions(newData);
        this.setData({
          discussions: [...currentDiscussions, ...sortedNewData],
          isLoadingMore: false,
          currentPage: this.data.currentPage + 1
        });
      }
    }, 500);
  },

  // 获取模拟数据
  getMockDiscussions: function(page = 1) {
    const allMockData = [
      {
        article_id: 1,
        title: "我家小橘的日常分享",
        content: "今天小橘又做了很多可爱的事情，想和大家分享一下...",
        author: "橘猫妈妈",
        author_avatar: "../../assets/avatar1.jpg",
        img: "../../assets/demo1.jpg",
        like_count: 128,
        is_liked: false,
        reply_count: 23,
        category: "share",
        create_time: "2024-01-15 14:30:00",
        time: "2小时前"
      },
      {
        article_id: 2,
        title: "猫咪突然不吃东西了，急求帮助！",
        content: "我家猫咪从昨天开始就不怎么吃东西，精神也不太好...",
        author: "担心的铲屎官",
        author_avatar: "../../assets/default-avatar.png",
        img: "../../assets/Abyssinian_11.jpg",
        like_count: 56,
        is_liked: true,
        reply_count: 34,
        category: "help",
        create_time: "2024-01-15 12:15:00",
        time: "4小时前"
      },
      {
        article_id: 3,
        title: "科普：猫咪的各种叫声含义",
        content: "很多新手铲屎官不知道猫咪不同叫声代表什么意思...",
        author: "宠物专家",
        author_avatar: "../../assets/avatar1.jpg",
        img: "../../assets/demo1.jpg",
        like_count: 89,
        is_liked: false,
        reply_count: 12,
        category: "knowledge",
        create_time: "2024-01-15 09:00:00",
        time: "7小时前"
      },
      {
        article_id: 4,
        title: "今天带猫咪去体检啦！",
        content: "第一次带小猫去宠物医院，整个过程记录分享给大家...",
        author: "新手铲屎官",
        author_avatar: "../../assets/default-avatar.png",
        img: "../../assets/Abyssinian_11.jpg",
        like_count: 76,
        is_liked: false,
        reply_count: 18,
        category: "share",
        create_time: "2024-01-14 16:20:00",
        time: "1天前"
      }
    ];
    
    // 根据当前分类筛选
    const filteredData = this.data.activeCategory === 'all' 
      ? allMockData 
      : allMockData.filter(item => item.category === this.data.activeCategory);
    
    // 模拟分页
    const pageSize = 10;
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    
    return page === 1 ? filteredData : []; // 简化分页逻辑
  },

  // 排序讨论数据
  sortDiscussions: function(data) {
    const sortType = this.data.currentSort;
    return [...data].sort((a, b) => {
      if (sortType === 'hot') {
        return b.like_count - a.like_count;
      } else {
        return new Date(b.create_time) - new Date(a.create_time);
      }
    });
  },

  // 分类切换
  onCategoryChange: function(e) {
    const category = e.currentTarget.dataset.category;
    if (category === this.data.activeCategory) return;
    
    this.setData({ 
      activeCategory: category,
      discussions: [],
      currentPage: 1,
      noMoreData: false
    });
    
    this.loadDiscussions();
  },

  // 排序下拉菜单切换
  onSortDropdownToggle: function() {
    this.setData({ 
      showSortDropdown: !this.data.showSortDropdown 
    });
  },

  // 排序方式切换
  onSortChange: function(e) {
    const sort = e.currentTarget.dataset.sort;
    if (sort === this.data.currentSort) {
      this.setData({ showSortDropdown: false });
      return;
    }
    
    this.setData({ 
      currentSort: sort,
      showSortDropdown: false
    });
    
    // 重新排序当前数据
    const sortedData = this.sortDiscussions(this.data.discussions);
    this.setData({ discussions: sortedData });
  },

  // 点赞/取消点赞
  toggleLike: function(e) {
    const { postId, index } = e.currentTarget.dataset;
    const token = this.data.userToken;
    
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }
    
    const discussions = [...this.data.discussions];
    const post = discussions[index];
    
    if (!post) return;
    
    const isLiked = post.is_liked;
    const url = `${config.apiURL}/like/${postId}`;
    const method = isLiked ? 'DELETE' : 'POST';
    
    // 乐观更新UI
    post.is_liked = !isLiked;
    post.like_count = isLiked ? (post.like_count - 1) : (post.like_count + 1);
    discussions[index] = post;
    
    this.setData({ discussions });
    
    // 调用API
    wx.request({
      url: url,
      method: method,
      header: {
        'Authorization': token,
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.data.code !== 200) {
          // 失败时回滚UI
          post.is_liked = isLiked;
          post.like_count = isLiked ? (post.like_count + 1) : (post.like_count - 1);
          discussions[index] = post;
          this.setData({ discussions });
          
          wx.showToast({
            title: res.data.message || '操作失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        // 失败时回滚UI
        post.is_liked = isLiked;
        post.like_count = isLiked ? (post.like_count + 1) : (post.like_count - 1);
        discussions[index] = post;
        this.setData({ discussions });
        
        wx.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none'
        });
      }
    });
  },

  // 讨论详情点击
  onDiscussionTap: function (e) {
    const discussion = e.currentTarget.dataset.discussion;
    // TODO: 跳转到讨论详情页面
    wx.showToast({
      title: '讨论详情功能开发中',
      icon: 'none'
    });
  },

  // 发布新讨论
  onNewDiscussion: function () {
    // TODO: 跳转到发布讨论页面
    wx.navigateTo({
      url: '/pages/posting/posting?type=discussion'
    }).catch(() => {
      wx.showToast({
        title: '发布讨论功能开发中',
        icon: 'none'
      });
    });
  },

  // 图片加载成功
  onImageLoad: function(e) {
    // 可以添加图片加载完成的处理逻辑
  },

  // 图片加载失败
  onImageError: function(e) {
    const { index } = e.currentTarget.dataset;
    const discussions = [...this.data.discussions];
    if (discussions[index]) {
      discussions[index].img = '../../assets/demo1.jpg'; // 使用默认图片
      this.setData({ discussions });
    }
  }
});
