<template>
  <div class="document-list-container">
    <h2>文档管理</h2>
    
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
          <a-space>
            <a-button type="link" @click="handlePreview(record)">预览</a-button>
            <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getFileList, type FileItem } from '../api/knowledge'
import type { TablePaginationConfig } from 'ant-design-vue'

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
    width: 180,
  }
]

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

const handlePreview = (record: FileItem) => {
  // TODO: 实现文件预览功能
  message.info('文件预览功能开发中')
}

const handleDelete = (record: FileItem) => {
  // TODO: 实现文件删除功能
  message.info('文件删除功能开发中')
}

onMounted(() => {
  fetchFileList()
})
</script>

<style scoped>
.document-list-container {
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 24px;
}
</style>