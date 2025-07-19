Page({
    data: {
        messages: []
    },

    onLoad: function() {
        this.loadMessages();
    },

    onShow: function() {
        this.loadMessages();
    },

    loadMessages: function() {
        // 模拟消息数据，实际项目中应该从后端获取
        const mockMessages = [
            {
                id: 1,
                user_name: "用户A",
                avatar: "/assets/avatar1.jpg",
                last_message: "你好，请问这个猫咪是什么品种？",
                time: "10:30",
                unread: 2
            },
            {
                id: 2,
                user_name: "用户B", 
                avatar: "/assets/avatar1.jpg",
                last_message: "谢谢分享！",
                time: "昨天",
                unread: 0
            }
        ];

        this.setData({
            messages: mockMessages
        });
    },

    onMessageTap: function(e) {
        const messageId = e.currentTarget.dataset.id;
        wx.navigateTo({
            url: `/pages/chat/chat?id=${messageId}`
        });
    }
}); 