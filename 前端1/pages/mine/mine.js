const config = require('../../utils/config.js')

Page({
  data: {
    // 用户信息（初始为空）
    userInfo: {
      avatar: '../../assets/avatar2.jpg',
      nickname: '明明',
      intro: '',
      loveLevel: '0☆',
      postCount: 0,
      recordCount: 0,
      fansCount: 0,
      followingCount: 0
    },
    isLoggedIn: false,
    
    // 标签状态
    activeTab: 'publish', // publish, like, collect
    
    // 喜欢标签的子选项
    likeSubTab: 'post', // post, record
    showLikeDropdown: false,
    
    // 空状态显示
    showEmptyState: false,

    //初始化点赞帖子数组，适配空状态  
    publishedPosts: [],
    likedPosts: [], // 已点赞帖子列表
    feedRecords: [],
    healthRecords: [],
    collections: [] // 收藏列表（已初始化，无需修改）
  },

  onLoad: function() {
    // 页面加载
    this.loadUserInfo();
    this.updateEmptyState();
  },

  onShow: function() {
    // 页面显示时重新加载（可能修改了资料/新增收藏/点赞）
    this.loadUserInfo();
    if (this.data.activeTab === 'publish') { // 新增：发布标签加载对应数据
      this.loadPublishedPosts();
    } else if (this.data.activeTab === 'like') {
      this.loadLikedPosts();
    } else if (this.data.activeTab === 'collect') {
      this.loadCollections();
    }
    this.updateEmptyState();
  },

  // 加载用户信息（适配新接口返回格式+优化数据映射）
  loadUserInfo: function() {
    // 优先缓存token，无则用固定token兜底（关键：固定token也能加载统计/点赞/收藏）
    const token = wx.getStorageSync('token') || 'b03c6d6d-7179-484e-a707-db29e1de5f31';
    const userId = wx.getStorageSync('user_id');
    
    // 修复：|| 或的关系，无token/无userId都算未登录（原先是&&，逻辑错误）
    if (!token || !userId) {
      // 未登录：重置用户信息，固定token仍可加载统计/点赞/收藏
      this.setData({
        isLoggedIn: false,
        userInfo: {
          avatar: '../../assets/avatar2.png',
          nickname: '明明',
          loveLevel: '0☆',
          postCount: 0,
          recordCount: 0,
          fansCount: 0,
          followingCount: 0
        }
      });
      // 未登录也加载统计数据（固定token兜底）
      this.loadUserStats(token);
      return;
    }

    this.setData({ isLoggedIn: true });

    // 获取用户基本信息（有userId时才请求）
    wx.request({
      url:'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/auth/get_user_info',
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token,
        'ngrok-skip-browser-warning': 'true' // 新增：跳过ngrok警告
      },
      success: (res) => {
        console.log('用户基本信息接口返回:', res.data);
        if (res.data.code === 200) {
          const userData = res.data.data;
          // 适配新接口返回格式的精准映射
          this.setData({
            'userInfo.nickname': userData.user_name || '用户',
            // 处理头像路径：接口返回相对路径，拼接完整域名
            'userInfo.avatar': userData.user_avatar 
              ? `https://silva-nonpyogenic-vincenza.ngrok-free.dev${userData.user_avatar}` 
              : '../../assets/avatar2.png',
            // 处理个性签名：null转为友好提示
            'userInfo.intro': userData.user_bio || '这个人很懒，什么都没写',
            'userInfo.loveLevel': '0☆',
            // 直接从用户信息接口获取粉丝和关注数（无需等统计接口）
            'userInfo.fansCount': userData.follower_count || 0,
            'userInfo.followingCount': userData.following_count || 0
          });
        } else if (res.data.code === 401) {
          // token失效，清除登录状态
          wx.removeStorageSync('token');
          wx.removeStorageSync('user_id');
          this.setData({ 
            isLoggedIn: false,
            // 重置用户信息
            userInfo: {
              avatar: '../../assets/avatar2.png',
              nickname: '明明',
              loveLevel: '0☆',
              postCount: 0,
              recordCount: 0,
              fansCount: 0,
              followingCount: 0
            }
          });
        } else {
          // 其他错误，给出提示
          wx.showToast({
            title: res.data.msg || '获取用户信息失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('获取用户信息失败:', err);
        // 请求失败时仍保证页面有默认数据
        this.setData({
          'userInfo.nickname': '明明',
          'userInfo.avatar': '../../assets/avatar2.png',
          'userInfo.intro': '这个人很懒，什么都没写'
        });
      },
      complete: () => {
        // 无论用户信息是否请求成功，都加载统计数据
        this.loadUserStats(token);
      }
    });
  },

  // 加载用户统计数据（核心适配新接口：移除userId参数+修复打印错误+对接新地址）
  loadUserStats: function(token) {
    // 修复：移除无用的userId参数，对接新的统计接口地址
    wx.request({
      url: 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/user/my-stats',
      method: 'GET',
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
        console.log('已点赞帖子接口返回:', res.data);
        
        // 添加详细的调试信息
        console.log('接口状态码:', res.statusCode);
        console.log('headers:', res.header);
        
        if (res.data.code === 200 && res.data.data && res.data.data.posts) {
          console.log('进入条件分支');
          console.log('rawLikedPosts 原始数据:', JSON.stringify(res.data.data.posts, null, 2));
          
          const rawLikedPosts = res.data.data.posts;
          
          try {
            // 测试 map 函数
            console.log('开始 map 操作');
            
            const formatLikedPosts = rawLikedPosts.map((post, index) => {
              console.log(`处理第 ${index} 个帖子:`, post);
              
              // 返回映射对象
              return {
                id: post.article_id,
                title: post.title || '无标题帖子',
                author: post.user_name || '未知作者',
                image: post.img ? `https://silva-nonpyogenic-vincenza.ngrok-free.dev${post.img}` : '../../assets/avatar2.png',
                likedTime: post.liked_time,
                time: post.publish_time,
                likeCount: post.like_count || 0,
                replyCount: post.reply_count || 0,
                isLiked: post.is_liked
              };
            });
            
            console.log('formatLikedPosts 结果:', JSON.stringify(formatLikedPosts, null, 2));
            console.log('formatLikedPosts 长度:', formatLikedPosts.length);
            
            this.setData({ likedPosts: formatLikedPosts });
            
            if (formatLikedPosts.length === 0) {
              wx.showToast({ 
                title: '还没有点赞过任何帖子', 
                icon: 'none', 
                duration: 2000 
              });
            }
          } catch (error) {
            console.error('映射过程中出现错误:', error);
            console.error('错误详情:', error.stack);
            this.setData({ likedPosts: [] });
            wx.showToast({ 
              title: '数据处理失败', 
              icon: 'none', 
              duration: 2000 
            });
          }
        } else {
          console.log('条件不满足:');
          console.log('res.data.code:', res.data.code);
          console.log('res.data.data:', res.data.data);
          console.log('res.data.data.posts:', res.data.data ? res.data.data.posts : '无data');
          
          this.setData({ likedPosts: [] });
          wx.showToast({ 
            title: '暂无点赞帖子', 
            icon: 'none', 
            duration: 2000 
          });
        }
      },
      fail: (err) => {
        console.error('加载已点赞帖子失败:', err);
        this.setData({ likedPosts: [] });
        wx.showToast({ 
          title: '网络错误，加载失败', 
          icon: 'none', 
          duration: 2000 
        });
      },
      complete: () => {
        wx.hideLoading();
        this.updateEmptyState();
      }
    });
  },

  // 加载收藏列表（原有代码，无修改，可正常使用）
  loadCollections: function() {
    // 优先使用缓存token，无则用固定token兜底
    const token = wx.getStorageSync('token') || 'b03c6d6d-7179-484e-a707-db29e1de5f31';
    // 你指定的收藏接口完整地址
    const collectUrl = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/favorite/my-favorites?page=1&per_page=20';

    // 显示加载中提示，提升体验
    wx.showLoading({
      title: '加载收藏列表...',
      mask: true
    });

    wx.request({
      url: collectUrl,
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + token, // token认证
        'Content-Type': 'application/json', // json格式
        'ngrok-skip-browser-warning': 'true' // 跳过ngrok的浏览器安全验证
      },
      success: (res) => {
        console.log('收藏列表接口返回:', res.data);
        // 精准匹配接口业务码200，且存在posts数组
        if (res.data.code === 200 && res.data.data && res.data.data.posts) {
          const rawCollections = res.data.data.posts;
          // 精准映射接口字段到collections，适配WXML渲染
          const formatCollections = rawCollections.map(item => ({
            id: item.article_id, // 收藏内容ID（接口返回article_id）
            title: item.title || '无标题内容', // 标题
            type: '文章', // 收藏类型，接口均为帖子/文章，固定为文章即可
            // 收藏时间：接口返回favorited_time，格式如2026-01-27 23:13:59
            time: `收藏于${item.favorited_time}`,
            // 额外保留字段，方便后续扩展（可选）
            author: item.user_name || '未知作者',
            image: item.img ? `https://silva-nonpyogenic-vincenza.ngrok-free.dev${item.img}` : '../../assets/avatar2.png',
            publishTime: item.publish_time,
            likeCount: item.like_count || 0
          }));
          // 更新收藏列表数据
          this.setData({ collections: formatCollections });
          // 无收藏数据时友好提示
          if (formatCollections.length === 0) {
            wx.showToast({ title: '还没有收藏任何内容', icon: 'none', duration: 2000 });
          }
        } else {
          // 接口返回异常，置空收藏数据
          this.setData({ collections: [] });
          wx.showToast({ title: '暂无收藏内容', icon: 'none', duration: 2000 });
        }
      },
      fail: (err) => {
        // 网络错误、接口地址错误等请求失败情况
        console.error('加载收藏列表失败:', err);
        this.setData({ collections: [] });
        wx.showToast({ title: '网络错误，收藏加载失败', icon: 'none', duration: 2000 });
      },
      complete: () => {
        // 无论成功/失败，隐藏加载提示，更新空状态
        wx.hideLoading();
        this.updateEmptyState();
      }
    });
  },
  loadPublishedPosts: function() {
    // 优先取缓存token，无则用兜底token
    const token = wx.getStorageSync('token') || 'b03c6d6d-7179-484e-a707-db29e1de5f31';
    const publishUrl = 'https://silva-nonpyogenic-vincenza.ngrok-free.dev/api/post/my-posts?page=1&per_page=20';

    // 显示加载提示，提升体验
    wx.showLoading({
      title: '加载发布帖子...',
      mask: true
    });

    wx.request({
      url: publishUrl,
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + '078fc17c-ac92-4c15-b03b-627c51ef1042',
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true' // 必加，跳过ngrok警告
      },
      success: (res) => {
        console.log('已发布帖子接口返回:', res.data);
        if (res.data.code === 200 && res.data.data && res.data.data.posts) {
          const rawPosts = res.data.data.posts;
          // 适配接口字段，格式化数据（和页面WXML渲染字段对应）
          const formatPosts = rawPosts.map(post => ({
            id: post.article_id, // 帖子ID
            title: post.title || '无标题', // 帖子标题
            content: post.content || '', // 帖子内容（可选展示）
            image: post.img ? `https://silva-nonpyogenic-vincenza.ngrok-free.dev${post.img}` : '../../assets/avatar2.png', // 拼接头像完整URL
            likeCount: post.like_count || 0, // 点赞数
            replyCount: post.reply_count || 0, // 评论数
            time: post.publish_time, // 发布时间
            isLiked: post.is_liked || false // 是否被自己点赞
          }));

          this.setData({
            publishedPosts: formatPosts,
            // 同步更新发布帖子数（优先用接口返回的total）
            'userInfo.postCount': res.data.data.total || this.data.userInfo.postCount
          });

          // 无发布数据时友好提示
          if (formatPosts.length === 0) {
            wx.showToast({
              title: '还没有发布任何帖子',
              icon: 'none',
              duration: 2000
            });
          }
        } else {
          // 接口返回异常（如无数据）
          this.setData({ publishedPosts: [] });
          wx.showToast({
            title: res.data.msg || '暂无发布帖子',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('加载已发布帖子失败:', err);
        this.setData({ publishedPosts: [] });
        wx.showToast({
          title: '网络错误，加载失败',
          icon: 'none'
        });
      },
      complete: () => {
        wx.hideLoading();
        this.updateEmptyState(); // 更新空状态
      }
    });
  },

  // 更新空状态（原有代码，无修改）
  updateEmptyState: function() {
    let showEmpty = false;
    
    if (this.data.activeTab === 'publish') {
      showEmpty = this.data.publishedPosts.length === 0;
    } else if (this.data.activeTab === 'like') {
      if (this.data.likeSubTab === 'post') {
        showEmpty = this.data.likedPosts.length === 0;
      } else if (this.data.likeSubTab === 'record') {
        showEmpty = this.data.feedRecords.length === 0 && this.data.healthRecords.length === 0;
      }
    } else if (this.data.activeTab === 'collect') {
      showEmpty = this.data.collections.length === 0;
    }
    
    this.setData({ showEmptyState: showEmpty });
  },

  // 标签切换（原有代码，无修改）
  onTabChange: function(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({
      activeTab: tab,
      showLikeDropdown: false
    });
    
    // 切换到对应标签时加载对应数据
    if (tab === 'publish') { // 新增：发布标签加载发布帖子
      this.loadPublishedPosts();
    } else if (tab === 'like') {
      this.loadLikedPosts();
    } else if (tab === 'collect') {
      this.loadCollections();
    }
    
    this.updateEmptyState();
  },


  // 喜欢标签的下拉切换（原有代码，无修改）
  onLikeDropdownToggle: function() {
    this.setData({
      showLikeDropdown: !this.data.showLikeDropdown
    });
  },

  // 喜欢子标签切换（原有代码，无修改）
  onLikeSubTabChange: function(e) {
    const subTab = e.currentTarget.dataset.subtab;
    this.setData({
      likeSubTab: subTab,
      showLikeDropdown: false
    });
    this.updateEmptyState();
  },

  // 头像点击（原有代码，无修改）
  onAvatarTap: function() {
    wx.showToast({ title: '头像功能开发中', icon: 'none' });
  },

  // 编辑个人资料（原有代码，无修改）
  onEditProfile: function() {
    wx.navigateTo({ url: '/pages/editProfile/editProfile' });
  },

  // 设置（原有代码，无修改）
  onSettings: function() {
    wx.navigateTo({ url: '/pages/settings/settings' });
  },

  // 移除原有单独的 onFollowingList 方法，逻辑整合到 onStatsClick 中
  // 粉丝、关注、帖子、记录点击（核心修改：新增关注数跳转逻辑）
  onStatsClick: function(e) {
    const type = e.currentTarget.dataset.type;  
    // 点击粉丝时跳转到粉丝列表页面
    if (type === '粉丝') {
      wx.navigateTo({
        url: `/pages/fansDetail/fansDetail?totalFans=${this.data.userInfo.fansCount}`,
      });
      return;
    }
    // 新增：点击关注时跳转到关注列表页面
    if (type === '关注') {
      wx.navigateTo({
        url: `/pages/followingsDetail/followingsDetail?totalFollowings=${this.data.userInfo.followingCount}`,
      });
      return;
    }
    // 其他类型（帖子、记录等）仍显示开发中提示
    wx.showToast({ title: type + '详情开发中', icon: 'none' });
  },

  // 发布作品（原有代码，无修改）
  onPosting: function() {
    wx.navigateTo({ url: '/pages/posting/posting' });
  },

  // 帖子详情（原有代码，无修改）
  onPostDetail: function(e) {
    const post = e.currentTarget.dataset.post;
    wx.navigateTo({
      url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}`
    });
  }
});