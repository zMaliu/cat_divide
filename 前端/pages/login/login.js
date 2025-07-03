Page({
    data: {
      currentTab: 'login', // 当前选中的标签：login 或 register
    //   loginForm: {
    //     user_name: '',
    //     password: ''
    //   },
      registerForm: {
        user_name: '',
        password: ''
      },
      
    },

    // 事件函数
    // 下面这两个函数第一次忘记写了，这个是能传数据的关键函数，一个input就要有一个函数来接受数据 
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

      // 用kimi做编程的ai

    handleRegister: function () {
        const { user_name, password } = this.data.registerForm;
        //console.log函数可以获取日志  帮助检查错误
        console.log("user_name",user_name);
        console.log("password",password);
        wx.request({
            url: 'http://localhost:5001/api/register',
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
                if (res.data.success) {
                wx.showToast({
                    title: '注册成功',
                    icon: 'success'
                });
                }
                else {
                    wx.showToast({
                    title: res.data.error || '注册失败',
                    icon: 'none'
                    });
                }
                }
            })
    }
});