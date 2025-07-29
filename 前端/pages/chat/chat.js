Page({
    data: {
      sessionId: '',
      targetUserId: '',
      targetUserAvatar: '', // 对方头像
      myUserId: '',
      myAvatar: '',         // 自己头像
      messageList: [],
      inputMessage: '',
      scrollToView: ''
    },
  
    onLoad: function(options) {
      const targetUserId = options.user_id;
      const myUserId = String(wx.getStorageSync('user_id'));
      const myAvatar = wx.getStorageSync('avatar') || '/images/default-avatar.png';
      const targetUserAvatar = options.avatar || '/images/default-avatar.png';
      this.setData({
        targetUserId,
        myUserId,
        myAvatar,
        targetUserAvatar
      });
      this.createOrGetSession();
    },
  
    createOrGetSession: function() {
      const token = wx.getStorageSync('token');
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
            this.getMessageList();
          } else {
            wx.showToast({ title: res.data.msg || '获取会话失败', icon: 'none' });
          }
        },
        fail: () => {
          wx.showToast({ title: '网络错误', icon: 'none' });
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
              return msg;
            });
            this.setData({
              messageList: msgList
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
    }
  });