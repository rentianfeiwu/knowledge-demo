import axios from 'axios'
import { message } from 'ant-design-vue'

// Create axios instance
const request = axios.create({
  baseURL: '',  // 移除 /api 前缀，因为已经在 vite 配置中处理了
  timeout: 60000,
  withCredentials: true
})

// 直接在请求拦截器中处理
request.interceptors.request.use(
  config => {
    config.headers['X-Requested-With'] = 'XMLHttpRequest'
    // 在开发环境中禁用 SSL 验证
    if (process.env.NODE_ENV === 'development') {
      config.validateStatus = () => true
    }
    return config
  },
  error => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.code === 'ERR_NETWORK') {
      message.error('网络连接失败，请检查网络设置')
    } else if (error.code === 'ERR_CERT_AUTHORITY_INVALID') {
      message.error('证书验证失败，请确保使用HTTPS访问')
    } else {
      message.error(error.response?.data?.detail || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request