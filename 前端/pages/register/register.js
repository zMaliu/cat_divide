Page({
  data: {
    registerForm: {
      user_name: '',
      password: ''
    }
  },

  onLoad: function () {
    // 页面初始化
  },

  // 返回选择页面
  goBack: function () {
    wx.navigateBack();
  },

  // 用户名输入
  onUsernameInput: function (e) {
    this.setData({
      'registerForm.user_name': e.detail.value
    });
  },

  // 密码输入
  onPasswordInput: function (e) {
    this.setData({
      'registerForm.password': e.detail.value
    });
  },

  // 处理注册
  handleRegister: function () {
    const { user_name, password } = this.data.registerForm;
    
    // 基本验证
    if (!user_name.trim()) {
      wx.showToast({
        title: '请输入用户名',
        icon: 'none'
      });
      return;
    }
    
    if (!password.trim()) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      });
      return;
    }
    
    if (password.length < 6) {
      wx.showToast({
        title: '密码至少6位',
        icon: 'none'
      });
      return;
    }

    // 显示加载
    wx.showLoading({
      title: '注册中...'
    });

    // 发起注册请求
    wx.request({
      url: 'http://localhost:5001/api/auth/register',
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        user_name: user_name.trim(),
        password: password
      },
      success: (res) => {
        wx.hideLoading();
        
        if (res.data.code === 200) {
          wx.showToast({
            title: '注册成功',
            icon: 'success',
            duration: 1500
          });
          
          // 注册成功后跳转到登录页面
          setTimeout(() => {
            wx.redirectTo({
              url: `/pages/loginForm/loginForm?username=${encodeURIComponent(user_name.trim())}`
            });
          }, 1500);
          
        } else {
          wx.showToast({
            title: res.data.msg || '注册失败',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('注册请求失败:', err);
        wx.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none',
          duration: 2000
        });
      }
    });
  }
});
