<template>
  <a-layout class="layout">
    <template v-if="!isBaseDemo">
      <a-layout-sider width="200" style="background: #fff">
        <a-menu
          mode="inline"
          :model-value="selectedKeys"
          @update:model-value="selectedKeys = $event"
          :style="{ height: '100%', borderRight: 0 }"
          @select="handleMenuSelect"
        >
          <a-menu-item key="assistant">
            <template #icon>
              <robot-outlined />
            </template>
            <span>美业助手</span>
          </a-menu-item>
          <a-menu-item key="knowledge">
            <template #icon>
              <folder-outlined />
            </template>
            <span>本地知识库</span>
          </a-menu-item>
          <a-menu-item key="analytics">
            <template #icon>
              <line-chart-outlined />
            </template>
            <span>数据分析</span>
          </a-menu-item>
        </a-menu>
      </a-layout-sider>
    </template>
    <a-layout-content :style="contentStyle">
      <router-view></router-view>
    </a-layout-content>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  RobotOutlined, 
  FolderOutlined, 
  LineChartOutlined 
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const selectedKeys = ref<string[]>(['assistant'])

const isBaseDemo = computed(() => route.name === 'base-demo')

const contentStyle = computed(() => ({
  padding: '24px',
  minHeight: '280px',
  margin: isBaseDemo.value ? '0' : '24px'
}))

const handleMenuSelect = ({ key }: { key: string }) => {
  router.push(`/${key}`)
}
</script>

<style>
.layout {
  min-height: 100vh;
}
</style>
