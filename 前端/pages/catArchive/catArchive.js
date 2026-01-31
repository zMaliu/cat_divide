const config = require('../../utils/config.js');

Page({
  data: {
    userToken: '',
    userId: null,
    cats: [],
    filteredCats: [], // 过滤后的猫咪列表
    searchKeyword: '', // 搜索关键词
    isLoading: false,
    isSubmitting: false,
    showForm: false,
    formMode: 'create',
    genderOptions: ['公', '母', '未知'],
    genderIndex: 2,
    imageUploaded: false, // 标记图片是否已上传
    tempImagePath: '', // 临时图片路径
    // 这个表单是这个页面data中的一部分数据，表单原本是这样的，将后端返回来的信息加进去，用setdata函数来设置状态，存储到当前页面
    form: {
      id: null,
      name: '',
      breed: '',
      age: '',
      gender: 'unknown',
      description: '',
      image_url: ''
    }
  },

  onLoad() {
    const token = wx.getStorageSync('token');
    const userId = wx.getStorageSync('user_id');
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再管理猫咪档案',
        showCancel: false,
        success: () => {
          wx.switchTab({ url: '/pages/mine/mine' });
        }
      });
      return;
    }
    this.setData({ 
      userToken: token,
      userId: userId ? parseInt(userId) : null
    });
    this.fetchCats();
  },

  // 获取猫咪列表
  fetchCats() {
    const { userToken } = this.data;
    if (!userToken) return;

    this.setData({ isLoading: true });
    wx.request({
      url: `${config.apiURL}/cat/list`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${userToken}`
      },
      success: (res) => {
        if (res.data.code === 200) {
          const { userId } = this.data;
          const cats = (res.data.data.cats || []).map(cat => {
            // 处理图片路径
            let displayImage = '';
            if (cat.image_url) {
              if (cat.image_url.startsWith('http')) {
                displayImage = cat.image_url;
              } else if (cat.image_url.startsWith('/')) {
                displayImage = `${config.baseURL}${cat.image_url}`;
              } else if (cat.image_url.startsWith('wxfile://') || cat.image_url.startsWith('http://tmp/')) {
                // 临时文件路径，直接使用
                displayImage = cat.image_url;
              } else {
                displayImage = `${config.baseURL}/uploads/${cat.image_url}`;
              }
            }
            
            // 如果没有图片URL，使用默认图片
            if (!displayImage) {
              displayImage = `${config.baseURL}/default.jpg`;
            }
            
            return {
              ...cat,
              displayImage: displayImage,
              genderLabel: cat.gender === 'male' ? '公' : (cat.gender === 'female' ? '母' : '未知'),
              isOwner: userId && cat.owner_id === userId // 标记是否为当前用户创建
            };
          });
          this.setData({ 
            cats: cats,
            filteredCats: cats // 初始时显示所有
          });
          // 如果有搜索关键词，应用过滤
          if (this.data.searchKeyword) {
            this.filterCats(this.data.searchKeyword);
          }
        } else {
          wx.showToast({
            title: res.data.msg || '获取失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none'
        });
      },
      complete: () => {
        this.setData({ isLoading: false });
      }
    });
  },

  // 打开新增
  openCreate() {
    this.setData({
      formMode: 'create',
      showForm: true,
      genderIndex: 2,
      imageUploaded: false,
      tempImagePath: '',
      form: {
        id: null,
        name: '',
        breed: '',
        age: '',
        gender: 'unknown',
        description: '',
        image_url: ''
      }
    });
  },

  // 打开编辑
  openEdit(e) {
    const { index } = e.currentTarget.dataset;
    const cat = this.data.filteredCats[index];
    if (!cat) return;

    this.setData({
      formMode: 'edit',
      showForm: true,
      genderIndex: this.getGenderIndex(cat.gender),
      form: {
        id: cat.cat_id,
        name: cat.name || '',
        breed: cat.breed || '',
        age: cat.age !== null && cat.age !== undefined ? cat.age : '',
        gender: cat.gender || 'unknown',
        description: cat.description || '',
        image_url: cat.image_url || ''
      }
    });
  },

  // 关闭表单
  closeForm() {
    if (this.data.isSubmitting) return;
    this.setData({ showForm: false });
  },

  // 输入变更
  onInputChange(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({
      [`form.${field}`]: value
    });
  },

  // 性别选择
  onGenderChange(e) {
    const genderMap = ['male', 'female', 'unknown'];
    const idx = Number(e.detail.value);
    this.setData({
      genderIndex: idx,
      'form.gender': genderMap[idx]
    });
  },

  getGenderIndex(gender) {
    if (gender === 'male') return 0;
    if (gender === 'female') return 1;
    return 2;
  },

  // 提交新增/更新
  submitForm() {
    const { formMode, form, userToken, tempImagePath, imageUploaded } = this.data;
    if (!form.name || !form.name.trim()) {
      wx.showToast({ title: '请填写名字', icon: 'none' });
      return;
    }

    // 如果有临时图片且未上传，先上传图片
    let imageUrl = form.image_url ? form.image_url.trim() : '';
    const isTempPath = imageUrl && (imageUrl.startsWith('wxfile://') || imageUrl.startsWith('http://tmp/') || imageUrl.startsWith('tmp/'));
    
    if (isTempPath && tempImagePath) {
      // 临时文件，需要先上传
      this.uploadImageBeforeSubmit(tempImagePath, () => {
        // 上传成功后重新提交
        this.submitForm();
      });
      return;
    }

    // 如果图片是临时路径但没有 tempImagePath，说明上传可能失败了
    if (isTempPath) {
      wx.showToast({
        title: '图片上传失败，请重新选择图片',
        icon: 'none'
      });
      return;
    }

    // 构建 payload，年龄为空时不包含该字段
    const payload = {
      cat_name: form.name.trim(),
      cat_breed: form.breed ? form.breed.trim() : '',
      cat_gender: form.gender || 'unknown',
      cat_description: form.description ? form.description.trim() : '',
      cat_image_url: imageUrl
    };

    // 只有当年龄不为空时才添加 cat_age 字段
    if (form.age !== '' && form.age !== null && form.age !== undefined) {
      const ageValue = Number(form.age);
      if (isNaN(ageValue) || ageValue < 0) {
        wx.showToast({ title: '年龄需为非负数字', icon: 'none' });
        return;
      }
      payload.cat_age = ageValue;
    }

    const url = formMode === 'create'
      ? `${config.apiURL}/cat/create`
      : `${config.apiURL}/cat/${form.id}`;
    const method = formMode === 'create' ? 'POST' : 'PUT';

    this.setData({ isSubmitting: true });
    wx.request({
      url,
      method,
      data: payload,
      header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken}`
      },
      success: (res) => {
        if (res.data.code === 200) {
          wx.showToast({
            title: formMode === 'create' ? '创建成功' : '更新成功',
            icon: 'success'
          });
          this.setData({ showForm: false });
          this.fetchCats();
        } else {
          wx.showToast({
            title: res.data.msg || '操作失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请稍后再试',
          icon: 'none'
        });
      },
      complete: () => {
        this.setData({ isSubmitting: false });
      }
    });
  },

  // 删除
  confirmDelete(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认删除',
      content: '删除后不可恢复，确定删除吗？',
      success: (res) => {
        if (res.confirm) {
          this.deleteCat(id);
        }
      }
    });
  },

  deleteCat(catId) {
    const { userToken } = this.data;
    if (!userToken) return;
    wx.request({
      url: `${config.apiURL}/cat/${catId}`,
      method: 'DELETE',
      header: {
        'Authorization': `Bearer ${userToken}`
      },
      success: (res) => {
        if (res.data.code === 200) {
          wx.showToast({ title: '删除成功', icon: 'success' });
          this.fetchCats();
        } else {
          wx.showToast({
            title: res.data.msg || '删除失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请稍后再试',
          icon: 'none'
        });
      }
    });
  },

  // 搜索功能
  onSearchInput(e) {
    const keyword = e.detail.value.trim();
    this.setData({ searchKeyword: keyword });
    this.filterCats(keyword);
  },

  // 过滤猫咪列表
  filterCats(keyword) {
    const { cats } = this.data;
    if (!keyword) {
      this.setData({ filteredCats: cats });
      return;
    }
    
    const filtered = cats.filter(cat => {
      // 根据品种搜索（不区分大小写）
      const breed = (cat.breed || '').toLowerCase();
      const searchLower = keyword.toLowerCase();
      return breed.includes(searchLower);
    });
    
    this.setData({ filteredCats: filtered });
  },

  // 清空搜索
  clearSearch() {
    this.setData({ 
      searchKeyword: '',
      filteredCats: this.data.cats
    });
  },

  // 选择图片
  chooseImage() {
    const { userToken } = this.data;
    if (!userToken) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }

    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0];
        this.uploadImage(tempFilePath);
      },
      fail: (err) => {
        console.error('选择图片失败:', err);
        wx.showToast({
          title: '选择图片失败',
          icon: 'none'
        });
      }
    });
  },

  // 上传图片
  uploadImage(filePath) {
    const { userToken } = this.data;
    wx.showLoading({
      title: '上传中...',
      mask: true
    });

    // 先显示临时图片并保存临时路径
    this.setData({
      'form.image_url': filePath,
      tempImagePath: filePath,
      imageUploaded: false
    });

    // 第一步：先上传原图片到 cat/upload-image 接口
    wx.uploadFile({
      url: `${config.apiURL}/cat/upload-image`,
      filePath: filePath,
      name: 'image',
      header: {
        'Authorization': `Bearer ${userToken}`
      },
      success: (uploadRes) => {
        try {
          const uploadResult = JSON.parse(uploadRes.data);
          if (uploadResult.code === 200 && uploadResult.data && uploadResult.data.image_url) {
            // 原图片上传成功，获取原图片URL
            let originalImageUrl = uploadResult.data.image_url;
            if (!originalImageUrl.startsWith('http')) {
              if (originalImageUrl.startsWith('/')) {
                originalImageUrl = `${config.baseURL}${originalImageUrl}`;
              } else {
                originalImageUrl = `${config.baseURL}/${originalImageUrl}`;
              }
            }

            // 第二步：调用 yolo 接口进行识别（获取品种信息）
            wx.uploadFile({
              url: `${config.apiURL}/yolo/detect-cat`,
              filePath: filePath,
              name: 'image',
              header: {
                'Authorization': `Bearer ${userToken}`
              },
              success: (detectRes) => {
                wx.hideLoading();
                try {
                  const detectResult = JSON.parse(detectRes.data);
                  
                  // 处理品种识别结果
                  let detectedBreed = '';
                  if (detectResult.code === 200 && detectResult.data && detectResult.data.detections && detectResult.data.detections.length > 0) {
                    // 找到置信度最高的检测结果
                    let maxConfidence = 0;
                    let bestDetection = null;
                    
                    for (let detection of detectResult.data.detections) {
                      if (detection.confidence > maxConfidence) {
                        maxConfidence = detection.confidence;
                        bestDetection = detection;
                      }
                    }
                    
                    // 如果检测到品种（class 不是 'cat'），使用它
                    if (bestDetection && bestDetection.class && bestDetection.class !== 'cat') {
                      // 将品种名称转换为中文友好的格式
                      detectedBreed = this.formatBreedName(bestDetection.class);
                    }
                  }
                  
                  // 更新表单数据，使用原图片URL
                  const updateData = {
                    'form.image_url': originalImageUrl,
                    imageUploaded: true,
                    tempImagePath: '' // 清空临时路径
                  };
                  
                  // 如果识别到品种且品种字段为空，自动填充
                  if (detectedBreed && !this.data.form.breed) {
                    updateData['form.breed'] = detectedBreed;
                  }
                  
                  this.setData(updateData);
                  
                  if (detectedBreed) {
                    wx.showToast({
                      title: `上传成功，已识别品种：${detectedBreed}`,
                      icon: 'success',
                      duration: 2000
                    });
                  } else {
                    wx.showToast({
                      title: '上传成功',
                      icon: 'success'
                    });
                  }
                } catch (e) {
                  console.error('解析识别结果失败:', e);
                  // 即使识别失败，也使用原图片
                  this.setData({
                    'form.image_url': originalImageUrl,
                    imageUploaded: true,
                    tempImagePath: ''
                  });
                  wx.showToast({
                    title: '上传成功',
                    icon: 'success'
                  });
                }
              },
              fail: (detectErr) => {
                wx.hideLoading();
                console.error('识别失败:', detectErr);
                // 即使识别失败，也使用原图片
                this.setData({
                  'form.image_url': originalImageUrl,
                  imageUploaded: true,
                  tempImagePath: ''
                });
                wx.showToast({
                  title: '上传成功（识别失败）',
                  icon: 'success',
                  duration: 2000
                });
              }
            });
          } else {
            wx.hideLoading();
            // 原图片上传失败
            this.setData({
              imageUploaded: false
            });
            wx.showToast({
              title: uploadResult.msg || '上传失败，请重试',
              icon: 'none',
              duration: 2000
            });
          }
        } catch (e) {
          wx.hideLoading();
          console.error('解析上传结果失败:', e);
          this.setData({
            imageUploaded: false
          });
          wx.showToast({
            title: '上传失败，请重试',
            icon: 'none',
            duration: 2000
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('上传失败:', err);
        this.setData({
          imageUploaded: false
        });
        wx.showToast({
          title: '上传失败，请重试',
          icon: 'none',
          duration: 2000
        });
      }
    });
  },

  // 提交前上传图片
  uploadImageBeforeSubmit(filePath, callback) {
    const { userToken } = this.data;
    wx.showLoading({
      title: '上传图片中...',
      mask: true
    });

    // 先上传原图片到 cat/upload-image 接口
    wx.uploadFile({
      url: `${config.apiURL}/cat/upload-image`,
      filePath: filePath,
      name: 'image',
      header: {
        'Authorization': `Bearer ${userToken}`
      },
      success: (uploadRes) => {
        wx.hideLoading();
        try {
          const uploadResult = JSON.parse(uploadRes.data);
          if (uploadResult.code === 200 && uploadResult.data && uploadResult.data.image_url) {
            // 原图片上传成功，获取原图片URL
            let originalImageUrl = uploadResult.data.image_url;
            if (!originalImageUrl.startsWith('http')) {
              if (originalImageUrl.startsWith('/')) {
                originalImageUrl = `${config.baseURL}${originalImageUrl}`;
              } else {
                originalImageUrl = `${config.baseURL}/${originalImageUrl}`;
              }
            }
            
            // 更新表单数据，使用原图片URL
            this.setData({
              'form.image_url': originalImageUrl,
              imageUploaded: true,
              tempImagePath: ''
            });
            
            // 上传成功后执行回调
            if (callback) callback();
          } else {
            // 上传失败
            this.setData({
              'form.image_url': '',
              imageUploaded: true,
              tempImagePath: ''
            });
            wx.showToast({
              title: uploadResult.msg || '图片上传失败',
              icon: 'none',
              duration: 2000
            });
            setTimeout(() => {
              if (callback) callback();
            }, 500);
          }
        } catch (e) {
          wx.hideLoading();
          console.error('解析上传结果失败:', e);
          this.setData({
            'form.image_url': '',
            imageUploaded: true,
            tempImagePath: ''
          });
          wx.showToast({
            title: '图片上传失败',
            icon: 'none',
            duration: 2000
          });
          setTimeout(() => {
            if (callback) callback();
          }, 500);
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('上传失败:', err);
        this.setData({
          'form.image_url': '',
          imageUploaded: true,
          tempImagePath: ''
        });
        wx.showToast({
          title: '图片上传失败',
          icon: 'none',
          duration: 2000
        });
        setTimeout(() => {
          if (callback) callback();
        }, 500);
      }
    });
  },

  // 移除图片
  removeImage() {
    this.setData({
      'form.image_url': '',
      tempImagePath: '',
      imageUploaded: false
    });
  },

  // 图片加载错误处理
  onImageError(e) {
    console.error('图片加载失败:', e);
    // 如果图片加载失败，使用默认图片
    const defaultImage = `${config.baseURL}/default.jpg`;
    this.setData({
      'form.image_url': defaultImage
    });
  },

  // 卡片图片加载错误处理
  onCardImageError(e) {
    const { index } = e.currentTarget.dataset;
    const defaultImage = `${config.baseURL}/default.jpg`;
    const cats = this.data.filteredCats;
    if (cats[index]) {
      cats[index].displayImage = defaultImage;
      this.setData({
        filteredCats: cats
      });
    }
  },

  // 格式化品种名称（将英文品种名转换为中文友好的格式）
  formatBreedName(breedName) {
    // 品种名称映射表
    const breedMap = {
      'Abyssinian': '阿比西尼亚',
      'Bengal': '孟加拉',
      'Birman': '伯曼',
      'Bombay': '孟买',
      'British_Shorthair': '英短',
      'Egyptian_Mau': '埃及猫',
      'Maine_Coon': '缅因',
      'Persian': '波斯',
      'Ragdoll': '布偶',
      'Russian_Blue': '俄罗斯蓝猫',
      'Siamese': '暹罗',
      'Sphynx': '斯芬克斯'
    };
    
    // 如果找到映射，返回中文名；否则返回原名称（去掉下划线，添加空格）
    if (breedMap[breedName]) {
      return breedMap[breedName];
    } else {
      // 将下划线替换为空格，并首字母大写
      return breedName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  }
});

