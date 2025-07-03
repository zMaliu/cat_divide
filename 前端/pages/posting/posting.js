Page({
    data: {
      currentTab: 'posting',
      postingForm: {
        photo: '',
        title: '',
        content:''
      },
    },

    onChoosePhoto: function(e) {
        wx.chooseImage({
            count:1,
            sizeType: ['original', 'compressed'],
            sourceType: ['album', 'camera'], 
            success: (res) => {
                this.setData({
                  'postingForm.photo': res.tempFilePaths[0]
                }); 
            }  
        })
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

    handleRegister: function () {
        const { photo,title,content } = this.data.postingForm;
        console.log("photo",photo);
        console.log("title",title);
        console.log("content",content);
        wx.request({
            url: 'http://localhost:5001/api/register',
            method: 'POST',
            //filePath: imagePath,
            filePath: this.data.postingForm.image,
            header: {
            'Content-Type': 'application/json'
            },
            data: {
                photo: photo,
                title: title,
                content:content
            },
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