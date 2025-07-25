Page({
    data: {
      post: {},
      commentContent: '', 
      comments: [],
      isLiked: false,
      likeCount: 0,
      isFollowing: false,
      commentFocus: false,
      commentSortType: 'time', // 'time' 或 'hot'
      replyTo: null
    },
    
    // 确保数据初始化
    onReady: function() {
      this.setData({
        commentContent: ''
      });
      console.log('页面准备完成，评论内容初始化为空字符串');
    },
  
    onLoad: function(options) {
        if (options.data) {
          let post = JSON.parse(decodeURIComponent(options.data));
          this.setData({ 
            post: post,
            likeCount: post.like_count || 0
          });
          this.getPostDetail(post.article_id);
          this.getComments(post.article_id);
          this.checkLikeStatus(post.article_id);
          this.checkFollowStatus(post.user_id);
        }
      },
  
    
    getPostDetail: function(article_id) {
      wx.request({
        url: `http://localhost:5001/api/post/detail/${article_id}`,
        method: 'GET',
        success: (res) => {
          if (res.data && res.data.data && res.data.data.post) {
            this.setData({
              post: res.data.data.post,
              likeCount: res.data.data.post.like_count || 0
            });
          }
        }
      });
    },

    getComments: function(article_id) {
      const token = wx.getStorageSync('token');
      if (!token) return;
      
      // 使用适当的token格式
      const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
      
      wx.request({
        url: `http://localhost:5001/api/comment/list/${article_id}`,
        method: 'GET',
        header: {
          'Authorization': authToken
        },
        success: (res) => {
          if (res.data && res.data.data && Array.isArray(res.data.data.comments)) {
            // 处理评论数据，添加默认的点赞数
            const comments = res.data.data.comments.map(comment => {
              return {
                ...comment,
                like_count: comment.like_count || 0
              };
            });
            
            this.setData({
              comments: this.sortComments(comments, this.data.commentSortType)
            });
          }
        }
      });
    },

    // 按时间或热度排序评论
    sortComments: function(comments, sortType) {
      if (sortType === 'time') {
        // 按时间倒序排序（最新的在前面）
        return [...comments].sort((a, b) => new Date(b.comment_time) - new Date(a.comment_time));
      } else {
        // 按点赞数倒序排序（点赞多的在前面）
        return [...comments].sort((a, b) => b.like_count - a.like_count);
      }
    },

    // 切换评论排序方式
    toggleCommentSort: function() {
      const newSortType = this.data.commentSortType === 'time' ? 'hot' : 'time';
      this.setData({
        commentSortType: newSortType,
        comments: this.sortComments(this.data.comments, newSortType)
      });
    },

    onCommentInput: function(e) {
      const value = e.detail.value;
      console.log('评论输入:', value);  // 添加调试日志
      this.setData({
        commentContent: value
      });
    },

    // 聚焦评论输入框
    focusCommentInput: function() {
      this.setData({
        commentFocus: true
      });
    },

    // 回复评论
    replyComment: function(e) {
      const commentId = e.currentTarget.dataset.id;
      const userName = e.currentTarget.dataset.name;
      
      this.setData({
        commentContent: `回复 @${userName}: `,
        commentFocus: true,
        replyTo: commentId
      });
    },

    // 点赞评论
    likeComment: function(e) {
      const commentId = e.currentTarget.dataset.id;
      wx.showToast({
        title: '评论点赞功能开发中',
        icon: 'none'
      });
    },

    // 预览图片
    previewImage: function() {
      if (this.data.post.img) {
        wx.previewImage({
          urls: [this.data.post.img],
          current: this.data.post.img
        });
      }
    },

    // 分享帖子
    sharePost: function() {
      wx.showShareMenu({
        withShareTicket: true,
        menus: ['shareAppMessage', 'shareTimeline']
      });
    },

    // 分享给朋友
    onShareAppMessage: function() {
      const post = this.data.post;
      return {
        title: post.title,
        path: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`,
        imageUrl: post.img || ''
      };
    },

    // 分享到朋友圈
    onShareTimeline: function() {
      const post = this.data.post;
      return {
        title: post.title,
        query: `data=${encodeURIComponent(JSON.stringify(post))}`,
        imageUrl: post.img || ''
      };
    },

    handleComment: function() {
      const token = wx.getStorageSync('token');
      const article_id = this.data.post.article_id;
      let article_content = this.data.commentContent;
      
      console.log('评论内容:', article_content);  // 添加调试日志
      
      // 确保article_content是字符串
      if (typeof article_content !== 'string') {
        article_content = '';
      }
      
      article_content = article_content.trim();
      
      if (!article_content) {
        wx.showToast({ title: '评论不能为空', icon: 'none' });
        return;
      }

      if (!token) {
        wx.showToast({ title: '请先登录', icon: 'none' });
        wx.navigateTo({
          url: '/pages/login/login'
        });
        return;
      }
      
      // 使用适当的token格式
      const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
      
      wx.showLoading({ title: '发送中...' });
      
      wx.request({
        url: 'http://localhost:5001/api/comment/create',
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': authToken
        },
        data: {
          article_id: article_id,
          article_content: article_content
        },
        success: (res) => {
          wx.hideLoading();
          if (res.data.code === 200) {
            wx.showToast({ title: '评论成功', icon: 'success' });
            this.setData({ 
              commentContent: '',
              replyTo: null
            });
            this.getComments(article_id); // 刷新评论列表
          } else {
            wx.showToast({ title: res.data.msg || '评论失败', icon: 'none' });
          }
        },
        fail: () => {
          wx.hideLoading();
          wx.showToast({ title: '网络错误，请重试', icon: 'none' });
        }
      });
    },

    // 检查是否已点赞
    checkLikeStatus: function(article_id) {
      const token = wx.getStorageSync('token');
      if (!token) return;

      // 使用适当的token格式
      const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;

      wx.request({
        url: `http://localhost:5001/api/like/check/${article_id}`,
        method: 'GET',
        header: {
          'Authorization': authToken
        },
        success: (res) => {
          if (res.data && res.data.code === 200) {
            this.setData({
              isLiked: res.data.data.is_liked || false
            });
          }
        }
      });
    },

    // 点赞/取消点赞
    handleLike: function() {
      const token = wx.getStorageSync('token');
      const article_id = this.data.post.article_id;
      
      if (!token) {
        wx.showToast({ title: '请先登录', icon: 'none' });
        wx.navigateTo({
          url: '/pages/login/login'
        });
        return;
      }

      // 使用适当的token格式
      const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;

      const url = this.data.isLiked
        ? `http://localhost:5001/api/like/unlike`
        : `http://localhost:5001/api/like/like`;

      // 乐观更新UI
      const newIsLiked = !this.data.isLiked;
      const likeCountChange = newIsLiked ? 1 : -1;
      
      this.setData({
        isLiked: newIsLiked,
        likeCount: Math.max(0, this.data.likeCount + likeCountChange)
      });

      wx.request({
        url: url,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': authToken
        },
        data: {
          post_id: article_id
        },
        fail: (err) => {
          console.error("点赞/取消点赞失败:", err);
          
          // 恢复原状态
          this.setData({
            isLiked: !newIsLiked,
            likeCount: this.data.likeCount - likeCountChange
          });
          
          wx.showToast({
            title: '操作失败，请重试',
            icon: 'none'
          });
        }
      });
    },

    // 检查是否已关注作者
    checkFollowStatus: function(authorId) {
      const token = wx.getStorageSync('token');
      if (!token) return;
      
      const currentUserId = wx.getStorageSync('user_id');
      if (!currentUserId || currentUserId == authorId) {
        // 不能关注自己
        return;
      }

      // 使用适当的token格式
      const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;

      wx.request({
        url: `http://localhost:5001/api/follow/check/${authorId}`,
        method: 'GET',
        header: {
          'Authorization': authToken
        },
        success: (res) => {
          if (res.data && res.data.code === 200) {
            this.setData({
              isFollowing: res.data.data.is_following || false
            });
          }
        }
      });
    },

    // 关注/取消关注
    handleFollow: function() {
      const token = wx.getStorageSync('token');
      const authorId = this.data.post.user_id;
      const currentUserId = wx.getStorageSync('user_id');
      
      if (!token) {
        wx.showToast({ title: '请先登录', icon: 'none' });
        wx.navigateTo({
          url: '/pages/login/login'
        });
        return;
      }

      if (currentUserId == authorId) {
        wx.showToast({ title: '不能关注自己', icon: 'none' });
        return;
      }

      // 使用适当的token格式
      const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;

      // 乐观更新UI
      this.setData({
        isFollowing: !this.data.isFollowing
      });

      const url = this.data.isFollowing
        ? `http://localhost:5001/api/follow/create/${authorId}`
        : `http://localhost:5001/api/follow/unfollow/${authorId}`;

      wx.request({
        url: url,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': authToken
        },
        fail: (err) => {
          console.error("关注/取消关注失败:", err);
          
          // 恢复原状态
          this.setData({
            isFollowing: !this.data.isFollowing
          });
          
          wx.showToast({
            title: '操作失败，请重试',
            icon: 'none'
          });
        }
      });
    }
  });