// pages/follow/follow.js
Page({
  data: {
    followPosts: []
  },

  onLoad: function() {
    console.log('onLoad follow'); // 1. 检查是否执行
    this.loadFollowPosts();
  },

  loadFollowPosts: function() {
    this.setData({
      followPosts: [
        {
          id: 1,
          img: '/assets/demo1.jpg',
          title: '我家英短蓝猫走丢了',
          desc: '在朝阳区望京SOHO附近走丢，特征：蓝灰色毛发，脖子上有红色项圈',
          avatar: '/assets/avatar1.jpg',
          nickname: '蓝猫主人',
          content: '我家英短蓝猫在朝阳区望京SOHO附近走丢了，特征：蓝灰色毛发，脖子上有红色项圈，性格温顺，不怕人。如有发现请立即联系我，必有重谢！',
          tags: ['英短蓝猫', '走失', '望京SOHO', '朝阳区', '重金酬谢'],
          likeCount: 128
        },
        {
          id: 2,
          img: '/assets/demo2.jpg',
          title: '布偶猫求领养',
          desc: '一岁布偶猫，因工作调动无法继续照顾，寻找有爱心的新主人',
          avatar: '/assets/avatar2.jpg',
          nickname: '布偶铲屎官',
          content: '一岁布偶猫，已绝育，疫苗齐全，性格温顺亲人。因工作调动无法继续照顾，希望找到有爱心的新主人。要求：有养猫经验，有稳定收入，能接受定期回访。',
          tags: ['布偶猫', '领养', '一岁', '已绝育', '疫苗齐全'],
          likeCount: 256
        },
        {
          id: 3,
          img: '/assets/demo3.jpg',
          title: '小区流浪猫救助',
          desc: '发现一只受伤的橘猫，需要医疗救助和临时安置',
          avatar: '/assets/avatar3.jpg',
          nickname: '爱心救助者',
          content: '在小区发现一只受伤的橘猫，后腿有外伤，需要及时就医。本人可以提供部分医疗费用，但需要有人帮忙照顾和安置。希望有经验的朋友能伸出援手。',
          tags: ['流浪猫', '救助', '橘猫', '医疗', '临时安置'],
          likeCount: 89
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