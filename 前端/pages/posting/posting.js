Page({
    data: {
      currentTab: 'posting',
      postingForm: {
        // photo: '',
        title: '',
        content:''
      },
    },

    // onChoosePhoto: function(e) {
    //     wx.chooseImage({
    //         count:1,
    //         sizeType: ['original', 'compressed'],
    //         sourceType: ['album', 'camera'], 
    //         success: (res) => {
    //             this.setData({
    //               'postingForm.photo': res.tempFilePaths[0]
    //             }); 
    //         }  
    //     })
    // },

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
        console.log("title",title);
        console.log("content",content);
        wx.request({
            url: 'http://localhost:5001/api/posting',
            method: 'POST',
            // filePath: photo,      photo变量本身就是一个路径，这个写法可以，下面这个也可以
            // filePath: this.data.postingForm.photo,
            // 对this的理解
            // this 让你能在页面的任意方法里访问和操作当前页面的数据。只要你在 data 里定义了变量，
            // 就可以通过this.data.xxx 访问。直接写变量名（如 imagePath）只有在你本函数里定义了才行，否则会报错。
            
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
                if (res.data.success) {
                wx.showToast({
                    title: '发布成功',
                    icon: 'success'
                });
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