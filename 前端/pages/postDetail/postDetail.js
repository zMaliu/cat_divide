
const config = require('../../utils/config.js')

Page({
    data: {
        post: {},
        commentContent: '',
        comments: [],
        userToken: '',
        fromPage: '', // 记录来源页面
        fromIndex: -1 // 记录在列表中的索引
    },

    onLoad: function(options) {
        console.log('========== postDetail onLoad ==========');
        const token = wx.getStorageSync('token'); 
        console.log('onLoad获取token:', token);
        this.setData({ userToken: token });
        console.log('onLoad设置后 this.data.userToken:', this.data.userToken);
        
        // 保存来源页面信息
        if (options.fromPage) {
            this.setData({
                fromPage: options.fromPage,
                fromIndex: parseInt(options.fromIndex || '-1')
            });
        }
        
        if (options.data) {
            let post = JSON.parse(decodeURIComponent(options.data));
            
                            // 强制转换点赞状态为布尔值
                post.is_liked = !!(post.is_liked === true || post.is_liked === 1 || post.is_liked === '1');
            
            // 处理图片URL - 使用本地默认图片
            if (post.img && post.img === '/default.jpg') {
                post.imgUrl = '../../assets/default.jpg'; // 使用本地默认图片
            } else if (post.img && !post.img.startsWith('http')) {
                post.imgUrl = config.baseURL + post.img;
            } else {
                post.imgUrl = post.img || '../../assets/default.jpg';
            }
            
            console.log('加载帖子数据:', {
                is_liked: post.is_liked,
                类型: typeof post.is_liked,
                图片: post.imgUrl
            });
            
            this.setData({ post: post });
            
            // 先获取评论，然后获取最新的帖子详情
            this.getComments(post.article_id);
            
            // 强制获取最新的帖子详情，包括关注状态
            this.getPostDetail(post.article_id);
        }
    },

    onShow: function() {
        console.log('========== postDetail onShow ==========');
        // 页面显示时重新获取token
        const token = wx.getStorageSync('token');
        console.log('onShow获取token:', token);
        console.log('onShow前 this.data.userToken:', this.data.userToken);
        this.setData({ userToken: token });
        console.log('onShow后 this.data.userToken:', this.data.userToken);
    },
    
    // 强制刷新数据
    refreshData: function() {
        if (!this.data.post || !this.data.post.article_id) {
            wx.showToast({
                title: '没有帖子数据',
                icon: 'none'
            });
            return;
        }
        
        wx.showLoading({
            title: '刷新中...',
            mask: true
        });
        
        // 强制获取最新的帖子详情
        this.getPostDetail(this.data.post.article_id);
        
        setTimeout(() => {
            wx.hideLoading();
        }, 1000);
    },

    // 页面卸载时，传递更新的数据给首页
    onUnload: function() {
        if (this.data.fromPage === 'home') {
            const app = getApp();
            if (app.globalData) {
                app.globalData.needRefreshHome = true;
                // 传递更新后的帖子数据和索引
                if (this.data.post && this.data.fromIndex >= 0) {
                    app.globalData.updatedPost = {
                        is_liked: this.data.post.is_liked,
                        like_count: this.data.post.like_count,
                        is_followed: this.data.post.is_followed
                    };
                    app.globalData.updatedPostIndex = this.data.fromIndex;
                }
            }
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
            url: `${config.apiURL}/post/${article_id}`,
            method: 'GET',
            header: headers,
            success: (res) => {
                if (res.data.code === 200) {
                    const post = res.data.data.post;
                    
                    // 处理图片URL - 使用本地默认图片
                    if (post.img && post.img === '/default.jpg') {
                        post.imgUrl = '../../assets/default.jpg';
                    } else if (post.img && !post.img.startsWith('http')) {
                        post.imgUrl = config.baseURL + post.img;
                    } else {
                        post.imgUrl = post.img || '../../assets/default.jpg';
                    }
                    
                    this.setData({
                        post: post
                    });
                }
            }
        });
    },

    getComments: function(article_id) {
        const token = this.data.userToken;
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            // 确保token格式正确
            if (token.startsWith('Bearer ')) {
                headers['Authorization'] = token;
            } else {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        wx.request({
            url: `${config.apiURL}/comment/list/${article_id}`,
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
            url: config.apiURL + '/comment/create',
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
        
        // 调试日志
        console.log('=== 点赞调试 ===');
        console.log('this.data.userToken:', this.data.userToken);
        console.log('Storage中的token:', wx.getStorageSync('token'));
        console.log('article_id:', article_id);
        
        if (!token) {
            console.log('❌ token为空，提示登录');
            wx.showToast({ title: '请先登录', icon: 'none' });
            return;
        }
        
        console.log('✅ token存在，准备发送请求');
        
        // 修复：使用 post.is_liked 而不是复杂的状态判断
        const currentIsLiked = this.data.post.is_liked === 1 || this.data.post.is_liked === true;
        const newIsLiked = !currentIsLiked;
        const method = newIsLiked ? 'POST' : 'DELETE';
        const url = `${config.apiURL}/like/${article_id}`;
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
                    
                    // 重新获取文章详情，确保UI显示最新数据
                    this.getPostDetail(article_id);
                    
                    // 设置全局刷新标志，让首页也能同步更新
                    const app = getApp();
                    if (app.globalData) {
                        app.globalData.needRefreshHome = true;
                    }
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
        
        // 防止重复点击
        if (this.followInProgress) {
            return;
        }
        this.followInProgress = true;
        
        // 确保当前关注状态是布尔值
        const currentIsFollowed = !!this.data.post.is_followed;
        const newIsFollowed = !currentIsFollowed;
        const method = newIsFollowed ? 'POST' : 'DELETE';
        const url = `${config.apiURL}/follow/${authorId}`;
        
        // 立即更新UI状态
        const newPost = {...this.data.post, is_followed: newIsFollowed};
        this.setData({
            post: newPost
        });
        
        // 设置全局刷新标志
        const app = getApp();
        if (app.globalData) {
            app.globalData.needRefreshHome = true;
        }
        
        console.log('关注状态变更:', {
            原状态: currentIsFollowed,
            新状态: newIsFollowed,
            作者ID: authorId,
            状态类型: typeof newIsFollowed
        });
        
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // 确保token格式正确
        if (token.startsWith('Bearer ')) {
            headers['Authorization'] = token;
        } else {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        wx.request({
            url: url,
            method: method,
            header: headers,
            success: (res) => {
                console.log('关注请求响应:', res.data);
                
                if (res.data.code === 200) {
                    // 使用后端返回的状态，而不是前端计算的状态
                    const serverIsFollowed = res.data.data && res.data.data.is_following !== undefined 
                        ? res.data.data.is_following 
                        : newIsFollowed;
                    
                    wx.showToast({
                        title: serverIsFollowed ? '关注成功' : '取消关注成功',
                        icon: 'success'
                    });
                    
                    // 强制刷新视图，使用服务器返回的状态
                    setTimeout(() => {
                        const updatedPost = {...this.data.post, is_followed: serverIsFollowed};
                        this.setData({
                            post: updatedPost
                        });
                        
                        console.log('更新后的帖子数据:', {
                            is_followed: this.data.post.is_followed,
                            类型: typeof this.data.post.is_followed
                        });
                    }, 100);
                } else {
                    // 如果请求失败，回滚UI状态
                    const rollbackPost = {...this.data.post, is_followed: currentIsFollowed};
                    this.setData({
                        post: rollbackPost
                    });
                    wx.showToast({
                        title: res.data.msg || '操作失败',
                        icon: 'none'
                    });
                }
            },
            fail: (err) => {
                console.error('关注请求失败:', err);
                
                // 如果网络错误，回滚UI状态
                const rollbackPost = {...this.data.post, is_followed: currentIsFollowed};
                this.setData({
                    post: rollbackPost
                });
                wx.showToast({
                    title: '操作失败，请重试',
                    icon: 'none'
                });
            },
            complete: () => {
                // 操作完成后，重置标志
                setTimeout(() => {
                    this.followInProgress = false;
                }, 500);  // 添加500ms防抖
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