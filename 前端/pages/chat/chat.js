
const util = require('../../utils/util.js');

Page({
  data: {
    sessionId: '',
    targetUserId: '',
    targetUserAvatar: '', // 对方头像
    myUserId: '',
    myAvatar: '',         // 自己头像
    messageList: [],
    inputMessage: '',
    scrollToView: '',
    username: ''
  },

  onLoad: function(options) {
    const targetUserId = options.user_id;
    const myUserId = String(wx.getStorageSync('user_id'));
    const myAvatar = wx.getStorageSync('avatar') || '/images/default-avatar.png';
    const targetUserAvatar = options.avatar || '/images/default-avatar.png';
    const username = options.username || '用户';
    
    this.setData({
      targetUserId,
      myUserId,
      myAvatar,
      targetUserAvatar,
      username
    });
    
    // 检查登录状态
    const token = wx.getStorageSync('token');
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
    
    this.createOrGetSession();
  },

  onShow: function() {
    // 页面显示时刷新消息
    if (this.data.sessionId) {
      this.getMessageList();
    }
  },

  createOrGetSession: function() {
    const token = wx.getStorageSync('token');
    // 先创建会话
    wx.request({
      url: 'http://localhost:5001/api/chat/session',
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      data: {
        touser_id: this.data.targetUserId
      },
      success: (res) => {
        if (res.data.code === 200) {
          const sessionId = res.data.data.session.session_id;
          this.setData({ sessionId });
          // 然后获取会话列表来获取用户名
          this.getSessionWithUsername();
        } else {
          wx.showToast({ title: res.data.msg || '获取会话失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  getSessionWithUsername: function() {
    const token = wx.getStorageSync('token');
    wx.request({
      url: 'http://localhost:5001/api/chat/session',
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        page: 1,
        per_page: 100
      },
      success: (res) => {
        if (res.data.code === 200) {
          const sessions = res.data.data.sessions || [];
          // 找到当前会话
          const currentSession = sessions.find(session => 
            session.session_id == this.data.sessionId
          );
          
          if (currentSession && currentSession.other_user_name) {
            this.setData({ 
              username: currentSession.other_user_name
            });
          }
          
          this.getMessageList();
        } else {
          this.getMessageList(); 
        }
      },
      fail: () => {
        this.getMessageList(); 
      }
    });
  },



  getMessageList: function() {
    const token = wx.getStorageSync('token');
    const sessionId = this.data.sessionId;
    if (!sessionId) return;
    
    wx.request({
      url: `http://localhost:5001/api/chat/message/${sessionId}`,
      method: 'GET',
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
                success: (res) => {
            if (res.data.code === 200) {
              const msgList = (res.data.data.messages || []).map(msg => {
                msg.fromuser_id = String(msg.fromuser_id);
                msg.original_time = msg.created_time;
                msg.created_time = util.formatChatTime(new Date(msg.created_time));
                return msg;
              });

              console.log('原始消息列表:', msgList);
              const processedMsgList = this.processMessageTime(msgList);
              console.log('处理后的消息列表:', processedMsgList);
   
              if (processedMsgList.length > 0 && processedMsgList[0].target_user_name) {
                this.setData({
                  username: processedMsgList[0].target_user_name
                });
              }
              
              console.log('设置消息列表:', processedMsgList);
              this.setData({
                messageList: processedMsgList
              });
              this.scrollToBottom();
            } else {
              wx.showToast({ title: res.data.msg || '获取消息失败', icon: 'none' });
            }
          },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  sendMessage: function() {
    const token = wx.getStorageSync('token');
    const { inputMessage, targetUserId } = this.data;
    if (!inputMessage.trim()) {
      wx.showToast({ title: '请输入内容', icon: 'none' });
      return;
    }
    
    wx.request({
      url: `http://localhost:5001/api/chat/message`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      data: {
        touser_id: targetUserId,
        content: inputMessage
      },
      success: (res) => {
        if (res.data.code === 200) {
          wx.showToast({ title: '发送成功', icon: 'success' });
          this.setData({ inputMessage: '' });
          this.getMessageList();
        } else {
          wx.showToast({ title: res.data.msg || '发送失败', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  onInputChange: function(e) {
    this.setData({
      inputMessage: e.detail.value
    });
  },

  scrollToBottom: function() {
    this.setData({
      scrollToView: 'msg-bottom'
    });
  },

  processMessageTime: function(messages) {
    console.log('处理时间显示，消息数量:', messages ? messages.length : 0);
    if (!messages || messages.length === 0) return messages;
    
    const processedMessages = [];
    let lastMessageTime = null;
    
    for (let i = 0; i < messages.length; i++) {
      const currentMessage = messages[i];
      
      let currentTime;
      try {
        currentTime = new Date(currentMessage.original_time);
      } catch (e) {
        currentTime = new Date();
      }
      
      let showTime = false;
      if (i === 0) {
        showTime = true;
        console.log('第一条消息显示时间');
      } else if (lastMessageTime) {
        const timeDiff = Math.abs(currentTime.getTime() - lastMessageTime.getTime());
        const fiveMinutes = 5 * 60 * 1000; 
        showTime = timeDiff > fiveMinutes;
        console.log(`消息${i}时间差: ${timeDiff}ms, 显示时间: ${showTime}`);
      }
      
      currentMessage.showTime = showTime;
      processedMessages.push(currentMessage);
      
      lastMessageTime = currentTime;
    }
    
    return processedMessages;
  }
}); 