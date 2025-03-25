import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import App from './App.vue'
// import 'ant-design-vue/dist/antd.css'

// 导入页面组件
import Assistant from './pages/Assistant.vue'
import Knowledge from './pages/Knowledge.vue'
import Analytics from './pages/Analytics.vue'
import BaseDemo from './pages/BaseDemo.vue'
import DocumentList from './pages/DocumentList.vue'

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/assistant'
    },
    {
      path: '/assistant',
      name: 'assistant',
      component: Assistant
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: Knowledge
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: Analytics
    },
    {
      path: '/base-demo',
      name: 'base-demo',
      component: BaseDemo
    },
    {
      path: '/document-list',
      name: 'document-list',
      component: DocumentList
    }
  ]
})

// 创建Vue应用实例
const app = createApp(App)

// 使用插件
app.use(router)
app.use(Antd)

// 挂载应用
app.mount('#app')