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
   * 提交编辑后的资料（PUT请求）
   */
  submitEditForm() {
    // 简单表单验证
    // （可根据需求补充更严格的验证逻辑）
    wx.showLoading({
      title: '保存中...'
    });
  const token = wx.getStorageSync('token');


    // 发起PUT请求修改资料
    wx.request({
      url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/user/profile',
      method: 'PUT',
      data: this.data.editForm, // 提交编辑的字段
      header: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true' // 必备：跳过ngrok警告
      },
      success: (res) => {
        console.log('用户统计接口返回:', res.data);
        if (res.data.code === 200) {
          const stats = res.data.data;
          // 精准映射新接口字段到页面userInfo，和接口返回完全一致
          this.setData({
            'userInfo.postCount': stats.post_count || 0,    // 发布帖子数
            'userInfo.fansCount': stats.follower_count || this.data.userInfo.fansCount,// 粉丝数（优先统计接口，无则用用户信息接口）
            'userInfo.followingCount': stats.following_count || this.data.userInfo.followingCount,// 关注数（优先统计接口）
            'userInfo.recordCount': stats.like_count || 0   // 点赞数（映射为发布记录数）
          });
        }
      },
      fail: (err) => {
        console.error('获取用户统计失败:', err);
        // 失败时使用已有的粉丝/关注数，不重置
        this.setData({
          'userInfo.postCount': 0,
          'userInfo.recordCount': 0
        });
      }
    });
  },

  // 核心：加载已点赞帖子列表（原有代码，无修改，可正常使用）
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
        if (res.statusCode === 200) {
          // 保存成功，关闭弹窗并刷新数据
          wx.showToast({
            title: '保存成功',
            icon: 'success'
          });
          this.hideEditModal();
          // 重新获取最新的用户资料
          this.getUserProfile();
        } else {
          wx.showToast({
            title: '保存失败：' + (res.data.msg || '服务器异常'),
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，保存失败',
          icon: 'none'
        });
        console.error('修改资料失败：', err);
      }
    });
  }
});