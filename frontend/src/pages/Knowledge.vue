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

    <div class="search-section">
      <a-input-search
        v-model:value="searchQuery"
        placeholder="请输入搜索内容"
        enter-button
        :loading="searching"
        @search="handleSearch"
        size="large"
      />
    </div>

    <div class="file-list-section">
      <h3>已上传文档</h3>
      <a-table
        :dataSource="fileList"
        :columns="columns"
        :pagination="pagination"
        @change="handleTableChange"
        :loading="loading"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'size'">
            {{ formatFileSize(record.size) }}
          </template>
          <template v-if="column.key === 'action'">
            <a @click="handleSearch(record.filename)">--</a>
          </template>
        </template>
      </a-table>
    </div>

    <div v-if="aiResponse" class="ai-response">
      <h3>AI 回答：</h3>
      <p>{{ aiResponse }}</p>
    </div>

    <div v-if="searchResults && searchResults.length > 0" class="search-results">
      <h3>相关文档：</h3>
      <a-list :data-source="searchResults" :bordered="true">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta
              :title="item.filename"
              :description="item.content.substring(0, 200) + '...'"
            >
              <template #title>
                <span>{{ item.filename }}</span>
                <a-tag color="blue" class="score-tag">
                  相关度: {{ (item.score * 100).toFixed(1) }}%
                </a-tag>
              </template>
            </a-list-item-meta>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <div v-if="hasSearched && (!searchResults || searchResults.length === 0)" class="no-results">
      <a-empty description="未找到相关文档" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import { uploadFile, searchDocuments, getFileList, type FileItem } from '../api/knowledge'
import type { TablePaginationConfig } from 'ant-design-vue'

const searchQuery = ref('')
const searching = ref(false)
const aiResponse = ref('')
const searchResults = ref<any[]>([])
const hasSearched = ref(false)
const uploadProgress = ref(0)
const fileList = ref<FileItem[]>([])
const loading = ref(false)
const pagination = ref<TablePaginationConfig>({
  total: 0,
  current: 1,
  pageSize: 10,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const columns = [
  {
    title: '文件名',
    dataIndex: 'filename',
    key: 'filename',
  },
  {
    title: '类型',
    dataIndex: 'file_type',
    key: 'file_type',
    width: 100,
  },
  {
    title: '大小',
    dataIndex: 'size',
    key: 'size',
    width: 120,
  },
  {
    title: '上传时间',
    dataIndex: 'upload_time',
    key: 'upload_time',
    width: 180,
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
  }
]

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
    await fetchFileList()
  } catch (error) {
    message.error('文件上传失败')
    options.onError()
    uploadProgress.value = 0
  }
}

const handleTableChange = (pag: TablePaginationConfig) => {
  pagination.value.current = pag.current || 1
  pagination.value.pageSize = pag.pageSize || 10
  fetchFileList()
}

const fetchFileList = async () => {
  loading.value = true
  try {
    const { total, items } = await getFileList(
      pagination.value.current,
      pagination.value.pageSize
    )
    fileList.value = items
    pagination.value.total = total
  } catch (error) {
    message.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchFileList()
})

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  searching.value = true
  hasSearched.value = true
  try {
    const response = await searchDocuments(searchQuery.value)
    if (response.ai_response) {
      aiResponse.value = response.ai_response
      searchResults.value = response.search_results || []
    } else {
      aiResponse.value = ''
      searchResults.value = []
      message.info('未找到相关文档')
    }
  } catch (error) {
    message.error('搜索失败')
    aiResponse.value = ''
    searchResults.value = []
  } finally {
    searching.value = false
  }
}
</script>

<style scoped>
.knowledge-container {
  padding: 24px;
}

.upload-section {
  margin-bottom: 24px;
}

.search-section {
  margin-bottom: 24px;
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

.file-list-section {
  margin: 24px 0;
}

.upload-section :deep(.ant-progress) {
  margin-top: 8px;
  width: 200px;
}

.no-results {
  margin-top: 24px;
  text-align: center;
  padding: 24px;
  background: #fafafa;
  border-radius: 4px;
}

.score-tag {
  margin-left: 8px;
}
</style> 