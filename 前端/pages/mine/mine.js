Page({
    currentTab:'mine',

    onPosting:function () {
        setTimeout(() => {
            wx.redirectTo({
              url: '/pages/posting/posting'
            });
          }, 1500);
        } 
    
});