// 环境配置
const config = {
    // 开发环境
    development: {
      baseURL: 'http://localhost:5001',
      apiURL: 'http://localhost:5001/api'
    },
    // 生产环境 - HTTPS（正式版必须用HTTPS）
    production: {
      baseURL: 'https://yunhumeng.cn',     
      apiURL: 'https://yunhumeng.cn/api'    
    }
  }
  
  // 当前环境 
  const currentEnv = 'development'
  
  // 导出当前环境配置（这部分不用改）
  module.exports = {
    baseURL: config[currentEnv].baseURL,
    apiURL: config[currentEnv].apiURL,
    env: currentEnv
  }