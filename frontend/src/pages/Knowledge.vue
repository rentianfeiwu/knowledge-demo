<template>
  <div class="knowledge-container">
    <div class="upload-section">
      <a-upload
        :customRequest="handleUpload"
        :showUploadList="false"
        accept=".pdf,.doc,.docx"
      >
        <a-button type="primary">
          <upload-outlined />
          上传文档
        </a-button>
      </a-upload>
      <a-progress
        v-if="uploadProgress > 0 && uploadProgress < 100"
        :percent="uploadProgress"
        size="small"
        status="active"
      />
    </div>

    <div class="chat-container">
      <div class="search-section">
        <a-space direction="vertical" style="width: 100%">
          <a-radio-group v-model:value="searchType" size="small">
            <a-radio-button value="hybrid">混合搜索</a-radio-button>
            <a-radio-button value="semantic">语义搜索</a-radio-button>
            <a-radio-button value="fulltext">全文搜索</a-radio-button>
          </a-radio-group>
          <a-input-search
            v-model:value="searchQuery"
            placeholder="请输入您的问题"
            enter-button="询问"
            :loading="searching"
            @search="handleSearch"
            size="large"
          />
        </a-space>
      </div>

      <div class="chat-history">
        <div v-if="aiResponse" class="ai-response">
          <h3>AI 回答：</h3>
          <p>{{ aiResponse }}</p>
        </div>

        <div v-if="searchResults && searchResults.length > 0" class="search-results">
          <h3>参考文档：</h3>
          <a-list :data-source="searchResults" :bordered="true">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <span v-html="item.filename"></span>
                    <a-tag color="blue" class="score-tag">
                      相关度: {{ (item.score).toFixed(1) }}%
                    </a-tag>
                  </template>
                  <template #description>
                    <div v-html="item.content" class="content-preview"></div>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import { uploadFile, searchDocuments } from '../api/knowledge'

const searchQuery = ref('')
const searching = ref(false)
const searchType = ref('hybrid')  // 添加搜索类型状态
const uploadProgress = ref(0)
const searchResults = ref<any[]>([])  // 添加搜索结果状态
const aiResponse = ref('')  // 添加 AI 响应状态

const handleUpload = async (options: any) => {
  try {
    const formData = new FormData()
    formData.append('file', options.file)
    
    const onProgress = (progressEvent: any) => {
      const percent = Math.floor((progressEvent.loaded / progressEvent.total) * 100)
      uploadProgress.value = percent
    }

    await uploadFile(formData, onProgress)
    message.success('文件上传成功')
    options.onSuccess()
    uploadProgress.value = 0
  } catch (error) {
    message.error('文件上传失败')
    options.onError()
    uploadProgress.value = 0
  }
}

const handleSearch = async () => {
  if (!searchQuery.value?.trim()) {
    message.warning('请输入问题')
    return
  }
  
  searching.value = true
  try {
    const response = await searchDocuments(searchQuery.value, searchType.value)
    if (response.search_results && response.search_results.length > 0) {
      searchResults.value = response.search_results
      aiResponse.value = response.ai_response || '抱歉，我暂时无法生成回答。'
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
</script>

<style scoped>
.knowledge-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.upload-section {
  margin-bottom: 24px;
  text-align: right;
}

.chat-container {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-section {
  margin-bottom: 24px;
}

.ant-radio-group {
  margin-bottom: 12px;
}

.chat-history {
  margin-top: 24px;
}

.ai-response {
  margin-bottom: 24px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
}

.search-results {
  margin-top: 24px;
}

.upload-section :deep(.ant-progress) {
  margin-top: 8px;
  width: 200px;
}

.content-preview {
  color: #666;
  font-size: 14px;
}

:deep(.search-highlight) {
  background-color: #ffd54f;
  padding: 0 2px;
  border-radius: 2px;
}

.score-tag {
  margin-left: 8px;
}
</style>