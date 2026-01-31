Page({
  data: {
    totalFans: 0,    // 粉丝总数
    fansList: [],    // 粉丝列表
    loading: true    // 加载状态
  },

  onLoad(options) {
    // 接收从个人中心传递的粉丝数（兜底值）
    const totalFans = Number(options.totalFans) || 0;
    this.setData({ totalFans });
    
    // 加载真实的粉丝列表数据
    this.loadFansList();
  },

  /**
   * 加载真实粉丝列表（对接 /api/follow/my-followers 接口）
   */
  loadFansList() {
    // 优先取缓存token，无则用兜底token
    const token = 'b03c6d6d-7179-484e-a707-db29e1de5f31';
    const fansUrl = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/follow/my-followers?page=1&per_page=20';

    wx.request({
      url: fansUrl,
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true' // 跳过ngrok警告
      },
      success: (res) => {
        console.log('粉丝列表接口返回:', res.data);
        if (res.data.code === 200 && res.data.data) {
          const { followers, total } = res.data.data;
          
          // 适配接口字段，处理头像路径（相对路径转完整URL）
          const formatFans = followers.map(fan => ({
            ...fan,
            // 拼接头像完整URL（接口返回 /default.jpg → 完整域名+路径）
            user_avatar: fan.user_avatar 
              ? `https://silva-nonpyogenic-vincenza.ngrok-free.dev${fan.user_avatar}` 
              : '../../assets/avatar2.png'
          }));

          this.setData({
            fansList: formatFans,
            totalFans: total || this.data.totalFans, // 优先用接口返回的总数
            loading: false
          });
        } else {
          // 接口返回异常（如无数据）
          this.setData({
            fansList: [],
            loading: false
          });
          wx.showToast({
            title: res.data.msg || '加载粉丝列表失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('加载粉丝列表失败:', err);
        this.setData({
          fansList: [],
          loading: false
        });
        wx.showToast({
          title: '网络错误，加载失败',
          icon: 'none'
        });
      }
    });
  },

  /**
   * 关注/取消关注粉丝（交互逻辑，可对接实际关注接口）
   */
  toggleFollow(e) {
    const userId = e.currentTarget.dataset.userid;
    const isFollowed = e.currentTarget.dataset.isfollowed;
    const { fansList } = this.data;

    // 1. 先更新页面状态（前端交互优化）
    const newFansList = fansList.map(fan => {
      if (fan.user_id === userId) {
        return { ...fan, is_following_back: !isFollowed };
      }
      return fan;
    });
    this.setData({ fansList: newFansList });

    // 2. 提示用户操作结果
    wx.showToast({
      title: !isFollowed ? '已关注' : '已取消关注',
      icon: 'none',
      duration: 1500
    });

    // 3. 实际项目中调用「关注/取消关注」接口（示例）
    // const token = wx.getStorageSync('token');
    // wx.request({
    //   url: `https://xxx/api/follow/${!isFollowed ? 'follow' : 'unfollow'}`,
    //   method: 'POST',
    //   header: { 'Authorization': 'Bearer ' + token },
    //   data: { user_id: userId },
    //   success: (res) => {
    //     if (res.data.code !== 200) {
    //       wx.showToast({ title: '操作失败', icon: 'none' });
    //       // 失败则回滚状态
    //       this.setData({ fansList });
    //     }
    //   }
    // });
  },

  /**
   * 跳转到粉丝个人主页（预留，可扩展）
   */
  goToUserHome(e) {
    const user = e.currentTarget.dataset.user;
    wx.navigateTo({
      url: `/pages/userHome/userHome?userId=${user.user_id}&nickname=${user.user_name}`,
    });
  }
});