<template>
  <div class="base-demo">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="logo">DeepSeek政务平台</div>
      <div class="nav-items">
        <span class="menu-item">首页</span>
        <span class="menu-item">政务服务</span>
        <span class="menu-item">城市治理</span>
        <span class="menu-item">数据分析</span>
      </div>
    </nav>

    <div class="container">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div 
          v-for="item in menuItems" 
          :key="item.key"
          :class="['menu-item', { active: activeMenu === item.key }]"
          @click="activeMenu = item.key"
        >
          {{ item.label }}
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="content">
        <!-- 智能客服模块 -->
        <div class="card">
          <h3 class="card-title">政务智能助手</h3>
          <div class="chat-box" ref="chatContainer">
            <!-- 用户问题 -->
            <div v-if="searchQuery" class="user-msg">
              <div class="response-content">{{ searchQuery }}</div>
            </div>
            <!-- AI回答 -->
            <div v-if="aiResponse" class="bot-msg">
              <div class="response-content">{{ aiResponse }}</div>
            </div>
            <!-- 搜索结果 -->
            <div v-if="searchResults.length > 0" class="reference-docs">
              <div class="reference-title">参考文档：</div>
              <div class="reference-list">
                <span v-for="(result, index) in searchResults" :key="index" class="reference-item">
                  {{ result.filename }}{{ index < searchResults.length - 1 ? '、' : '' }}
                </span>
              </div>
            </div>
            <div v-if="!aiResponse && !searchResults.length" class="bot-msg">您好！请问需要办理什么业务？</div>
          </div>
          <div class="input-group">
            <a-input-search
              v-model:value="searchQuery"
              placeholder="输入您的问题..."
              :loading="searching"
              @pressEnter="handleSearch"
              :disabled="isListening"
            >
              <template #enterButton>
                <a-button type="primary" :loading="searching" @click="handleSearch">
                  搜索
                </a-button>
              </template>
            </a-input-search>
            <a-button
              :type="isListening ? 'primary' : 'default'"
              :danger="isListening"
              @click="handleVoiceInput"
              class="voice-btn"
            >
              <template #icon><audio-outlined /></template>
              {{ isListening ? '停止' : '语音' }}
            </a-button>
          </div>
          
          <!-- 搜索历史 -->
          <div v-if="searchHistory.length > 0" class="search-history">
            <span class="history-label">搜索历史：</span>
            <a-tag 
              v-for="(item, index) in searchHistory" 
              :key="index"
              class="history-tag"
              @click="searchQuery = item"
            >
              {{ item }}
            </a-tag>
          </div>
        </div>

        <!-- 智能材料审核模块 -->
        <div class="card">
          <h3 class="card-title">智能材料审核</h3>
          <a-upload
            :customRequest="handleUpload"
            :showUploadList="false"
            accept=".pdf,.doc,.docx"
          >
            <div class="upload-zone">
              <upload-outlined />
              <p>拖拽文件或点击上传（支持PDF/Word文档）</p>
            </div>
          </a-upload>
          <a-progress
            v-if="uploadProgress > 0 && uploadProgress < 100"
            :percent="uploadProgress"
            size="small"
            status="active"
          />
          <!-- 文件列表 -->
          <div class="file-list" v-if="fileList.length > 0">
            <h4>已上传文件</h4>
            <a-list :data-source="fileList" :bordered="true">
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta
                    :title="item.filename"
                    :description="formatFileSize(item.size)"
                  >
                    <template #avatar>
                      <file-outlined />
                    </template>
                  </a-list-item-meta>
                  <div>{{ item.upload_time }}</div>
                </a-list-item>
              </template>
            </a-list>
          </div>
        </div>

        <!-- 数据可视化模块 -->
        <div class="card">
          <h3 class="card-title">民生问题分析</h3>
          <div ref="chartRef" style="height: 300px"></div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import { UploadOutlined, FileOutlined, AudioOutlined } from '@ant-design/icons-vue'
import * as echarts from 'echarts'
import { uploadFile, searchDocuments, getFileList, type FileItem } from '../api/knowledge'
// 引入百度语音识别SDK
// 需要先安装依赖: npm install baidu-aip-sdk --save
// 删除以下导入
// @ts-ignore
// import * as AipSpeech from 'baidu-aip-sdk'

// 添加 SpeechRecognition 类型声明
interface SpeechRecognitionEvent extends Event {
  results: {
    item(index: number): {
      item(index: number): {
        transcript: string;
        confidence: number;
      };
    };
    [index: number]: {
      [index: number]: {
        transcript: string;
        confidence: number;
      };
    };
  };
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
}

interface SpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

