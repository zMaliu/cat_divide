Page({
    data:{
        currentTab: 'hot', // 默认显示热点页面
        posts: [],
        isRefreshing: false,
        isLoadingMore: false,
        isLoading: true,
        page: 1,
        perPage: 10,
        hasMore: true,
        searchKeyword: '',
        isSearchMode: false
    },

    onLoad: function() {
        this.loadPosts();
    },

    // 处理搜索输入
    onSearchInput: function(e) {
        this.setData({
            searchKeyword: e.detail.value
        });
    },

    // 执行搜索
    doSearch: function(e) {
        const keyword = this.data.searchKeyword.trim();
        if (!keyword) {
            // 如果搜索关键词为空且当前是搜索模式，则切换回普通模式
            if (this.data.isSearchMode) {
                this.setData({
                    isSearchMode: false,
                    page: 1
                });
                this.loadPosts(true);
            }
            return;
        }

        this.setData({
            isSearchMode: true,
            isLoading: true,
            posts: [],
            page: 1,
            hasMore: true
        });
        
        this.searchPosts();
    },

    // 清除搜索
    clearSearch: function() {
        this.setData({
            searchKeyword: '',
            isSearchMode: false,
            page: 1
        });
        this.loadPosts(true);
    },

    // 执行搜索请求
    searchPosts: function() {
        if (!this.data.hasMore) return;

        this.setData({
            isLoading: true,
            isLoadingMore: this.data.posts.length > 0
        });

        wx.request({
            url: 'http://localhost:5001/api/search',
            method: 'GET',
            data: {
                keyword: this.data.searchKeyword,
                page: this.data.page,
                per_page: this.data.perPage
            },
            success: (res) => {
                if (res.data.code === 200) {
                    // 为每个帖子添加imageLoaded属性来控制加载状态
                    const newPosts = res.data.data.posts.map(post => ({
                        ...post,
                        imageLoaded: false
                    }));

                    this.setData({
                        posts: [...this.data.posts, ...newPosts],
                        page: this.data.page + 1,
                        hasMore: newPosts.length === this.data.perPage
                    });
                } else {
                    wx.showToast({
                        title: res.data.msg || '搜索失败',
                        icon: 'none'
                    });
                }
            },
            complete: () => {
                this.setData({
                    isLoading: false,
                    isRefreshing: false,
                    isLoadingMore: false
                });
            }
        });
    },

    // 加载帖子数据
    loadPosts: function(refresh = false) {
        if (this.data.isSearchMode) {
            if (refresh) {
                this.setData({
                    page: 1,
                    posts: [],
                    hasMore: true
                });
            }
            this.searchPosts();
            return;
        }

        if (refresh) {
            this.setData({
                page: 1,
                posts: [],
                hasMore: true
            });
        }

        if (!this.data.hasMore && !refresh) return;

        this.setData({
            isLoading: true,
            isLoadingMore: !refresh && this.data.posts.length > 0
        });

        wx.request({
          url: 'http://localhost:5001/api/list',
          method: 'GET',
          data: {
            page: this.data.page,
            per_page: this.data.perPage
          },
          success: (res) => {
            if (res.data.code === 200) {
              // 为每个帖子添加imageLoaded属性来控制加载状态
              const newPosts = res.data.data.posts.map(post => ({
                ...post,
                imageLoaded: false
              }));

              this.setData({
                posts: [...this.data.posts, ...newPosts],
                page: this.data.page + 1,
                hasMore: newPosts.length === this.data.perPage
              });
            } else {
              wx.showToast({
                title: res.data.msg || '获取作品失败',
                icon: 'none'
              });
            }
          },
          complete: () => {
            this.setData({
                isLoading: false,
                isRefreshing: false,
                isLoadingMore: false
            });
          }
        });
    },

    // 图片加载完成处理
    onImageLoad: function(e) {
        const index = e.currentTarget.dataset.index;
        const key = `posts[${index}].imageLoaded`;
        this.setData({
            [key]: true
        });
    },

    // 下拉刷新
    onRefresh: function() {
        this.setData({
            isRefreshing: true
        });
        this.loadPosts(true);
    },

    // 加载更多
    loadMore: function() {
        if (this.data.isLoadingMore || !this.data.hasMore) return;
        this.loadPosts();
    },

    // 跳转到详情页
    goPostDetail: function(e) {
        const post = e.currentTarget.dataset.post;
        wx.navigateTo({
            url: `/pages/post-detail/post-detail?id=${post.article_id}`
        });
    },

    // 跳转到发布页面
    goToPosting: function() {
        wx.switchTab({
            url: '/pages/posting/posting'
        });
    },

    // 显示分享菜单
    onShareAppMessage: function() {
        return {
            title: '芝士猫窝 - 流浪猫的数字家园',
            path: '/pages/home/home'
        };
    }
})