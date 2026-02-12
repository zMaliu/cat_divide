<<<<<<< HEAD
Page({
  data: {
    userInfo: {}, // 存储用户信息
    loading: true, // 加载状态
    error: false, // 错误状态
    showEditModal: false, // 编辑弹窗显示状态
    editForm: { // 编辑表单数据
      user_bio: '',
      user_location: '',
      user_birthday: ''
    }
  },

  onLoad: function() {
    // 页面加载时获取用户资料
    this.getUserProfile();
  },

  /**
   * 获取用户个人资料（适配新接口）
   */
  getUserProfile() {
    const token = wx.getStorageSync('token');

    wx.request({
      url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/auth/get_user_info',
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token,
        'ngrok-skip-browser-warning': 'true' // 新增：跳过ngrok警告
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.code === 200) {
          // 新接口返回的data嵌套在res.data.data中
          const userInfo = res.data.data;
          this.setData({
            userInfo: userInfo,
            loading: false,
            error: false
          });
        } else {
          this.handleRequestError('获取资料失败：' + (res.data.msg || '接口返回异常'));
        }
      },
      fail: (err) => {
        this.handleRequestError('网络错误，请检查网络连接');
        console.error('请求失败：', err);
      }
    });
  },

  /**
   * 处理请求失败
   */
  handleRequestError(msg) {
    this.setData({
      loading: false,
      error: true
    });
    wx.showToast({
      title: msg || '获取资料失败',
      icon: 'none'
    });
  },

  /**
   * 打开编辑资料弹窗
   */
  onEditProfile() {
    // 打开弹窗时，将当前用户信息填充到表单
    const { user_bio, user_location, user_birthday } = this.data.userInfo;
    this.setData({
      showEditModal: true,
      editForm: {
        user_bio: user_bio || '',
        user_location: user_location || '',
        user_birthday: user_birthday || ''
      }
    });
  },

  /**
   * 关闭编辑资料弹窗
   */
  hideEditModal() {
    this.setData({
      showEditModal: false
    });
  },

  /**
   * 阻止弹窗点击穿透
   */
  stopPropagation() {},

  /**
   * 输入框内容变化
   */
  onInputChange(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({
      [`editForm.${key}`]: e.detail.value
    });
  },

  /**
   * 生日选择器变化
   */
  onBirthdayChange(e) {
    this.setData({
      'editForm.user_birthday': e.detail.value
    });
  },

  /**
   * 提交编辑后的资料（修复后的 PUT 请求）
   */
  submitEditForm() {
    // 简单表单验证（可选：可补充长度限制等）
    if (!this.data.editForm) {
      wx.showToast({
        title: '请填写编辑内容',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '保存中...'
    });

    const token = wx.getStorageSync('token');
    // 发起正确的 PUT 请求修改资料
    wx.request({
      url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/user/profile',
      method: 'PUT', // 明确 PUT 方法
      data: this.data.editForm, // 提交编辑的字段（简介、地区、生日）
      header: {
        'Authorization': 'Bearer ' + token, // 携带登录令牌
        'Content-Type': 'application/json', // JSON 格式提交
        'ngrok-skip-browser-warning': 'true' // 跳过 ngrok 浏览器警告
      },
      success: (res) => {
        wx.hideLoading(); // 必须隐藏加载提示
        console.log('修改资料返回结果：', res.data);
        // 处理接口响应（适配后端返回格式：{code, msg, data}）
        if (res.statusCode === 200 && (res.data.code === 200 || res.data.code === 0)) {
          wx.showToast({
            title: '保存成功',
            icon: 'success'
          });
          this.hideEditModal(); // 关闭编辑弹窗
          this.getUserProfile(); // 重新获取最新用户资料
        } else {
          wx.showToast({
            title: '保存失败：' + (res.data.msg || '服务器异常'),
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading(); // 失败也要隐藏加载提示
        wx.showToast({
          title: '网络错误，保存失败',
          icon: 'none'
        });
        console.error('修改资料请求失败：', err);
      }
    });
  },

  // 加载已点赞帖子列表（保留原有逻辑，和修改资料解耦）
  loadLikedPosts: function() {
    const token = wx.getStorageSync('token') || 'b03c6d6d-7179-484e-a707-db29e1de5f31';
    const likedPostUrl = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/like/my-liked?page=1&per_page=20';
  
    wx.showLoading({
      title: '加载点赞列表...',
      mask: true
    });
  
    wx.request({
      url: likedPostUrl,
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'
      },
      success: (res) => {
        wx.hideLoading();
        if (res.statusCode === 200 && res.data.code === 200) {
          // 这里处理点赞列表的逻辑（比如渲染列表）
          console.log('点赞列表数据：', res.data.data);
          // 示例：如果需要存储点赞列表
          // this.setData({ likedPosts: res.data.data.list });
          wx.showToast({
            title: '点赞列表加载成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: '加载点赞列表失败：' + (res.data.msg || '接口异常'),
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，加载失败',
          icon: 'none'
        });
        console.error('加载点赞列表失败：', err);
      }
    });
  }
=======
Page({
  data: {
    userInfo: {}, // 存储用户信息
    loading: true, // 加载状态
    error: false, // 错误状态
    showEditModal: false, // 编辑弹窗显示状态
    editForm: { // 编辑表单数据
      user_bio: '',
      user_location: '',
      user_birthday: ''
    }
  },

  onLoad: function() {
    // 页面加载时获取用户资料
    this.getUserProfile();
  },

  /**
   * 获取用户个人资料（适配新接口）
   */
  getUserProfile() {
    const token = wx.getStorageSync('token');

    wx.request({
      url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/auth/get_user_info',
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token,
        'ngrok-skip-browser-warning': 'true' // 新增：跳过ngrok警告
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.code === 200) {
          // 新接口返回的data嵌套在res.data.data中
          const userInfo = res.data.data;
          this.setData({
            userInfo: userInfo,
            loading: false,
            error: false
          });
        } else {
          this.handleRequestError('获取资料失败：' + (res.data.msg || '接口返回异常'));
        }
      },
      fail: (err) => {
        this.handleRequestError('网络错误，请检查网络连接');
        console.error('请求失败：', err);
      }
    });
  },

  /**
   * 处理请求失败
   */
  handleRequestError(msg) {
    this.setData({
      loading: false,
      error: true
    });
    wx.showToast({
      title: msg || '获取资料失败',
      icon: 'none'
    });
  },

  /**
   * 打开编辑资料弹窗
   */
  onEditProfile() {
    // 打开弹窗时，将当前用户信息填充到表单
    const { user_bio, user_location, user_birthday } = this.data.userInfo;
    this.setData({
      showEditModal: true,
      editForm: {
        user_bio: user_bio || '',
        user_location: user_location || '',
        user_birthday: user_birthday || ''
      }
    });
  },

  /**
   * 关闭编辑资料弹窗
   */
  hideEditModal() {
    this.setData({
      showEditModal: false
    });
  },

  /**
   * 阻止弹窗点击穿透
   */
  stopPropagation() {},

  /**
   * 输入框内容变化
   */
  onInputChange(e) {
    const key = e.currentTarget.dataset.key;
    this.setData({
      [`editForm.${key}`]: e.detail.value
    });
  },

  /**
   * 生日选择器变化
   */
  onBirthdayChange(e) {
    this.setData({
      'editForm.user_birthday': e.detail.value
    });
  },

  /**
   * 提交编辑后的资料（修复后的 PUT 请求）
   */
  submitEditForm() {
    // 简单表单验证（可选：可补充长度限制等）
    if (!this.data.editForm) {
      wx.showToast({
        title: '请填写编辑内容',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '保存中...'
    });

    const token = wx.getStorageSync('token');
    // 发起正确的 PUT 请求修改资料
    wx.request({
      url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/user/profile',
      method: 'PUT', // 明确 PUT 方法
      data: this.data.editForm, // 提交编辑的字段（简介、地区、生日）
      header: {
        'Authorization': 'Bearer ' + token, // 携带登录令牌
        'Content-Type': 'application/json', // JSON 格式提交
        'ngrok-skip-browser-warning': 'true' // 跳过 ngrok 浏览器警告
      },
      success: (res) => {
        wx.hideLoading(); // 必须隐藏加载提示
        console.log('修改资料返回结果：', res.data);
        // 处理接口响应（适配后端返回格式：{code, msg, data}）
        if (res.statusCode === 200 && (res.data.code === 200 || res.data.code === 0)) {
          wx.showToast({
            title: '保存成功',
            icon: 'success'
          });
          this.hideEditModal(); // 关闭编辑弹窗
          this.getUserProfile(); // 重新获取最新用户资料
        } else {
          wx.showToast({
            title: '保存失败：' + (res.data.msg || '服务器异常'),
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading(); // 失败也要隐藏加载提示
        wx.showToast({
          title: '网络错误，保存失败',
          icon: 'none'
        });
        console.error('修改资料请求失败：', err);
      }
    });
  },

  // 加载已点赞帖子列表（保留原有逻辑，和修改资料解耦）
  loadLikedPosts: function() {
    const token = wx.getStorageSync('token') || 'b03c6d6d-7179-484e-a707-db29e1de5f31';
    const likedPostUrl = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/like/my-liked?page=1&per_page=20';
  
    wx.showLoading({
      title: '加载点赞列表...',
      mask: true
    });
  
    wx.request({
      url: likedPostUrl,
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'
      },
      success: (res) => {
        wx.hideLoading();
        if (res.statusCode === 200 && res.data.code === 200) {
          // 这里处理点赞列表的逻辑（比如渲染列表）
          console.log('点赞列表数据：', res.data.data);
          // 示例：如果需要存储点赞列表
          // this.setData({ likedPosts: res.data.data.list });
          wx.showToast({
            title: '点赞列表加载成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: '加载点赞列表失败：' + (res.data.msg || '接口异常'),
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，加载失败',
          icon: 'none'
        });
        console.error('加载点赞列表失败：', err);
      }
    });
  }
>>>>>>> d0fa90f2a95da012597ce7f762a23c5ddc39bf71
});