Page({
  data: {},

  onLoad: function () {
    // 2秒后自动跳转到选择页面
    setTimeout(() => {
      wx.redirectTo({
        url: '/pages/login/login'
      });
    }, 2000);
  },

  onShow: function () {
    // 隐藏导航栏
    wx.hideHomeButton();
  }
});
