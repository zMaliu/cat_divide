Page({
    data:{
        currentTab: 'hot', // 默认显示热点页面
        posts: []
    },

    onLoad: function() {
        wx.request({
          url: 'http://localhost:5001/api/post/list?per_page=100', 
          method: 'GET',
          success: (res) => {
            if (res.data.code === 200) {
              this.setData({
                posts: res.data.data.posts
              });
            } else {
              wx.showToast({
                title: res.data.msg || '获取作品失败',
                icon: 'none'
              });
            }
          }
        });
    },


    // 点击某个作品，跳转到详情页
    goToDetail: function(e) {
        const post = e.currentTarget.dataset.post;
        wx.navigateTo({
        url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`
        });
    }

});


