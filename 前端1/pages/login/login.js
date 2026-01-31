Page({
  data: {},

  onLoad: function () {
    // 选择页面初始化
  },

  // 跳转到注册页面
  goToRegister: function () {
    wx.navigateTo({
      url: '/pages/register/register'
    });
  },

  // 跳转到登录页面
  goToLogin: function () {
    wx.navigateTo({
      url: '/pages/loginForm/loginForm'
    });
  }
});