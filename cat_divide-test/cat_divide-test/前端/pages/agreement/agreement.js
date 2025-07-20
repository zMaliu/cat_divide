Page({
  data: {
    // 页面数据
  },
  
  onLoad: function() {
    // 页面加载时执行
  },
  
  navigateBack: function() {
    wx.navigateBack({
      delta: 1
    });
  }
}) 