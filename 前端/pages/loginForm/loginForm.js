<<<<<<< HEAD
const config = require('../../utils/config.js')

Page({
  data: {
    loginForm: {
      user_name: '',
      password: ''
    }
  },

  onLoad: function (options) {
    // 如果从注册页面跳转过来，预填充用户名
    if (options.username) {
      this.setData({
        'loginForm.user_name': decodeURIComponent(options.username)
      });
    }
  },

  // 返回选择页面
  goBack: function () {
    wx.navigateBack();
  },

  // 用户名输入
  onUsernameInput: function (e) {
    this.setData({
      'loginForm.user_name': e.detail.value
    });
  },

  // 密码输入
  onPasswordInput: function (e) {
    this.setData({
      'loginForm.password': e.detail.value
    });
  },

  // 处理登录
  handleLogin: function () {
    const { user_name, password } = this.data.loginForm;
    
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

    // 显示加载
    wx.showLoading({
      title: '登录中...'
    });

    // 发起登录请求
    const requestUrl = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/auth/login';
    console.log('=== 登录调试信息 ===');
    console.log('完整URL:', requestUrl);
    console.log('config.apiURL:', config.apiURL);
    console.log('用户名:', user_name.trim());
    
    wx.request({
      url: requestUrl,
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
          // 保存登录信息
          wx.setStorageSync('token', res.data.data.token);
          wx.setStorageSync('user_id', res.data.data.user_id);
          console.log(res.data.data.token)
          wx.showToast({
            title: '登录成功',
            icon: 'success',
            duration: 1500
          });
          
          // 登录成功后跳转到首页
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/home/home'
            });
          }, 1500);
          
        } else {
          wx.showToast({
            title: res.data.msg || res.data.error || '登录失败',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('登录请求失败:', err);
        wx.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none',
          duration: 2000
        });
      }
    });
  }
});
=======
const config = require('../../utils/config.js')

Page({
  data: {
    loginForm: {
      user_name: '',
      password: ''
    }
  },

  onLoad: function (options) {
    // 如果从注册页面跳转过来，预填充用户名
    if (options.username) {
      this.setData({
        'loginForm.user_name': decodeURIComponent(options.username)
      });
    }
  },

  // 返回选择页面
  goBack: function () {
    wx.navigateBack();
  },

  // 用户名输入
  onUsernameInput: function (e) {
    this.setData({
      'loginForm.user_name': e.detail.value
    });
  },

  // 密码输入
  onPasswordInput: function (e) {
    this.setData({
      'loginForm.password': e.detail.value
    });
  },

  // 处理登录
  handleLogin: function () {
    const { user_name, password } = this.data.loginForm;
    
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

    // 显示加载
    wx.showLoading({
      title: '登录中...'
    });

    // 发起登录请求
    const requestUrl = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/auth/login';
    console.log('=== 登录调试信息 ===');
    console.log('完整URL:', requestUrl);
    console.log('config.apiURL:', config.apiURL);
    console.log('用户名:', user_name.trim());
    
    wx.request({
      url: requestUrl,
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
          // 保存登录信息
          wx.setStorageSync('token', res.data.data.token);
          wx.setStorageSync('user_id', res.data.data.user_id);
          console.log(res.data.data.token)
          wx.showToast({
            title: '登录成功',
            icon: 'success',
            duration: 1500
          });
          
          // 登录成功后跳转到首页
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/home/home'
            });
          }, 1500);
          
        } else {
          wx.showToast({
            title: res.data.msg || res.data.error || '登录失败',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('登录请求失败:', err);
        wx.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none',
          duration: 2000
        });
      }
    });
  }
});
>>>>>>> d0fa90f2a95da012597ce7f762a23c5ddc39bf71
