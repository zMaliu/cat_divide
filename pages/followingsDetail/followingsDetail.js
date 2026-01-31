Page({
  data: {
    totalFollowings: 0,  // 关注总数
    followingsList: [],  // 关注用户列表
    loading: true,       // 加载状态
    showDetailModal: false, // 详细信息弹窗显示状态
    currentUser: {}      // 当前选中的用户数据
  },

  onLoad(options) {
    // 接收从个人中心传递的关注数（转数字+兜底，避免参数异常）
    const totalFollowings = Number(options.totalFollowings) || 0;
    this.setData({ totalFollowings });

    // 加载真实关注列表数据
    this.loadFollowingsList();
  },

  /**
   * 加载关注列表（对接 /api/follow/my-followings 接口）
   */
  loadFollowingsList() {
    // 优先取缓存token，无则用兜底token（与粉丝页逻辑一致）
    const token = wx.getStorageSync('token') || 'b03c6d6d-7179-484e-a707-db29e1de5f31';
    const followingsUrl = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/follow/my-followings?page=1&per_page=20';

    wx.request({
      url: followingsUrl,
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'  // 跳过ngrok警告，必加
      },
      success: (res) => {
        console.log('关注列表接口返回:', res.data);
        if (res.data.code === 200 && res.data.data) {
          const { followings, total } = res.data.data;

          // 数据格式化：处理头像路径（相对路径→完整URL）、字段兜底
          const formatFollowings = followings.map(user => ({
            ...user,
            // 拼接头像完整URL（接口返回 /default.jpg 或自定义路径）
            user_avatar: user.user_avatar 
              ? (user.user_avatar.startsWith('http') 
                ? user.user_avatar  // 若为完整URL直接使用
                : `https://silva-nonpyogenic-vincenza.ngrok-free.dev${user.user_avatar}`) 
              : '../../assets/avatar2.png',  // 兜底头像
            // 简介为空时兜底
            user_bio: user.user_bio || ''
          }));

          this.setData({
            followingsList: formatFollowings,
            totalFollowings: total || this.data.totalFollowings,  // 优先用接口总数
            loading: false
          });
        } else {
          // 接口返回异常（如无数据）
          this.setData({
            followingsList: [],
            loading: false
          });
          wx.showToast({
            title: res.data.msg || '加载关注列表失败',
            icon: 'none',
            duration: 1500
          });
        }
      },
      fail: (err) => {
        console.error('加载关注列表失败:', err);
        this.setData({
          followingsList: [],
          loading: false
        });
        wx.showToast({
          title: '网络错误，加载失败',
          icon: 'none',
          duration: 1500
        });
      }
    });
  },
  showUserDetail(e) {
    const user = e.currentTarget.dataset.user;
    this.setData({
      showDetailModal: true,
      currentUser: user // 传递当前用户的完整数据
    });
  },

  /**
   * 隐藏用户详细信息弹窗
   */
  hideUserDetail() {
    this.setData({
      showDetailModal: false,
      currentUser: {}
    });
  },

  /**
   * 阻止弹窗点击穿透
   */
  stopPropagation() {},
  /**
   * 取消关注（前端交互+预留接口对接）
   */
  toggleUnfollow(e) {
    const userId = e.currentTarget.dataset.userid;
    const { followingsList, totalFollowings } = this.data;

    // 1. 前端先更新状态（优化交互体验，避免等待接口）
    const newFollowingsList = followingsList.filter(user => user.user_id !== userId);
    this.setData({
      followingsList: newFollowingsList,
      totalFollowings: totalFollowings - 1  // 总数同步减少
    });

    // 2. 提示用户操作结果
    wx.showToast({
      title: '已取消关注',
      icon: 'none',
      duration: 1500
    });

    // 3. 实际项目中对接「取消关注」接口（示例代码，需替换真实接口）
    // const token = wx.getStorageSync('token');
    // if (!token) return;
    // wx.request({
    //   url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/follow/unfollow',
    //   method: 'POST',
    //   header: { 'Authorization': 'Bearer ' + token },
    //   data: { user_id: userId },  // 传递目标用户ID
    //   success: (res) => {
    //     if (res.data.code !== 200) {
    //       // 接口失败：回滚前端状态
    //       wx.showToast({ title: '取消关注失败', icon: 'none' });
    //       this.setData({
    //         followingsList,
    //         totalFollowings
    //       });
    //     }
    //   },
    //   fail: () => {
    //     // 网络失败：回滚状态
    //     wx.showToast({ title: '网络错误，操作失败', icon: 'none' });
    //     this.setData({
    //       followingsList,
    //       totalFollowings
    //     });
    //   }
    // });
  },

  /**
   * 跳转到关注用户的个人主页（预留扩展）
   */
  goToUserHome(e) {
    const user = e.currentTarget.dataset.user;
    // 传递用户ID和用户名，便于个人主页获取数据
    wx.navigateTo({
      url: `/pages/userHome/userHome?userId=${user.user_id}&nickname=${encodeURIComponent(user.user_name)}`,
    });
  },

  /**
   * 空状态“去发现”按钮：跳转至用户发现页（预留）
   */
  goToDiscover() {
    wx.navigateTo({
      url: '/pages/discover/discover',  // 需创建对应发现页
    });
  }
});
