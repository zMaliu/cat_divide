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

        console.log("user_name",user_name);
        console.log("password",password);
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
                if (res.data.code == 200) {
                wx.showToast({
                    title: '注册成功',
                    icon: 'success'
                });
                console.log("res.data", res.data);    
                console.log('准备跳转')
                // 注册成功后切换到登录
                setTimeout(() => {
                    this.setData({
                    currentTab: 'login',
                    loginForm: {
                        user_name:user_name,
                        password: password
                    }
                });
              }, 1500);
                console.log('跳转完成')
                }else {
                    wx.showToast({
                    title: res.data.msg || '注册失败',
                    icon: 'none'
                    });
                }
                }
            })
    },

    handleLogin: function () {
        const { user_name, password } = this.data.loginForm;
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
                if (res.data.code == 200) {
                wx.setStorageSync('token', res.data.data.token); 
                  wx.showToast({
                    title: '登录成功',
                    icon: 'success'
                  });
                   console.log("token",res.data.token);
    
                // 跳转到主页面
                setTimeout(() => {
                  wx.switchTab({
                    url: '/pages/home/home'
                  });
                }, 1500);
              } else {
                wx.showToast({
                  title: res.data.error || '登录失败',
                  icon: 'none'
                });
                }
            },
            fail: () => {
                wx.hideLoading();
                wx.showToast({
                  title: '网络错误，请稍后重试',
                  icon: 'none'
                });
            }
        });
    }
});