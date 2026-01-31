const config = require('../../utils/config.js')

Page({
    data: {
        // 数据状态
        hotPicks: [],
        userToken: '',
        
        // 分页状态
        currentPage: 1,
        pageSize: 12,
        hasMore: true,
        autoLoadAll: true,  // 是否自动加载全部数据
        
        // 加载状态
        isLoading: false,
        isLoadingMore: false,
        loadError: false,
        noMoreData: false,
        
        // 滚动位置
        scrollTop: 0,
        isRestoringScroll: false  // 是否正在恢复滚动位置
    },

    onLoad: function() {
        this.initPage();
    },

    onShow: function() {
        // 每次显示页面时刷新token和数据
        const token = wx.getStorageSync('token');
        const oldToken = this.data.userToken || '';
        
        // 如果token发生变化，重新加载
        if (token !== oldToken) {
            this.setData({
                userToken: token
            });
            this.initPage();
            return;
        }
        
        // 获取全局变量中的刷新标志
        const app = getApp();
        if (app.globalData && app.globalData.needRefreshHome) {
            // 检查是否有更新的帖子数据（从详情页返回）
            if (app.globalData.updatedPost) {
                // 只更新对应的帖子，不重新加载整个列表
                const updatedPost = app.globalData.updatedPost;
                const index = app.globalData.updatedPostIndex;
                
                if (index >= 0 && index < this.data.hotPicks.length) {
                    const hotPicks = [...this.data.hotPicks];
                    // 只更新点赞和关注状态
                    hotPicks[index] = {
                        ...hotPicks[index],
                        is_liked: updatedPost.is_liked,
                        like_count: updatedPost.like_count,
                        is_followed: updatedPost.is_followed
                    };
                    
                    this.setData({ hotPicks }, () => {
                        // 更新数据后，恢复滚动位置
                        this.restoreScrollPosition();
                    });
                }
                
                // 清除全局数据
                app.globalData.updatedPost = null;
                app.globalData.updatedPostIndex = -1;
            }
            
            // 重置刷新标志
            app.globalData.needRefreshHome = false;
        } else {
            // 如果没有数据更新，等待数据加载完成后再恢复滚动位置
            // 检查是否已有数据
            if (this.data.hotPicks.length > 0) {
                // 有数据，立即恢复
                setTimeout(() => {
                    this.restoreScrollPosition();
                }, 300);
            } else {
                // 没有数据，等待加载完成
                // 数据加载完成后会在 loadHotPicks 的 setData 回调中调用 restoreScrollPosition
            }
        }
    },

    // 页面初始化
    initPage: function() {
        const token = wx.getStorageSync('token');
        this.setData({
            userToken: token,
            currentPage: 1,
            hotPicks: [],
            hasMore: true,
            autoLoadAll: true,  // 初始化时自动加载全部
            noMoreData: false,
            loadError: false,
            scrollTop: 0  // 初始化时重置滚动位置
        });
        // 清除保存的滚动位置
        wx.removeStorageSync('homeScrollTop');
        this.loadHotPicks(true);
    },

    // 加载热门精选
    loadHotPicks: function(isRefresh = false) {
        const { currentPage, pageSize, userToken, isLoading, isLoadingMore, autoLoadAll } = this.data;
        
        console.log('=== 开始加载 ===', {
            currentPage,
            isRefresh,
            isLoading,
            isLoadingMore,
            autoLoadAll,
            currentDataLength: this.data.hotPicks.length
        });
        
        // 防止重复请求
        if (isLoading || isLoadingMore) {
            console.log('⚠️ 请求被阻止：正在加载中');
            return;
        }
        
        // 设置加载状态
        if (isRefresh || currentPage === 1) {
            this.setData({ isLoading: true, isLoadingMore: false, loadError: false });
        } else {
            this.setData({ isLoadingMore: true, isLoading: false });
        }

        // 构建请求头
        const headers = {
            'Content-Type': 'application/json'
        };
        if (userToken) {
            headers['Authorization'] = `Bearer ${userToken}`;
        }

        // 构建热门精选请求
        let url = `${config.apiURL}/post/list?page=${currentPage}&per_page=${pageSize}`;

        wx.request({
            url: url,
            method: 'GET',
            header: headers,
            success: (res) => {
                console.log('热门精选API响应:', res.data);
                
                if (res.data.code === 200) {
                    const rawPets = res.data.data.posts || [];
                    console.log(`收到 ${rawPets.length} 条数据`);
                    
                    // 处理数据，补充缺失字段
                    const newPets = rawPets.map(item => ({
                        ...item,
                        // 处理图片字段，使用本地默认图片
                        img: item.img || '../../assets/default.jpg',
                        imgUrl: item.img === '/default.jpg' ? '../../assets/default.jpg' : (item.img && !item.img.startsWith('http') ? config.baseURL + item.img : (item.img || '../../assets/default.jpg')),
                        // 使用API返回的真实评论数
                        reply_count: item.reply_count || 0,
                        // 补充作者字段名统一
                        author: item.user_name || item.author || '匿名用户',
                        // 补充友好时间显示
                        time: item.time || this.formatTime(item.publish_time) || '刚刚'
                    }));
                    
                    // 合并数据 - 在首次加载或刷新时重置，其他情况累加
                    let allPets = [];
                    const autoLoadAll = this.data.autoLoadAll;
                    const currentPetsLength = this.data.hotPicks.length;
                    
                    if (isRefresh || currentPage === 1) {
                        // 首次加载或刷新时重置数据
                        allPets = newPets;
                        console.log(`首次加载/刷新，重置数据，当前${allPets.length}条`);
                    } else {
                        // 后续加载时累加数据
                        allPets = [...this.data.hotPicks, ...newPets];
                        console.log(`累加数据：之前${currentPetsLength}条 + 新增${newPets.length}条 = 总计${allPets.length}条`);
                    }
                    
                    // 检查是否还有更多数据
                    const hasMore = newPets.length >= pageSize;
                    console.log(`是否有更多数据：${hasMore} (本次返回${newPets.length}条，每页${pageSize}条)`);
                    console.log(`自动加载模式：${autoLoadAll}`);
                    
                    // 如果开启了自动加载全部，且还有更多数据，自动加载下一页
                    if (hasMore && autoLoadAll) {
                        console.log(`✅ 继续自动加载，当前第${currentPage}页，准备加载第${currentPage + 1}页`);
                        
                        // 先更新数据和页码
                        this.setData({
                            hotPicks: allPets,
                            currentPage: currentPage + 1,
                            loadError: false
                        }, () => {
                            // setData回调完成后，重置加载状态，然后继续加载
                            this.setData({
                                isLoading: false,
                                isLoadingMore: false  // 先关闭，避免阻止下次请求
                            }, () => {
                                console.log(`状态已重置，2秒后继续加载第${currentPage + 1}页...`);
                                // 延迟一下再加载下一页，避免请求过快
                                setTimeout(() => {
                                    this.loadHotPicks(false);
                                }, 500);
                            });
                        });
                    } else {
                        // 没有更多数据了，或者手动上拉加载，完成加载
                        console.log(`⏹️ 停止自动加载 - hasMore: ${hasMore}, autoLoadAll: ${autoLoadAll}`);
                        this.setData({
                            hotPicks: allPets,
                            hasMore: hasMore,
                            autoLoadAll: false,  // 关闭自动加载
                            noMoreData: !hasMore && allPets.length > 0,
                            currentPage: currentPage,
                            isLoading: false,
                            isLoadingMore: false,
                            loadError: false
                        }, () => {
                            // 数据加载完成后，恢复滚动位置
                            this.restoreScrollPosition();
                        });
                        
                        if (!hasMore) {
                            console.log(`✅ 热门精选加载完成: 总共${allPets.length}条数据`);
                        } else {
                            console.log(`ℹ️ 当前已加载${allPets.length}条数据（还有更多，但自动加载已关闭）`);
                        }
                    }
                } else {
                    console.error('API返回错误:', res.data);
                    this.handleLoadError(res.data.msg || '加载失败');
                }
            },
            fail: (err) => {
                console.error('请求失败:', err);
                this.handleLoadError('网络请求失败，请检查网络连接');
            }
        });
    },

    // 处理加载错误
    handleLoadError: function(errorMsg) {
        this.setData({
            isLoading: false,
            isLoadingMore: false,
            loadError: true
        });
        
        wx.showToast({
            title: errorMsg,
            icon: 'none',
            duration: 2000
        });
    },

    // 手动刷新按钮
    onManualRefresh: function() {
        console.log('手动刷新');
        wx.showLoading({ title: '刷新中...' });
        
        // 清除保存的滚动位置
        wx.removeStorageSync('homeScrollTop');
        
        this.setData({
            currentPage: 1,
            hotPicks: [],
            hasMore: true,
            autoLoadAll: true,  // 刷新时重新开启自动加载全部
            noMoreData: false,
            scrollTop: 0  // 重置滚动位置
        });
        
        this.loadHotPicks(true);
        
        setTimeout(() => {
            wx.hideLoading();
        }, 500);
    },

    // 上拉加载更多
    loadMorePets: function() {
        console.log('触发上拉加载');
        const { hasMore, isLoadingMore, isLoading } = this.data;
        
        if (!hasMore || isLoadingMore || isLoading) {
            console.log('无法加载更多:', { hasMore, isLoadingMore, isLoading });
            return;
        }
        
        this.setData({
            currentPage: this.data.currentPage + 1
        });
        this.loadHotPicks(false);
    },

    // 重试加载
    retryLoad: function() {
        console.log('重试加载');
        this.loadHotPicks(true);
    },

    // 功能按钮事件
    goToMap: function() {
        wx.showToast({
            title: '地图功能开发中',
            icon: 'none'
        });
    },

    goToFiles: function() {
        wx.navigateTo({
            url: '/pages/catArchive/catArchive'
        });
    },

    goToMonitor: function() {
        wx.showToast({
            title: '实时监测功能开发中',
            icon: 'none'
        });
    },

    // 点赞/取消点赞
    toggleLike: function(e) {
        const { postId, index } = e.currentTarget.dataset;
        const token = this.data.userToken;
        
        if (!token) {
            wx.showToast({
                title: '请先登录',
                icon: 'none'
            });
            return;
        }
        
        const hotPicks = [...this.data.hotPicks];
        const pet = hotPicks[index];
        
        if (!pet) return;
        
        // 使用与详情页相同的简单逻辑
        const currentIsLiked = pet.is_liked === 1 || pet.is_liked === true;
        const newIsLiked = !currentIsLiked;
        const method = newIsLiked ? 'POST' : 'DELETE';
        const url = `${config.apiURL}/like/${postId}`;
        
        wx.request({
            url: url,
            method: method,
            header: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            success: (res) => {
                if (res.data.code === 200) {
                    wx.showToast({ 
                        title: newIsLiked ? '点赞成功' : '取消点赞成功', 
                        icon: 'success' 
                    });
                    
                    // 重新加载首页数据，确保显示最新状态
                    this.refreshData();
                } else {
                    wx.showToast({
                        title: res.data.msg || '操作失败',
                        icon: 'none'
                    });
                }
            },
            fail: () => {
                wx.showToast({
                    title: '网络错误',
                    icon: 'none'
                });
            }
        });
    },
    
    // 刷新数据方法
    refreshData: function() {
        this.setData({
            currentPage: 1,
            hotPicks: [],
            hasMore: true,
            autoLoadAll: true,  // 刷新时重新开启自动加载全部
            noMoreData: false,
            loadError: false
        });
        this.loadHotPicks(true);
    },

    // 跳转到消息页面
    goToMessage: function() {
        wx.navigateTo({
            url: '/pages/message/message'
        });
    },

    // 跳转到识别页面
    goToRecognition: function() {
        wx.navigateTo({
            url: '/pages/index/index'
        });
    },

    // 跳转到发布页面
    goToPosting: function() {
        const token = this.data.userToken;
        if (!token) {
            wx.showModal({
                title: '提示',
                content: '请先登录后再发布内容',
                showCancel: false,
                success: () => {
                    wx.switchTab({
                        url: '/pages/mine/mine'
                    });
                }
            });
            return;
        }
        
        wx.navigateTo({
            url: '/pages/posting/posting'
        });
    },

    // 跳转到宠物详情页
    goToPetDetail: function(e) {
        const pet = e.currentTarget.dataset.pet;
        const index = e.currentTarget.dataset.index;
        if (!pet) return;
        
        // 保存当前滚动位置（使用当前data中的值）
        const currentScrollTop = this.data.scrollTop || 0;
        console.log('💾 保存滚动位置:', currentScrollTop);
        wx.setStorageSync('homeScrollTop', currentScrollTop);
        
        wx.navigateTo({
            url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(pet))}&fromPage=home&fromIndex=${index}`
        });
    },

    // 跳转到详情页（保留兼容性）
    goToDetail: function(e) {
        const post = e.currentTarget.dataset.post;
        const index = e.currentTarget.dataset.index;
        if (!post) return;
        
        // 保存当前滚动位置
        const currentScrollTop = this.data.scrollTop;
        wx.setStorageSync('homeScrollTop', currentScrollTop);
        
        wx.navigateTo({
            url: `/pages/postDetail/postDetail?data=${encodeURIComponent(JSON.stringify(post))}&fromPage=home&fromIndex=${index}`
        });
    },
    
    // scroll-view 的滚动事件
    onScroll: function(e) {
        // 如果正在恢复滚动位置，不更新data，避免冲突
        if (this.data.isRestoringScroll) {
            return;
        }
        
        // 保存滚动位置
        const scrollTop = e.detail.scrollTop || 0;
        // 实时保存滚动位置到本地存储
        wx.setStorageSync('homeScrollTop', scrollTop);
        // 更新data中的值
        if (Math.abs(scrollTop - (this.data.scrollTop || 0)) > 5) {
            this.setData({
                scrollTop: scrollTop
            });
        }
    },
    
    // 恢复滚动位置
    restoreScrollPosition: function() {
        const savedScrollTop = wx.getStorageSync('homeScrollTop');
        const dataLength = this.data.hotPicks.length;
        console.log('🔄 尝试恢复滚动位置:', savedScrollTop, '当前数据条数:', dataLength);
        
        if (savedScrollTop && savedScrollTop > 0 && dataLength > 0) {
            // 设置恢复标记，避免onScroll干扰
            this.setData({
                isRestoringScroll: true
            });
            
            // 使用多次延迟确保DOM完全渲染
            const restoreScroll = () => {
                // 先设置为0，触发一次变化
                this.setData({
                    scrollTop: 0
                }, () => {
                    // 短暂延迟后设置为目标值
                    setTimeout(() => {
                        this.setData({
                            scrollTop: savedScrollTop,
                            isRestoringScroll: false
                        });
                        console.log(`✅ 已恢复滚动位置: ${savedScrollTop}`);
                    }, 200);
                });
            };
            
            // 延迟执行，确保页面和数据都已准备好
            setTimeout(restoreScroll, 600);
        } else {
            console.log('⚠️ 无法恢复滚动位置:', {
                savedScrollTop,
                dataLength,
                reason: !savedScrollTop ? '没有保存的位置' : (dataLength === 0 ? '数据未加载' : '未知原因')
            });
        }
    },
    


    // 图片加载成功
    onImageLoad: function(e) {
        console.log('图片加载成功');
    },

    // 图片加载失败
    onImageError: function(e) {
        console.log('图片加载失败:', e.detail);
        // 可以在这里设置默认图片
    },

    // 时间格式化工具函数
    formatTime: function(timeStr) {
        if (!timeStr) return '刚刚';
        
        try {
            const publishTime = new Date(timeStr);
            const now = new Date();
            const diffMs = now - publishTime;
            const diffMins = Math.floor(diffMs / (1000 * 60));
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

            if (diffMins < 1) {
                return '刚刚';
            } else if (diffMins < 60) {
                return `${diffMins}分钟前`;
            } else if (diffHours < 24) {
                return `${diffHours}小时前`;
            } else if (diffDays < 30) {
                return `${diffDays}天前`;
            } else {
                return publishTime.toLocaleDateString();
            }
        } catch (e) {
            return '刚刚';
        }
    }
});
