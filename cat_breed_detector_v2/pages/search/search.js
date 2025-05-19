Page({
  data: {
    keyword: '',
    resultList: []
  },
  onInput(e) {
    this.setData({
      keyword: e.detail.value
    });
  },
  onSearch() {
    const keyword = this.data.keyword.trim();
    if (!keyword) {
      wx.showToast({ title: '请输入关键词', icon: 'none' });
      return;
    }
    // 这里用模拟数据，实际开发可请求后端
    const allPosts = [
      // 可以把 home.js 里的所有帖子都放进来
      {
        id: 1,
        img: '/assets/demo2.jpg',
        title: '可爱小猫咪',
        desc: '家养小猫咪，很亲人，很可爱'
      },
      {
        id: 2,
        img: '/assets/demo4.jpg',
        title: '小猫日常照片分享',
        desc: '很有意思的照片'
      }
      // ...更多帖子
    ];
    const result = allPosts.filter(post =>
      post.title.includes(keyword) || post.desc.includes(keyword)
    );
    this.setData({
      resultList: result
    });
  }
});
