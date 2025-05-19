// pages/home/home.js

Page({
    data: {
      currentTab: 'hot', // 默认显示热点页面
      followPosts: [
        {
          id: 1,
          img: '/assets/demo2.jpg',
          title: '可爱小猫咪',
          desc: '家养小猫咪，很亲人，很可爱',
          avatar: '/assets/avatar2.jpg',
          nickname: '蓝猫',
          likeCount: 12
        },
        {
          id: 2,
          img: '/assets/demo4.jpg',
          title: '小猫日常照片分享',
          desc: '很有意思的照片',
          avatar: '/assets/avatar4.jpg',
          nickname: '里里山野',
          likeCount: 13
        },

        {
          id: 3,
          img: '/assets/demo3.jpg',
          title: '慵懒小猫咪',
          desc: '雨天的慵懒小猫咪',
          avatar: '/assets/avatar3.jpg',
          nickname: '小区居民',
          likeCount: 15
        },
        {
          id: 4,
          img: '/assets/demo5.jpg',
          title: '兔耳朵小猫',
          desc: '给小猫戴上兔耳朵',
          avatar: '/assets/avatar2.jpg',
          nickname: '蓝猫',
          likeCount: 18
        }
        // ...更多附近帖子
      ],
  
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
        }
      ],

      nearbyPosts: [
        {
          id: 1,
          img: '/assets/demo2.jpg',
          title: '可爱小猫咪',
          desc: '家养小猫咪，很亲人，很可爱',
          avatar: '/assets/avatar2.jpg',
          nickname: '蓝猫',
          likeCount: 12
        },
        {
          id: 2,
          img: '/assets/demo4.jpg',
          title: '小猫日常照片分享',
          desc: '很有意思的照片',
          avatar: '/assets/avatar4.jpg',
          nickname: '里里山野',
          likeCount: 13
        },
        {
          id: 3,
          img: '/assets/demo3.jpg',
          title: '慵懒小猫咪',
          desc: '雨天的慵懒小猫咪',
          avatar: '/assets/avatar3.jpg',
          nickname: '小区居民',
          likeCount: 15
        },
        {
          id: 4,
          img: '/assets/demo5.jpg',
          title: '兔耳朵小猫',
          desc: '给小猫戴上兔耳朵',
          avatar: '/assets/avatar2.jpg',
          nickname: '蓝猫',
          likeCount: 18
        },
        {
          id: 5,
          img: '/assets/demo6.jpg',
          title: '小猫日常照片分享',
          desc: '很有意思的照片',
          avatar: '/assets/avatar4.jpg',
          nickname: '里里山野',
          likeCount: 13
        }
        // ...更多附近帖子
      ]
    
    },

    onLoad: function() {
      // 保持原有数据不变
    },

    switchTab: function(e) {
      const tab = e.currentTarget.dataset.tab;
      this.setData({
        currentTab: tab
      });
    },

    goDetail(e) {
      const post = e.currentTarget.dataset.post
      wx.navigateTo({
        url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`
      })
    },

    goFollow() {
      wx.navigateTo({
        url: '/pages/follow/follow'
      });
    },

    goNearby() {
      wx.navigateTo({
        url: '/pages/nearby/nearby'
      });
    },

    goSearch() {
      wx.navigateTo({
        url: '/pages/search/search'
      });
    },
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