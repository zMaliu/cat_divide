<<<<<<< HEAD
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
=======
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
>>>>>>> d0fa90f2a95da012597ce7f762a23c5ddc39bf71
