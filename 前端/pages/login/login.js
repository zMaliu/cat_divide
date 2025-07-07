Page({
    data: {
      currentTab: 'login', // 当前选中的标签：login 或 register
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

    // 事件函数
    // 这个是针对blindinput函数而言的，不是所有的input都要有一个函数，  这个叫做input的事件函数
    // 事件函数可以实时获取用户输入，比如保存到 data 里、做表单校验等，就要写事件函数。
    // 但只要你在 input 上写了 bindinput="xxx"（这个是在wxml里面写的），就必须在 JS 里有一个名为 xxx 的函数，否则小程序会报错。
    // onInputChange: function(e) {这里可以用 e.detail.value 拿到输入的内容}
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
        //console.log函数可以获取日志  帮助检查错误
        console.log("user_name",user_name);
        console.log("password",password);
        wx.request({
            url: 'http://127.0.0.1:5000/api/register',
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
                // 跳转到发作品
                console.log('准备跳转')
                setTimeout(() => {
                    wx.redirectTo({
                      url: '/pages/posting/posting'
                    });
                  }, 1500);
                  console.log('跳转完成')
                }
            //     // 注册成功后切换到登录
            //     setTimeout(() => {
            //         this.setData({
            //         currentTab: 'login',
            //         loginForm: {
            //             user_name:user_name,
            //             password: password
            //         }
            //     });
            //   }, 1500);
            //     } 
                else {
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
            url: 'http://127.0.0.1:5000/api/login',
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
                  // 保存用户信息到本地存储
                  wx.setStorageSync('userInfo', res.data.data);
                  
                  wx.showToast({
                    title: '登录成功',
                    icon: 'success'
                  });
    
                // 跳转到发作品
                setTimeout(() => {
                  wx.redirectTo({
                    url: '/pages/posting/posting.js'
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