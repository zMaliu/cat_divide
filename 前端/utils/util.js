// utils/util.js

// 兼容iOS的日期字符串转换
function fixDateString(str) {
    // yyyy-MM-dd HH:mm:ss => yyyy/MM/dd HH:mm:ss
    if (typeof str === 'string' && /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(str)) {
      return str.replace(/-/g, '/');
    }
    return str;
  }
  
  // 格式化相对时间（用于消息列表）
  function formatRelativeTime(date) {
    const targetDate = new Date(fixDateString(date));
    const now = new Date();
    const diff = now - targetDate;
  
    if (diff < 60000) {
      return '刚刚';
    }
    if (diff < 3600000) {
      return Math.floor(diff / 60000) + '分钟前';
    }
    if (diff < 86400000) {
      return Math.floor(diff / 3600000) + '小时前';
    }
    if (diff < 604800000) {
      return Math.floor(diff / 86400000) + '天前';
    }
    const year = targetDate.getFullYear();
    const month = (targetDate.getMonth() + 1).toString().padStart(2, '0');
    const day = targetDate.getDate().toString().padStart(2, '0');
    if (year === now.getFullYear()) {
      return `${month}-${day}`;
    } else {
      return `${year}-${month}-${day}`;
    }
  }
  
  // 格式化聊天时间
  function formatChatTime(date) {
    const targetDate = new Date(fixDateString(date));
    const now = new Date();
    if (targetDate.toDateString() === now.toDateString()) {
      const hours = targetDate.getHours().toString().padStart(2, '0');
      const minutes = targetDate.getMinutes().toString().padStart(2, '0');
      return `${hours}:${minutes}`;
    }
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (targetDate.toDateString() === yesterday.toDateString()) {
      const hours = targetDate.getHours().toString().padStart(2, '0');
      const minutes = targetDate.getMinutes().toString().padStart(2, '0');
      return `昨天 ${hours}:${minutes}`;
    }
    const year = targetDate.getFullYear();
    const month = (targetDate.getMonth() + 1).toString().padStart(2, '0');
    const day = targetDate.getDate().toString().padStart(2, '0');
    const hours = targetDate.getHours().toString().padStart(2, '0');
    const minutes = targetDate.getMinutes().toString().padStart(2, '0');
    if (year === now.getFullYear()) {
      return `${month}-${day} ${hours}:${minutes}`;
    } else {
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    }
  }
  
  // 其他工具函数（如有需要）
  function getUserAvatar(userId) {
    return '/assets/default-avatar.png';
  }
  function validatePhone(phone) {
    const phoneReg = /^1[3-9]\d{9}$/;
    return phoneReg.test(phone);
  }
  function validateEmail(email) {
    const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailReg.test(email);
  }
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
  function throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
  
  module.exports = {
    fixDateString,
    formatRelativeTime,
    formatChatTime,
    getUserAvatar,
    validatePhone,
    validateEmail,
    debounce,
    throttle
  };