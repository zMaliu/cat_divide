
Page({
    data: {
        currentTab: 'hot',
        posts: [],
        userToken: ''
    },

    onLoad: function() {
        const token = wx.getStorageSync('token');
        this.setData({
            userToken: token
        });
        this.loadPosts();
    },

    onShow: function() {
        const token = wx.getStorageSync('token');
        this.setData({
            userToken: token
        });
        this.loadPosts();
    },

    loadPosts: function() {
        const token = this.data.userToken;
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        wx.request({
            url: 'http://localhost:5001/api/post/list?per_page=100',
            method: 'GET',
            header: headers,
            success: (res) => {
                if (res.data.code === 200) {
                    console.log('文章列表数据:', res.data.data.posts);
                    if (res.data.data.posts.length > 0) {
                    console.log('第一篇文章:', res.data.data.posts[0]);
                    }
                    this.setData({
                        posts: res.data.data.posts
                    });
                }
            }
        });
    },

    // 只保留跳转详情页
    goToDetail: function(e) {
        const post = e.currentTarget.dataset.post;
        wx.navigateTo({
            url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`
        });
    }
});
