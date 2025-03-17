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
          style="width: calc(100% - 100px)"
        />
        <a-button 
          type="primary" 
          :loading="loading"
          @click="sendMessage"
        >
          发送
        </a-button>
      </a-input-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import { chatWithAssistant } from '@/api/assistant'

const inputMessage = ref('')
const loading = ref(false)
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