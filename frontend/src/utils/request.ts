import axios from 'axios'
import { message } from 'ant-design-vue'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api', // 使用代理路径
  timeout: 60000,
  withCredentials: true
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 添加自定义请求头
    config.headers['X-Requested-With'] = 'XMLHttpRequest'
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