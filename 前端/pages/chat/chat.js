Page({
    data: {
        chatId: null,
        messages: [],
        inputText: ''
    },

    onLoad: function(options) {
        this.setData({
            chatId: options.id
        });
        this.loadChatHistory();
    },

    loadChatHistory: function() {
        // 模拟聊天历史数据
        const mockMessages = [
            {
                id: 1,
                type: 'received',
                content: '你好，请问这个猫咪是什么品种？',
                time: '10:30'
            },
            {
                id: 2,
                type: 'sent',
                content: '这是阿比西尼亚猫，很温顺的品种',
                time: '10:32'
            }
        ];

        this.setData({
            messages: mockMessages
        });
    },

    onInputChange: function(e) {
        this.setData({
            inputText: e.detail.value
        });
    },

    sendMessage: function() {
        if (!this.data.inputText.trim()) {
            return;
        }

        const newMessage = {
            id: Date.now(),
            type: 'sent',
            content: this.data.inputText,
            time: this.getCurrentTime()
        };

        this.setData({
            messages: [...this.data.messages, newMessage],
            inputText: ''
        });
    },

    getCurrentTime: function() {
        const now = new Date();
        return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    }
}); 