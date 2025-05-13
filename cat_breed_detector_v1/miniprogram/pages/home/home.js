// pages/home/home.js

Page({
    data: {
      posts: [
        {
          id: 1,
          img: '/assets/demo1.jpg',
          title: '五一放假回来宿舍进猫',
          desc: '五一放假回来宿舍进猫，哪位是猫的主人，请尽快私信然后来认领',
          avatar: '/assets/avatar1.jpg',
          nickname: '**',
          content: '五一放假回来宿舍进猫，哪位是猫的主人，请尽快私信然后来认领',
          tags: ['迷路的小猫', '猫猫招领', '银渐层', '宿舍进可爱小猫', '安全保护','乖顺小猫','五一假期放假返校'],
          likeCount: 45
        },
        // ...更多帖子
      ]
    },
    goDetail(e) {
        const post = e.currentTarget.dataset.post
        wx.navigateTo({
          url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`
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