// 环境配置
const config = {
  // 开发环境
  development: {
    baseURL: 'http://localhost:5001',
    apiURL: 'http://localhost:5001/api'
  },
  // 生产环境 - 请替换为您的实际服务器地址
  production: {
    baseURL: 'https://your-domain.com',
    apiURL: 'https://your-domain.com/api'
  }
}

// 当前环境 - 上线前改为 'production'
const currentEnv = 'development'

// 导出当前环境配置
module.exports = {
  baseURL: config[currentEnv].baseURL,
  apiURL: config[currentEnv].apiURL,
  env: currentEnv
} 