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
    handleRegister: function () {
        const { user_name, password } = this.data.
        registerForm;
        console.log("user_name",user_name);
        console.log("password",password);
        wx.request({
            url: 'http://10.45.103.50:5000/api/register',
            method: 'POST',
            header: {
            'Content-Type': 'application/json'
            },
            data: {
            user_name:user_name,
            password:password
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
                    title: res.data.msg || '注册失败',
                    icon: 'none'
                    });
                }
                }
            })
    }
});