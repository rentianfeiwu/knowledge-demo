<template>
  <div class="chat-container">
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(msg, index) in messages" :key="index" 
           :class="['message', msg.role]">
        <div class="message-content">
          {{ msg.content }}
        </div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="message-content loading">
          <a-spin />
          <span class="loading-text">AI正在思考中...</span>
        </div>
      </div>
    </div>
    
    <div class="chat-input">
      <a-input-group compact>
        <a-input
          v-model:value="inputMessage"
          placeholder="请输入您的问题..."
          @keyup.enter="sendMessage"
          :disabled="loading"
          style="width: calc(100% - 160px)"
        />
        <a-button 
          type="primary" 
          :loading="loading"
          @click="sendMessage"
        >
          发送
        </a-button>
        <a-button
          type="primary"
          :loading="isRecording"
          @click="toggleRecording"
          style="margin-left: 8px"
        >
          {{ isRecording ? '停止录音' : '语音输入' }}
        </a-button>
      </a-input-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import { chatWithAssistant } from '@/api/assistant'
import { speechToText } from '@/api/speech'

const inputMessage = ref('')
const loading = ref(false)
const isRecording = ref(false)
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])

const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []
    
    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }
    
    mediaRecorder.value.onstop = async () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
      const audioFile = new File([audioBlob], 'recording.wav')
      
      try {
        const response = await speechToText(audioFile)
        inputMessage.value = response.data.text
      } catch (error) {
        message.error('语音识别失败')
      }
    }
    
    mediaRecorder.value.start()
    isRecording.value = true
  } catch (error) {
    message.error('无法访问麦克风')
  }
}

const stopRecording = () => {
  if (mediaRecorder.value) {
    mediaRecorder.value.stop()
    mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
    isRecording.value = false
  }
}
const messages = ref<Array<{role: 'user' | 'assistant', content: string}>>([])
const messagesContainer = ref<HTMLElement>()

const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return
  
  const userMessage = inputMessage.value
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  loading.value = true

  try {
    const response = await chatWithAssistant(userMessage, 
      messages.value.map(m => m.content))
    messages.value.push({ role: 'assistant', content: response.response })
  } catch (error) {
    message.error('发送消息失败')
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: '您好！我是您的美业助手，请问有什么可以帮您？'
  })
})
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 20px;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message-content {
  padding: 12px 16px;
  border-radius: 8px;
  background: #f0f2f5;
}

.message.user .message-content {
  background: #1890ff;
  color: white;
}

.chat-input {
  padding: 20px;
  background: white;
  border-top: 1px solid #f0f0f0;
}

.loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.loading-text {
  color: #666;
  font-size: 14px;
}
</style>