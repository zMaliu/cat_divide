const config = {
  development: {
    baseURL: 'http://localhost:5001',
    apiURL: 'http://localhost:5001/api'
  },
  production: {
    baseURL: 'https://your-domain.com',
    apiURL: 'https://your-domain.com/api'
  }
}

const currentEnv = 'development'

module.exports = {
  baseURL: config[currentEnv].baseURL,
  apiURL: config[currentEnv].apiURL,
  env: currentEnv
}