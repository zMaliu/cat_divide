Page({
    data: {
        post: null,
        comments: [],
        commentText: '',
        loading: false
    },

    onLoad: function(options) {
        const postData = JSON.parse(decodeURIComponent(options.post));
        this.setData({
            post: postData
        });
        this.loadComments();
    },

    loadComments: function() {
        this.setData({ loading: true });
        
        wx.request({
            url: `http://localhost:5001/api/comment/list/${this.data.post.article_id}`,
            method: 'GET',
            success: (res) => {
                console.log('评论列表响应:', res);
                if (res.data.code === 200) {
                    this.setData({
                        comments: res.data.data.comments || []
                    });
                } else {
                    wx.showToast({
                        title: res.data.msg || '获取评论失败',
                        icon: 'none'
                    });
                }
            },
            fail: (err) => {
                console.error('评论列表请求失败:', err);
                wx.showToast({
                    title: '网络错误',
                    icon: 'none'
                });
            },
            complete: () => {
                this.setData({ loading: false });
            }
        });
    },

    onCommentInput: function(e) {
        this.setData({
            commentText: e.detail.value
        });
    },

    submitComment: function() {
        if (!this.data.commentText.trim()) {
            wx.showToast({
                title: '请输入评论内容',
                icon: 'none'
            });
            return;
        }

        // 检查是否有登录token
        const token = wx.getStorageSync('token');
        if (!token) {
            wx.showToast({
                title: '请先登录',
                icon: 'none'
            });
            return;
        }

        wx.request({
            url: 'http://localhost:5001/api/comment/create',
            method: 'POST',
            header: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            data: {
                article_id: this.data.post.article_id,
                article_content: this.data.commentText
            },
            success: (res) => {
                console.log('评论提交响应:', res);
                if (res.data.code === 200) {
                    wx.showToast({
                        title: '评论成功',
                        icon: 'success'
                    });
                    this.setData({
                        commentText: ''
                    });
                    this.loadComments();
                } else {
                    wx.showToast({
                        title: res.data.msg || '评论失败',
                        icon: 'none'
                    });
                }
            },
            fail: (err) => {
                console.error('评论提交失败:', err);
                wx.showToast({
                    title: '网络错误',
                    icon: 'none'
                });
            }
        });
    }
}); 