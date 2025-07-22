Page({
    data: {
      currentTab: 'posting',
      postingForm: {
        // photo: '',
        title: '',
        content:''
      },
    },


    onPostingTitleInput: function (e) {
        this.setData({
          'postingForm.title': e.detail.value
        });
        //console.log(e);
    },

    onPostingContentInput: function (e) {
        this.setData({
          'postingForm.content': e.detail.value
        });
    },

    handlePosting: function () {
        const token = wx.getStorageSync('token');
        const { title,content } = this.data.postingForm;  //这一步是定义变量
        // console.log("photo",photo);
        console.log("token", token);
        console.log("title",title);
        console.log("content",content);
        wx.request({
            url: 'http://localhost:5001/api/post/create',
            method: 'POST',
            
            header: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
            },
            data: {
                // photo: photo,
                title: title,
                content:content
            },
            
            withCredentials: true, // 关键
            success: (res) => {
                wx.hideLoading();
                if (res.data.code == 200) {
                wx.showToast({
                    title: '发布成功',
                    icon: 'success'
                });
                
                setTimeout(() => {
                    wx.switchTab({
                        url: '/pages/mine/mine'
                    });
                }, 1500);

                }
                else {
                    wx.showToast({
                    title: res.data.msg || '发布失败',
                    icon: 'none'
                    });
                }
            }
        })
    }
});