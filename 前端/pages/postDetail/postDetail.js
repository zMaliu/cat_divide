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
        success: (res) => {
          if (res.data && res.data.data && res.data.data.post) {
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
      }
  });