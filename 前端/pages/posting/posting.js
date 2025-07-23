Page({
    data: {
      postingForm: {
        title: '',
        content: ''
      },
      uploadedImages: [],
      isSubmitting: false
    },

    onPostingTitleInput: function (e) {
        this.setData({
          'postingForm.title': e.detail.value
        });
    },

    onPostingContentInput: function (e) {
        this.setData({
          'postingForm.content': e.detail.value
        });
    },

    // 选择图片
    chooseImage: function() {
        const that = this;
        wx.chooseImage({
            count: 9 - that.data.uploadedImages.length,
            sizeType: ['compressed'],
            sourceType: ['album', 'camera'],
            success: function(res) {
                // 返回选定照片的本地文件路径列表
                that.setData({
                    uploadedImages: [...that.data.uploadedImages, ...res.tempFilePaths]
                });
            }
        });
    },

    // 移除图片
    removeImage: function(e) {
        const index = e.currentTarget.dataset.index;
        let images = this.data.uploadedImages;
        images.splice(index, 1);
        this.setData({
            uploadedImages: images
        });
    },

    // 上传图片到服务器
    uploadImages: function(postId) {
        const that = this;
        const images = that.data.uploadedImages;
        const token = wx.getStorageSync('token');
        const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
        
        if (images.length === 0) {
            return Promise.resolve([]);
        }

        return new Promise((resolve, reject) => {
            const uploadTasks = images.map((imagePath, index) => {
                return new Promise((res, rej) => {
                    wx.uploadFile({
                        url: 'http://localhost:5001/api/post/upload-image',
                        filePath: imagePath,
                        name: 'image',
                        header: {
                            'Authorization': authToken
                        },
                        formData: {
                            'post_id': postId,
                            'index': index
                        },
                        success: function(resp) {
                            const data = JSON.parse(resp.data);
                            if (data.code === 200) {
                                res(data.data);
                            } else {
                                rej(data.msg || '上传图片失败');
                            }
                        },
                        fail: function(error) {
                            rej(error);
                        }
                    });
                });
            });

            Promise.all(uploadTasks)
                .then(results => {
                    resolve(results);
                })
                .catch(error => {
                    reject(error);
                });
        });
    },

    handlePosting: function () {
        if (this.data.isSubmitting) {
            return;
        }

        const that = this;
        const { title, content } = this.data.postingForm;
        
        // 表单验证
        if (!title.trim()) {
            wx.showToast({
                title: '请输入标题',
                icon: 'none'
            });
            return;
        }
        
        if (!content.trim()) {
            wx.showToast({
                title: '请输入内容',
                icon: 'none'
            });
            return;
        }
        
        const token = wx.getStorageSync('token');
        if (!token) {
            wx.showToast({
                title: '请先登录',
                icon: 'none'
            });
            wx.navigateTo({
                url: '/pages/login/login'
            });
            return;
        }
        
        // 使用适当的token格式
        const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
        
        this.setData({
            isSubmitting: true
        });

        wx.showLoading({
            title: '发布中...'
        });
        
        wx.request({
            url: 'http://localhost:5001/api/post/create',
            method: 'POST',
            header: {
                'Content-Type': 'application/json',
                'Authorization': authToken
            },
            data: {
                title: title,
                content: content
            },
            success: (res) => {
                if (res.data.code === 200) {
                    const postId = res.data.data.post_id;
                    
                    // 如果有图片，上传图片
                    if (that.data.uploadedImages.length > 0) {
                        that.uploadImages(postId)
                            .then(() => {
                                wx.hideLoading();
                                wx.showToast({
                                    title: '发布成功',
                                    icon: 'success'
                                });
                                
                                setTimeout(() => {
                                    // 跳转到首页查看最新发布的帖子
                                    wx.switchTab({
                                        url: '/pages/home/home'
                                    });
                                }, 1500);
                            })
                            .catch(err => {
                                wx.hideLoading();
                                wx.showToast({
                                    title: '图片上传失败，请重试',
                                    icon: 'none'
                                });
                                console.error("图片上传失败:", err);
                            })
                            .finally(() => {
                                that.setData({
                                    isSubmitting: false
                                });
                            });
                    } else {
                        wx.hideLoading();
                        wx.showToast({
                            title: '发布成功',
                            icon: 'success'
                        });
                        
                        setTimeout(() => {
                            // 跳转到首页查看最新发布的帖子
                            wx.switchTab({
                                url: '/pages/home/home'
                            });
                        }, 1500);
                        
                        that.setData({
                            isSubmitting: false
                        });
                    }
                } else {
                    wx.hideLoading();
                    wx.showToast({
                        title: res.data.msg || '发布失败',
                        icon: 'none'
                    });
                    that.setData({
                        isSubmitting: false
                    });
                }
            },
            fail: (err) => {
                wx.hideLoading();
                wx.showToast({
                    title: '网络错误，请稍后重试',
                    icon: 'none'
                });
                console.error("发布失败:", err);
                that.setData({
                    isSubmitting: false
                });
            }
        });
    }
});