Page({
    data: {
        currentTab: 'hot', // 默认显示热门推荐
        posts: [],
        isLoading: false,
        isRefreshing: false,
        isLoadingMore: false,
        loadError: false,
        noMoreData: false,
        page: 1,
        pageSize: 10
    },

    onLoad: function() {
        this.loadPosts();
    },
    
    onShow: function() {
        // 每次页面显示都刷新数据
        if (this.data.posts.length === 0) {
            this.loadPosts();
        }
    },

    // 下拉刷新
    onPullDownRefresh: function() {
        this.setData({
            isRefreshing: true,
            page: 1,
            noMoreData: false
        });
        
        this.loadPosts(() => {
            this.setData({
                isRefreshing: false
            });
            wx.stopPullDownRefresh();
        });
    },
    
    // 切换标签
    switchTab: function(e) {
        const tab = e.currentTarget.dataset.tab;
        if (tab === this.data.currentTab) return;
        
        this.setData({
            currentTab: tab,
            posts: [],
            page: 1,
            noMoreData: false
        });
        
        this.loadPosts();
    },
    
    // 加载更多
    loadMorePosts: function() {
        if (this.data.isLoadingMore || this.data.noMoreData) return;
        
        this.setData({
            isLoadingMore: true,
            page: this.data.page + 1
        });
        
        this.loadPosts(true);
    },

    loadPosts: function(isLoadMore = false) {
        if (!isLoadMore) {
            this.setData({
                isLoading: true,
                loadError: false
            });
        }
        
        const { currentTab, page, pageSize } = this.data;
        let url = `http://localhost:5001/api/post/list?page=${page}&per_page=${pageSize}`;
        
        // 根据当前标签添加不同的参数
        if (currentTab === 'latest') {
            url += '&sort=latest';
        } else if (currentTab === 'following') {
            url += '&following=1';
            
            // 检查是否登录
            const token = wx.getStorageSync('token');
            if (!token) {
                wx.showToast({
                    title: '请先登录',
                    icon: 'none'
                });
                this.setData({
                    isLoading: false,
                    isLoadingMore: false,
                    posts: []
                });
                return;
            }
        }
        
        wx.request({
            url: url,
            method: 'GET',
            header: {
                'Authorization': wx.getStorageSync('token') || ''
            },
            success: (res) => {
                if (res.data.code === 200) {
                    const newPosts = res.data.data.posts || [];
                    
                    // 检查是否有更多数据
                    if (newPosts.length < pageSize) {
                        this.setData({
                            noMoreData: true
                        });
                    }
                    
                    // 处理帖子数据，添加是否点赞标记
                    const processedPosts = newPosts.map(post => {
                        return {
                            ...post,
                            is_liked: post.is_liked || false
                        };
                    });
                    
                    this.setData({
                        posts: isLoadMore ? [...this.data.posts, ...processedPosts] : processedPosts,
                        isLoading: false,
                        isLoadingMore: false
                    });
                    
                    console.log("加载的帖子:", processedPosts);
                } else {
                    console.error("获取作品失败:", res.data);
                    this.setData({
                        isLoading: false,
                        isLoadingMore: false,
                        loadError: true
                    });
                    
                    wx.showToast({
                        title: res.data.msg || '获取作品失败',
                        icon: 'none'
                    });
                }
            },
            fail: (err) => {
                console.error("请求失败:", err);
                this.setData({
                    isLoading: false,
                    isLoadingMore: false,
                    loadError: true
                });
                
                wx.showToast({
                    title: '网络错误，请检查连接',
                    icon: 'none'
                });
            }
        });
    },

    // 点赞/取消点赞
    toggleLike: function(e) {
        const postId = e.currentTarget.dataset.postId;
        const index = e.currentTarget.dataset.index;
        const token = wx.getStorageSync('token');
        
        // 阻止冒泡，避免触发卡片点击
        e.stopPropagation();
        
        if (!token) {
            wx.showToast({
                title: '请先登录',
                icon: 'none'
            });
            return;
        }
        
        const posts = this.data.posts;
        const post = posts[index];
        const isLiked = post.is_liked;
        
        // 乐观更新UI
        posts[index].is_liked = !isLiked;
        posts[index].like_count = isLiked ? Math.max(0, post.like_count - 1) : (post.like_count + 1);
        
        this.setData({
            posts: posts
        });
        
        // 发送请求
        wx.request({
            url: `http://localhost:5001/api/like/${isLiked ? 'unlike' : 'like'}`,
            method: 'POST',
            header: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            data: {
                post_id: postId
            },
            fail: (err) => {
                console.error("点赞/取消点赞失败:", err);
                
                // 恢复原状态
                posts[index].is_liked = isLiked;
                posts[index].like_count = post.like_count;
                
                this.setData({
                    posts: posts
                });
                
                wx.showToast({
                    title: '操作失败，请重试',
                    icon: 'none'
                });
            }
        });
    },

    // 点击某个作品，跳转到详情页
    goToDetail: function(e) {
        const post = e.currentTarget.dataset.post;
        wx.navigateTo({
            url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`
        });
    },

    // 重试加载
    retryLoad: function() {
        this.setData({
            page: 1,
            noMoreData: false
        });
        this.loadPosts();
    },
    
    // 跳转到发布页面
    goToPosting: function() {
        const token = wx.getStorageSync('token');
        if (!token) {
            wx.showToast({
                title: '请先登录',
                icon: 'none'
            });
            
            setTimeout(() => {
                wx.navigateTo({
                    url: '/pages/login/login'
                });
            }, 1500);
            return;
        }
        
        wx.navigateTo({
            url: '/pages/posting/posting'
        });
    },
    
    // 跳转到搜索页面
    goToSearch: function() {
        wx.showToast({
            title: '搜索功能开发中',
            icon: 'none'
        });
    }
});


