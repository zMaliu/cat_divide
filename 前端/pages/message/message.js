const util = require('../../utils/util.js');

Page({
  data: {
    messageList: [],
    loading: false,
    hasMore: true,
    page: 1,
    pageSize: 20,
    userToken: ''
  },

  onLoad: function() {
    const token = wx.getStorageSync('token');
    this.setData({ userToken: token });
    
    // 检查登录状态
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/profile/profile'
        });
      }, 1500);
      return;
    }
    
    this.loadMessageList();
  },

  // 功能区域点击事件（占位实现）
  goToLikes: function() {
    wx.showToast({
      title: '赞和收藏功能开发中',
      icon: 'none'
    });
  },

  goToComments: function() {
    wx.showToast({
      title: '评论功能开发中',
      icon: 'none'
    });
  },

  goToFollows: function() {
    wx.showToast({
      title: '新增关注功能开发中',
      icon: 'none'
    });
  },

  onShow: function() {
    if (this.data.userToken) {
      this.refreshMessageList();
    }
  },

  loadMessageList: function(isRefresh = false) {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    
    const token = this.data.userToken;
    const page = isRefresh ? 1 : this.data.page;
    
    wx.request({
      url: 'http://localhost:5001/api/chat/session',
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        page: page,
        per_page: this.data.pageSize
      },
      success: (res) => {
        if (res.data.code === 200) {
          const sessions = res.data.data.sessions || [];
          
          const processedSessions = sessions.map(session => ({
            ...session,
            updated_time: util.formatRelativeTime(new Date(session.updated_time)),
            other_user_name: session.other_user_name || '未知用户',
            last_message: session.last_message ? (session.last_message.length > 20 ? session.last_message.substring(0, 20) + '...' : session.last_message) : '暂无消息',
            fromuser_id: String(session.fromuser_id),
            touser_id: String(session.touser_id)
          }));
          
          if (isRefresh) {
            this.setData({
              messageList: processedSessions,
              page: 2,
              hasMore: processedSessions.length === this.data.pageSize
            });
          } else {
            const newList = [...this.data.messageList, ...processedSessions];
            this.setData({
              messageList: newList,
              page: this.data.page + 1,
              hasMore: processedSessions.length === this.data.pageSize
            });
          }
        } else {
          wx.showToast({
            title: res.data.msg || '加载失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.log('加载消息列表失败:', err);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      },
      complete: () => {
        this.setData({ loading: false });
        wx.stopPullDownRefresh();
      }
    });
  },

  refreshMessageList: function() {
    this.loadMessageList(true);
  },

  onMessageTap: function(e) {
    const session = e.currentTarget.dataset.session;
    if (!session) {
      wx.showToast({
        title: '会话信息错误',
        icon: 'none'
      });
      return;
    }
    
    const currentUserId = wx.getStorageSync('user_id');
    let otherUserId, username;
    
    if (session.fromuser_id == currentUserId) {
      otherUserId = session.touser_id;
      username = session.other_user_name;
    } else {
      otherUserId = session.fromuser_id;
      username = session.other_user_name;
    }
    
    // 跳转到聊天页面
    wx.navigateTo({
      url: `/pages/chat/chat?user_id=${otherUserId}&username=${username}`
    });
  },

  // 下拉刷新
  onPullDownRefresh: function() {
    this.refreshMessageList();
  },

  onReachBottom: function() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMessageList();
    }
  },

  onShareAppMessage: function() {
    return {
      title: '猫咪社区 - 消息',
      path: '/pages/message/message'
    };
  }
}); 