interface Window {
  SpeechRecognition: new () => SpeechRecognition;
  webkitSpeechRecognition: new () => SpeechRecognition;
}

// 状态定义
const activeMenu = ref('assistant')
const searchQuery = ref('')
const searching = ref(false)
const aiResponse = ref('')
const searchResults = ref<any[]>([])
const uploadProgress = ref(0)
const fileList = ref<FileItem[]>([])
const isListening = ref(false)
const tempText = ref('')
const searchHistory = ref<string[]>([])

// 菜单项
const menuItems = [
  { key: 'assistant', label: '智能客服' },
  { key: 'review', label: '材料审核' },
  { key: 'monitor', label: '舆情监控' },
  { key: 'emergency', label: '应急管理' },
  { key: 'dashboard', label: '数据看板' }
]

// 文件上传处理
const handleUpload = async (options: any) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    
    uploadProgress.value = 0
    const onProgress = (progressEvent: any) => {
      const percent = Math.floor((progressEvent.loaded / progressEvent.total) * 100)
      uploadProgress.value = percent
    }

    await uploadFile(formData, onProgress)
    message.success('文件上传成功')
    options.onSuccess()
    uploadProgress.value = 0
    await fetchFileList()
  } catch (error) {
    message.error('文件上传失败')
    options.onError()
    uploadProgress.value = 0
  }
}

// 百度语音识别服务
class BaiduSpeechService {
  isListening: boolean = false;
  private recorder: any = null;
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private audioData: Blob[] = [];
  private timeoutId: number | null = null;
  
  constructor() {
    // 不再需要创建客户端
  }
  
  async start(onResult: (text: string) => void, onError: (error: string) => void) {
    if (this.isListening) return;
    
    try {
      // 检查是否支持 getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('浏览器不支持音频输入');
      }

      this.isListening = true;
      this.audioData = [];
      
      // 请求麦克风权限
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      // 创建MediaRecorder
      this.recorder = new MediaRecorder(this.mediaStream);
      
      // 收集音频数据
      this.recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioData.push(event.data);
        }
      };
      
      // 录音结束时处理
      this.recorder.onstop = async () => {
        if (this.audioData.length === 0) {
          onError('no-speech');
          return;
        }
        
        try {
          // 将音频数据转换为文件
          const audioBlob = new Blob(this.audioData, { type: 'audio/wav' });
          
          // 创建FormData对象
          const formData = new FormData();
          formData.append('audio', audioBlob);
          
          // 修改请求配置
          const response = await fetch('/api/speech/speech-to-text', {
            method: 'POST',
            body: formData,
            credentials: 'include'  // 添加凭证支持
          });
          
          if (!response.ok) {
            throw new Error('语音识别请求失败');
          }
          
          const result = await response.json();
          
          if (result && result.text) {
            onResult(result.text);
          } else {
            onError('no-speech');
          }
        } catch (error) {
          console.error('语音识别失败:', error);
          onError('network');
        }
      };
      
      // 开始录音
      this.recorder.start();
      
      // 设置30秒超时
      this.timeoutId = window.setTimeout(() => {
        this.stop();
      }, 30000);
      
      message.success('开始录音，请说话...');
    } catch (error: any) {
      console.error('录音失败:', error);
      this.isListening = false;
      if (error.name === 'NotAllowedError') {
        onError('not-allowed');
      } else if (error.name === 'NotFoundError') {
        onError('device-not-found');
      } else {
        onError('initialization-error');
      }
    }
  }
  
  stop() {
    if (!this.isListening) return;
    
    this.isListening = false;
    
    if (this.recorder && this.recorder.state !== 'inactive') {
      this.recorder.stop();
    }
    
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
  }
}

// 替换原有的语音服务
// const speechService = new SpeechRecognitionService();
const speechService = new BaiduSpeechService();

// 处理语音识别
const handleVoiceInput = () => {
  if (isListening.value) {
    speechService.stop();
    isListening.value = false;
    return;
  }
  
  isListening.value = true;
  speechService.start(
    (text) => {
      searchQuery.value = text;
      tempText.value = text;
      isListening.value = false;
      
      // 添加到搜索历史
      if (!searchHistory.value.includes(text)) {
        searchHistory.value.unshift(text);
        if (searchHistory.value.length > 3) {
          searchHistory.value.pop();
        }
      }
    },
    (error) => {
      if (error === 'timeout') {
        message.warning('语音识别超时，请重试');
      } else {
        handleSpeechError(error);
      }
      isListening.value = false;
    }
  );
};

