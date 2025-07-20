Page({
    data: {
      currentTab: 'posting',
      postingForm: {
        photo: '',
        title: '',
        content: ''
      },
      selectedTag: '',
      isUploading: false
    },

    // 选择照片
    onChoosePhoto: function(e) {
        wx.chooseImage({
            count: 1,
            sizeType: ['original', 'compressed'],
            sourceType: ['album', 'camera'], 
            success: (res) => {
                this.setData({
                  'postingForm.photo': res.tempFilePaths[0]
                }); 
            }  
        });
    },

    // 移除已选照片
    removePhoto: function() {
        this.setData({
            'postingForm.photo': ''
        });
    },
    
    // 选择标签
    selectTag: function(e) {
        const tag = e.currentTarget.dataset.tag;
        this.setData({
            selectedTag: this.data.selectedTag === tag ? '' : tag
        });
    },

    onPostingTitleInput: function (e) {
        this.setData({
          'postingForm.title': e.detail.value.slice(0, 30)
        });
    },

    onPostingContentInput: function (e) {
        this.setData({
          'postingForm.content': e.detail.value.slice(0, 300)
        });
    },

    // 表单验证
    validateForm: function() {
      const { title, content } = this.data.postingForm;
      
      if (!title || title.trim() === '') {
        wx.showToast({
          title: '请输入标题',
          icon: 'none'
        });
        return false;
      }
      
      if (!content || content.trim() === '') {
        wx.showToast({
          title: '请输入内容',
          icon: 'none'
        });
        return false;
      }
      
      return true;
    },

    handlePosting: function () {
        if (!this.validateForm()) return;
        if (this.data.isUploading) return;  // 防止重复提交

        const token = wx.getStorageSync('token');
        const { photo, title, content } = this.data.postingForm;
        const tag = this.data.selectedTag;
        
        if (!token) {
          wx.showToast({
            title: '请先登录',
            icon: 'none'
          });
          setTimeout(() => {
            wx.navigateTo({
              url: '/pages/login/login'
            });
          }, 1500);
          return;
        }

        this.setData({ isUploading: true });

        // 显示上传中提示
        wx.showLoading({
          title: '发布中...',
          mask: true
        });

        // 使用默认猫咪图片的处理
        const imgToUpload = photo || '../../assets/Abyssinian_11.jpg';
        
        // 构建发布数据
        const postData = {
            title: title,
            content: content,
            img: imgToUpload
        };
        
        // 如果选择了标签，加入数据
        if (tag) {
            postData.tag = tag;
        }
        
        wx.request({
            url: 'http://localhost:5001/api/create',
            method: 'POST',
            header: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            data: postData,
            withCredentials: true,
            success: (res) => {
                wx.hideLoading();
                if (res.data.code === 200) {
                  wx.showToast({
                      title: '发布成功',
                      icon: 'success'
                  });
                  setTimeout(() => {
                      wx.switchTab({
                          url: '/pages/home/home'
                      });
                  }, 1500);
                }
                else {
                    wx.showToast({
                      title: res.data.msg || '发布失败',
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
            },
            complete: () => {
                this.setData({ isUploading: false });
            }
        });
    }
});