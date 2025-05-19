// pages/nearby/nearby.js
Page({
  data: {
    nearbyPosts: []
  },

  onLoad: function() {
    this.loadNearbyPosts();
  },

  loadNearbyPosts: function() {
    this.setData({
      nearbyPosts: [
        {
          id: 1,
          img: '/assets/demo4.jpg',
          title: '小区门口发现银渐层',
          desc: '在小区门口发现一只银渐层，看起来像是走丢的，很亲人',
          avatar: '/assets/avatar4.jpg',
          nickname: '小区居民',
          content: '今天在小区门口发现一只银渐层，看起来像是走丢的，很亲人，会主动蹭人。特征：银灰色毛发，眼睛是蓝色的，脖子上有蓝色项圈。如有主人看到请速来认领。',
          tags: ['银渐层', '走失', '小区门口', '亲人', '蓝色项圈'],
          likeCount: 156
        },
        {
          id: 2,
          img: '/assets/demo5.jpg',
          title: '猫咪寄养服务',
          desc: '提供专业猫咪寄养服务，有独立房间，24小时监控',
          avatar: '/assets/avatar5.jpg',
          nickname: '专业寄养师',
          content: '提供专业猫咪寄养服务，有独立房间，24小时监控，定期消毒。可提供猫粮、猫砂，也可自带。价格合理，欢迎咨询。地址：朝阳区望京西园四区。',
          tags: ['寄养', '专业', '24小时监控', '独立房间', '望京'],
          likeCount: 342
        },
        {
          id: 3,
          img: '/assets/demo6.jpg',
          title: '猫咪用品团购',
          desc: '组织小区猫咪用品团购，包括猫粮、猫砂、玩具等',
          avatar: '/assets/avatar6.jpg',
          nickname: '团购组织者',
          content: '组织小区猫咪用品团购，包括猫粮、猫砂、玩具等。价格比市场价便宜20%-30%，质量保证。有意向的铲屎官可以加入团购群。',
          tags: ['团购', '猫粮', '猫砂', '玩具', '优惠'],
          likeCount: 178
        }
      ]
    });
  },

  goDetail(e) {
    const post = e.currentTarget.dataset.post
    wx.navigateTo({
      url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`
    })
  }
}); 