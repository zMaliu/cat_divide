
Page({
    data: {
        post: {},
        commentContent: '',
        comments: [],
        userToken: ''
    },

    onLoad: function(options) {
        const token = wx.getStorageSync('token'); 
        this.setData({ userToken: token });
        
        if (options.data) {
            let post = JSON.parse(decodeURIComponent(options.data));
            this.setData({ post: post });
            this.getComments(post.article_id);
            this.getPostDetail(post.article_id);
        }
    },

    getPostDetail: function(article_id) {
        const token = this.data.userToken;
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        wx.request({
            url: `http://localhost:5001/api/post/detail/${article_id}`,
            method: 'GET',
            header: headers,
            success: (res) => {
                if (res.data.code === 200) {
                    this.setData({
                        post: res.data.data.post
                    });
                }
            }
        });
    },

    getComments: function(article_id) {
        const token = this.data.userToken;
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        wx.request({
            url: `http://localhost:5001/api/comment/list/${article_id}`,
            method: 'GET',
            header: headers,
            success: (res) => {
                if (res.data && res.data.data && Array.isArray(res.data.data.comments)) {
                    this.setData({
                        comments: res.data.data.comments
                    });
                }
            }
        });
    },

    onCommentInput: function(e) {
        this.setData({
            commentContent: e.detail.value
        });
    },

    handleComment: function() {
        const token = this.data.userToken;
        const article_id = this.data.post.article_id;
        const article_content = this.data.commentContent.trim();
        if (!article_content) {
            wx.showToast({ title: '评论不能为空', icon: 'none' });
            return;
        }
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        wx.request({
            url: 'http://localhost:5001/api/comment/create',
            method: 'POST',
            header: headers,
            data: {
                article_id: article_id,
                article_content: article_content
            },
            success: (res) => {
                if (res.data.code === 200) {
                    wx.showToast({ title: '评论成功', icon: 'success' });
                    this.setData({ commentContent: '' });
                    this.getComments(article_id);
                } else {
                    wx.showToast({ title: res.data.msg || '评论失败', icon: 'none' });
                }
            }
        });
    },

    handleLike: function() {
        const token = this.data.userToken;
        const article_id = this.data.post.article_id;
        if (!token) {
            wx.showToast({ title: '请先登录', icon: 'none' });
            return;
        }
        
        const currentIsLiked = this.data.post.is_liked === 1 || this.data.post.is_liked === true;
        const newIsLiked = !currentIsLiked;
        const method = newIsLiked ? 'POST' : 'DELETE';
        const url = `http://localhost:5001/api/like/${article_id}`;
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
        
        wx.request({
            url: url,
            method: method,
            header: headers,
            success: (res) => {
                if (res.data.code === 200) {
                    wx.showToast({ 
                        title: newIsLiked ? '点赞成功' : '取消点赞成功', 
                        icon: 'success' 
                    });
                    
                    this.getPostDetail(article_id);
                } else {
                    wx.showToast({ title: res.data.msg || '点赞失败', icon: 'none' });
                }
            },
            fail: (err) => {
                wx.showToast({ title: '网络错误', icon: 'none' });
            }
        });
    },

    handleFollow: function() {
        const token = this.data.userToken;
        const post = this.data.post || {};
        const authorId = post.user_id;
        const currentUserId = wx.getStorageSync('user_id');
        
        if (!token) {
            wx.showToast({ title: '请先登录', icon: 'none' });
            wx.navigateTo({ url: '/pages/login/login' });
            return;
        }
        
        if (currentUserId == authorId) {
            wx.showToast({ title: '不能关注自己', icon: 'none' });
            return;
        }
        
        const currentIsFollowed = this.data.post.is_followed || false;
        const newIsFollowed = !currentIsFollowed;
        const method = newIsFollowed ? 'POST' : 'DELETE';
        const url = `http://localhost:5001/api/follow/${authorId}`;
        
        wx.request({
            url: url,
            method: method,
            header: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            success: (res) => {
                if (res.data.code === 200) {

                    this.setData({
                        'post.is_followed': newIsFollowed
                    });
                    wx.showToast({
                        title: newIsFollowed ? '关注成功' : '取消关注成功',
                        icon: 'success'
                    });
                } else {
                    wx.showToast({
                        title: res.data.msg || '操作失败',
                        icon: 'none'
                    });
                }
            },
            fail: (err) => {
                wx.showToast({
                    title: '操作失败，请重试',
                    icon: 'none'
                });
            }
        });
    },

    onMessageTap: function(e) {
        const userId = e.currentTarget.dataset.userId;
        if (!userId) {
            wx.showToast({ title: '用户ID不存在', icon: 'none' });
            return;
        }
        wx.navigateTo({
            url: `/pages/chat/chat?user_id=${userId}`
        });
    }
}); 