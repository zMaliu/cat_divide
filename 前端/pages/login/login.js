Page({
    data: {
      currentTab: 'login', 
      loginForm: {
        user_name: '',
        password: ''
      },
      registerForm: {
        user_name: '',
        password: ''
      },
      
    },

    // 切换到登录标签
    switchToLogin: function () {
        this.setData({
        currentTab: 'login'
        });
    },

    // 切换到注册标签
    switchToRegister: function () {
        this.setData({
        currentTab: 'register'
        });
    },

    onRegister_username_Input: function (e) {
        this.setData({
          'registerForm.user_name': e.detail.value
        });
      },

    onRegisterPasswordInput: function (e) {
        this.setData({
          'registerForm.password': e.detail.value
        });
      },

      onLogin_username_Input: function (e) {
        this.setData({
          'loginForm.user_name': e.detail.value
        });
      },

    onLoginPasswordInput: function (e) {
        this.setData({
          'loginForm.password': e.detail.value
        });
      },

    handleRegister: function () {
        const { user_name, password } = this.data.registerForm;

        if (!user_name.trim()) {
            wx.showToast({
                title: '请输入用户名',
                icon: 'none'
            });
            return;
        }

        if (!password || password.length < 6) {
            wx.showToast({
                title: '密码至少为6位',
                icon: 'none'
            });
            return;
        }

        wx.showLoading({
            title: '注册中...'
        });

        wx.request({
            url: 'http://localhost:5001/api/auth/register',
            method: 'POST',
            header: {
            'Content-Type': 'application/json'
            },
            data: {
            user_name: user_name,
            password: password
            },
            success: (res) => {
                wx.hideLoading();
                if (res.data.code === 200) {
                    wx.showToast({
                        title: '注册成功',
                        icon: 'success'
                    });
                    console.log("注册成功:", res.data);    
                    
                    // 注册成功后切换到登录
                    setTimeout(() => {
                        this.setData({
                        currentTab: 'login',
                        loginForm: {
                            user_name: user_name,
                            password: password
                        }
                    });
                  }, 1500);
                } else {
                    wx.showToast({
                        title: res.data.msg || '注册失败',
                        icon: 'none'
                    });
                }
            },
            fail: (err) => {
                wx.hideLoading();
                wx.showToast({
                    title: '网络错误，请稍后重试',
                    icon: 'none'
                });
                console.error("注册请求失败:", err);
            }
        });
    },

    handleLogin: function () {
        const { user_name, password } = this.data.loginForm;
        
        if (!user_name.trim()) {
            wx.showToast({
                title: '请输入用户名',
                icon: 'none'
            });
            return;
        }

        if (!password) {
            wx.showToast({
                title: '请输入密码',
                icon: 'none'
            });
            return;
        }

        wx.showLoading({
            title: '登录中...'
        });
        
        wx.request({
            url: 'http://localhost:5001/api/auth/login',
            method: 'POST',
            header: {
                'Content-Type': 'application/json'
            },
            data: {
                user_name: user_name,
                password: password
            },
            success: (res) => {
                wx.hideLoading();
                if (res.data.code === 200) {
                    // 添加Bearer前缀
                    const token = `Bearer ${res.data.data.token}`;
                    wx.setStorageSync('token', token);
                    wx.setStorageSync('user_id', res.data.data.user_id);
                    
                    console.log("保存的token:", token);
                    console.log("保存的user_id:", res.data.data.user_id);
                    
                    wx.showToast({
                        title: '登录成功',
                        icon: 'success'
                    });
    
                    // 跳转到主页面
                    setTimeout(() => {
                        wx.switchTab({
                            url: '/pages/home/home'
                        });
                    }, 1500);
                } else {
                    wx.showToast({
                        title: res.data.msg || '登录失败',
                        icon: 'none'
                    });
                }
            },
            fail: (err) => {
                wx.hideLoading();
                wx.showToast({
                    title: '网络错误，请稍后重试',
                    icon: 'none'
                });
                console.error("登录请求失败:", err);
            }
        });
    }
});