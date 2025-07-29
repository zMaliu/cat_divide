Page({
    data: {
      post: {},
      commentContent: '', 
      comments: []        
    },
  
    onLoad: function(options) {
        if (options.data) {
          let post = JSON.parse(decodeURIComponent(options.data));
          this.setData({ post: post });
          this.getComments(post.article_id);
        }
      },
  
    
    getPostDetail: function(article_id) {
      wx.request({
        url: `http://localhost:5001/api/post/detail/${article_id}`,
        method: 'GET',
        header: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + wx.getStorageSync('token')
          },
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
    const token = wx.getStorageSync('token');
        wx.request({
          url: `http://localhost:5001/api/comment/list/${article_id}`,
          method: 'GET',
          header: {
            'Authorization': 'Bearer ' + token
          },
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
        const token = wx.getStorageSync('token');
        const article_id = this.data.post.article_id;
        const article_content = this.data.commentContent.trim();
        if (!article_content) {
          wx.showToast({ title: '评论不能为空', icon: 'none' });
          return;
        }
        wx.request({
          url: 'http://localhost:5001/api/comment/create',
          method: 'POST',
          header: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
          },
          data: {
            article_id: article_id,
            article_content: article_content
          },
          success: (res) => {
            if (res.data.code === 200) {
              wx.showToast({ title: '评论成功', icon: 'success' });
              this.setData({ commentContent: '' });
              this.getComments(article_id); // 刷新评论列表
            } else {
              wx.showToast({ title: res.data.msg || '评论失败', icon: 'none' });
            }
          }
        });
      },

      handleLike: function() {
        const token = wx.getStorageSync('token');
        const article_id = this.data.post.article_id;
        
        if (!token) {
          wx.showToast({ title: '请先登录', icon: 'none' });
          return;
        }

        // 获取当前状态
        const currentLikeCount = this.data.post.like_count || 0;
        const currentIsLiked = this.data.post.is_liked || false;

        // 乐观更新UI
        const newIsLiked = !currentIsLiked;
        const likeCountChange = newIsLiked ? 1 : -1;

        // 使用正确的数据路径更新
        this.setData({
            'post.is_liked': newIsLiked,
            'post.like_count': Math.max(0, currentLikeCount + likeCountChange)
        });

        // 根据当前状态决定是点赞还是取消点赞
        const method = newIsLiked ? 'POST' : 'DELETE';
        const url = `http://localhost:5001/api/like/${article_id}`;

        wx.request({
          url: url,
          method: method,
          header: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
          },        
          success: (res) => {
            if (res.data.code === 200) {
                wx.showToast({ 
                    title: newIsLiked ? '点赞成功' : '取消点赞成功', 
                    icon: 'success' 
                  });

            } else {
              wx.showToast({ title: res.data.msg || '点赞失败', icon: 'none' });
              this.setData({
                'post.is_liked': currentIsLiked,
                'post.like_count': currentLikeCount
              });
            }
          },
          fail: (err) => {
            console.log('网络错误:', err);
            // 网络失败时也恢复状态
            wx.showToast({ title: '网络错误', icon: 'none' });
            this.setData({
              'post.is_liked': currentIsLiked,
              'post.like_count': currentLikeCount
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
  
      handleFollow: function() {
        const token = wx.getStorageSync('token');
        const post = this.data.post || {};
        const authorId = post.user_id;
        const currentUserId = wx.getStorageSync('user_id');

        console.log("post:", post);
        console.log("authorId:", authorId);

        
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
  
        // 获取当前状态
        const currentIsFollowed = this.data.post.is_followed || false;

        // 乐观更新UI
        const newIsFollowed = !currentIsFollowed;

        // 使用正确的数据路径更新
        this.setData({
            'post.is_followed': newIsFollowed
        });

  
       // 根据当前状态决定是关注还是取消关注
       const method = newIsFollowed ? 'POST' : 'DELETE';
       const url = `http://localhost:5001/api/follow/${authorId}`;
  
        wx.request({
          url: url,
          method: method,
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