// 搜索处理
const handleSearch = async () => {
  console.log('搜索内容:', searchQuery.value)
  
  if (!searchQuery.value?.trim()) {
    message.warning('请输入问题')
    return
  }
  
  searching.value = true
  try {
    const response = await searchDocuments(searchQuery.value)
    console.log('搜索响应:', response)
    
    if (response.search_results && response.search_results.length > 0) {
      searchResults.value = response.search_results
      // 过滤掉 <think> 标签内容
      const filteredResponse = response.ai_response?.replace(/<think>[\s\S]*?<\/think>/g, '').trim()
      aiResponse.value = filteredResponse || '抱歉，我暂时无法生成回答。'
      
      await nextTick()
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    } else {
      message.info('未找到相关文档')
      searchResults.value = []
      aiResponse.value = ''
    }
  } catch (error) {
    console.error('搜索失败:', error)
    message.error('搜索失败，请稍后重试')
    searchResults.value = []
    aiResponse.value = ''
  } finally {
    searching.value = false
  }
}

// 获取文件列表
const fetchFileList = async () => {
  try {
    const response = await getFileList()
    if (response) {
      fileList.value = response.items
    }
  } catch (error) {
    message.error('获取文件列表失败')
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 图表相关
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: {},
      xAxis: { data: ['教育', '医疗', '交通', '住房', '环境'] },
      yAxis: {},
      series: [{
        type: 'bar',
        data: [234, 189, 310, 278, 154]
      }]
    })
  }
}

// 错误处理
const handleSpeechError = (error: string) => {
  switch (error) {
    case 'not-allowed':
      message.error('请允许使用麦克风权限');
      break;
    case 'device-not-found':
      message.error('未找到麦克风设备');
      break;
    case 'initialization-error':
      message.error('录音初始化失败，请检查浏览器设置');
      break;
    case 'network':
      message.error('网络连接异常');
      break;
    case 'timeout':
      message.warning('语音识别超时');
      break;
    default:
      message.error('语音识别出现错误，请重试');
  }
  isListening.value = false;
};

// 生命周期钩子
onMounted(async () => {
  await fetchFileList()
  await nextTick()
  initChart()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

// 添加聊天容器引用
const chatContainer = ref<HTMLElement>()
</script>

<style scoped>
/* 基础样式 */
.base-demo {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 导航栏 */
.navbar {
  background: #1a2b5c;
  color: white;
  padding: 1rem;
  display: flex;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  margin-right: 2rem;
}

.nav-items .menu-item {
  margin: 0 1rem;
  cursor: pointer;
}

/* 主布局 */
.container {
  display: grid;
  grid-template-columns: 250px 1fr;
  min-height: calc(100vh - 64px);
}

/* 侧边栏 */
.sidebar {
  background: white;
  padding: 1rem;
  border-right: 1px solid #ddd;
}

.menu-item {
  padding: 0.8rem;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.menu-item:hover {
  background: #f0f4ff;
}

.menu-item.active {
  background: #1a2b5c;
  color: white;
}

/* 内容区 */
.content {
  padding: 2rem;
  display: grid;
  gap: 2rem;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-title {
  color: #1a2b5c;
  margin-bottom: 1rem;
}

/* 聊天框样式 */
.chat-box {
  height: 500px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  overflow-y: auto;
  background: #fff;
  margin-bottom: 1rem;
}

.user-msg {
  margin: 1rem 0;
  padding: 1rem;
  background: #e6f7ff;
  border-radius: 12px;
  max-width: 90%;
  margin-left: auto;
}

.bot-msg {
  margin: 1rem 0;
  padding: 1rem;
  background: #f0f4ff;
  border-radius: 12px;
  max-width: 90%;
}

.response-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

/* 上传区域样式 */
.upload-zone {
  border: 2px dashed #ddd;
  padding: 2rem;
  text-align: center;
  border-radius: 8px;
  cursor: pointer;
}

.upload-zone:hover {
  border-color: #1a2b5c;
}

/* 搜索结果样式 */
.reference-docs {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #666;
}

.reference-title {
  margin-bottom: 0.3rem;
  font-weight: bold;
}

.reference-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.reference-item {
  color: #1a2b5c;
}

/* 文件列表样式 */
.file-list {
  margin-top: 1rem;
}

/* 输入框组样式 */
.input-group {
  margin-top: 1rem;
  display: flex;
  gap: 8px;
}

.input-group :deep(.ant-input-search) {
  flex: 1;
}

.voice-btn {
  min-width: 80px;
}

/* 搜索历史样式 */
.search-history {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.history-label {
  color: #666;
}

.history-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.history-tag:hover {
  background: #e6f7ff;
  border-color: #1890ff;
}
</style>