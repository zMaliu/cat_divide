// pages/postDetail/postDetail.js

Page({
    data: {
      post: {},
      isFollowed: false,
      likeCount: 0,
      starCount: 0,
      commentCount: 0,
      isLiked: false,
      isStarred: false,
      inputValue: '',
      comments: [
      // 示例评论
       { id: 1, avatar: '/assets/avatar2.jpg', nickname: '小明', text: '好可爱的猫！' }
    ]
    },
    onLoad(options) {
      console.log('接收到的参数：', options);
      if (options.data) {
        try {
          const postData = JSON.parse(decodeURIComponent(options.data));
          console.log('解析后的数据：', postData);
          this.setData({
            post: postData,
            likeCount: postData.likeCount || 0,
            starCount: postData.starCount || 0,
            commentCount: postData.commentCount || 0
          });
        } catch (error) {
          console.error('数据解析错误：', error);
          wx.showToast({
            title: '数据加载失败',
            icon: 'none'
          });
        }
      } else {
        console.error('未接收到数据');
        wx.showToast({
          title: '未接收到数据',
          icon: 'none'
        });
      }
    },
    onInput(e) {
      this.setData({
        inputValue: e.detail.value
      })
    },
    onSendComment() {
      const text = this.data.inputValue.trim()
      if (!text) {
        wx.showToast({ title: '请输入评论内容', icon: 'none' })
        return
      }
      const newComment = {
        id: Date.now(),
        avatar: '/assets/my_avatar.jpg', // 可换成当前用户头像
        nickname: '我', // 可换成当前用户昵称
        text
      }
      this.setData({
        comments: [...this.data.comments, newComment],
        inputValue: '',
        commentCount: this.data.commentCount + 1
      })
      wx.showToast({ title: '评论成功', icon: 'none' })
    },
    onFollow() {
      this.setData({
        isFollowed: !this.data.isFollowed
      })
      wx.showToast({
        title: this.data.isFollowed ? '已关注' : '已取消关注',
        icon: 'none'
      })
    },
    onShare() {
      wx.showShareMenu({
        withShareTicket: true
      })
      wx.showToast({
        title: '已调起分享',
        icon: 'none'
      })
    },
    onLike() {
      let { isLiked, likeCount } = this.data
      this.setData({
        isLiked: !isLiked,
        likeCount: isLiked ? likeCount - 1 : likeCount + 1
      })
    },
    onStar() {
      let { isStarred, starCount } = this.data
      this.setData({
        isStarred: !isStarred,
        starCount: isStarred ? starCount - 1 : starCount + 1
      })
    }
  })






// Page({

//     /**
//      * 页面的初始数据
//      */
//     data: {

//     },

//     /**
//      * 生命周期函数--监听页面加载
//      */
//     onLoad(options) {

//     },

//     /**
//      * 生命周期函数--监听页面初次渲染完成
//      */
//     onReady() {

//     },

//     /**
//      * 生命周期函数--监听页面显示
//      */
//     onShow() {

//     },

//     /**
//      * 生命周期函数--监听页面隐藏
//      */
//     onHide() {

//     },

//     /**
//      * 生命周期函数--监听页面卸载
//      */
//     onUnload() {

//     },

//     /**
//      * 页面相关事件处理函数--监听用户下拉动作
//      */
//     onPullDownRefresh() {

//     },

//     /**
//      * 页面上拉触底事件的处理函数
//      */
//     onReachBottom() {

//     },

//     /**
//      * 用户点击右上角分享
//      */
//     onShareAppMessage() {

//     }
// })