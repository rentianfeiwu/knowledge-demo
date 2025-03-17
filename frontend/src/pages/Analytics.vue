<template>
  <div class="analytics-container">
    <!-- 总体概览卡片 -->
    <a-row :gutter="16" class="overview-cards">
      <a-col :span="6">
        <a-card>
          <template #title>总营收</template>
          <h2>¥{{ formatNumber(overview.total_revenue) }}</h2>
          <div class="card-footer">近{{ days }}天</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <template #title>订单总数</template>
          <h2>{{ formatNumber(overview.total_orders) }}</h2>
          <div class="card-footer">近{{ days }}天</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <template #title>平均客单价</template>
          <h2>¥{{ formatNumber(overview.avg_order_value) }}</h2>
          <div class="card-footer">近{{ days }}天</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <template #title>支付转化率</template>
          <h2>{{ (overview.conversion_rate * 100).toFixed(1) }}%</h2>
          <div class="card-footer">近{{ days }}天</div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 图表区域 -->
    <a-row :gutter="16" class="chart-section">
      <a-col :span="16">
        <a-card title="营收趋势">
          <div ref="trendChartRef" style="height: 300px"></div>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card title="服务类型分布">
          <div ref="pieChartRef" style="height: 300px"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 门店数据表格 -->
    <a-card title="门店业绩排名" class="store-section">
      <a-table
        :columns="storeColumns"
        :data-source="storeData"
        :loading="loading"
        :pagination="false"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a @click="showStoreDetail(record)">详情</a>
          </template>
          <template v-if="column.dataIndex === 'completion_rate'">
            {{ (record.completion_rate * 100).toFixed(1) }}%
          </template>
          <template v-if="column.dataIndex === 'total_revenue'">
            ¥{{ formatNumber(record.total_revenue) }}
          </template>
          <template v-if="column.dataIndex === 'avg_order_value'">
            ¥{{ formatNumber(record.avg_order_value) }}
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 门店详情抽屉 -->
    <a-drawer
      :model-value="drawerVisible"
      @update:model-value="drawerVisible = $event"
      :title="`门店 ${selectedStore?.store_id} 详情`"
      width="800"
      placement="right"
    >
      <div v-if="selectedStore">
        <a-row :gutter="16" class="store-overview">
          <a-col :span="8">
            <a-statistic 
              title="总营收" 
              :value="formatNumber(selectedStore.total_revenue)"
              prefix="¥"
            />
          </a-col>
          <a-col :span="8">
            <a-statistic 
              title="订单数" 
              :value="selectedStore.order_count"
            />
          </a-col>
          <a-col :span="8">
            <a-statistic 
              title="客户数" 
              :value="selectedStore.customer_count"
            />
          </a-col>
        </a-row>
        <div ref="storeServiceChartRef" style="height: 300px; margin-top: 24px"></div>
        <div ref="storeTrendChartRef" style="height: 300px; margin-top: 24px"></div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { 
  getOverview, 
  getStoreAnalytics, 
  getStoreServiceDistribution,
  getStoreDailyTrend,
  getRevenueTrend,
  getServiceDistribution,
  type StoreAnalytics,
  type ServiceDistribution,
  type DailyTrend
} from '../api/analytics'

// 数据状态
const days = ref(30)
const loading = ref(false)
const overview = ref<any>({
  total_revenue: 0,
  total_orders: 0,
  avg_order_value: 0,
  conversion_rate: 0
})
const storeData = ref<any>([])
const drawerVisible = ref(false)
const selectedStore = ref<StoreAnalytics | null>(null)

// 图表实例
let trendChart: echarts.ECharts
let pieChart: echarts.ECharts
let storeServiceChart: echarts.ECharts
let storeTrendChart: echarts.ECharts

// 表格列定义
const storeColumns = [
  {
    title: '门店ID',
    dataIndex: 'store_id',
    key: 'store_id',
  },
  {
    title: '总营收',
    dataIndex: 'total_revenue',
    key: 'total_revenue',
    sorter: (a: StoreAnalytics, b: StoreAnalytics) => a.total_revenue - b.total_revenue,
  },
  {
    title: '订单数',
    dataIndex: 'order_count',
    key: 'order_count',
  },
  {
    title: '平均客单价',
    dataIndex: 'avg_order_value',
    key: 'avg_order_value',
  },
  {
    title: '完成率',
    dataIndex: 'completion_rate',
    key: 'completion_rate',
  },
  {
    title: '客户数',
    dataIndex: 'customer_count',
    key: 'customer_count',
  },
  {
    title: '操作',
    key: 'action',
  },
]

// 数字格式化
const formatNumber = (num: number | null | undefined) => {
  if (num === null || num === undefined) return '0.00'
  return Number(num).toLocaleString('zh-CN', { 
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 获取概览数据和门店数据
    const [overviewResponse, storeAnalyticsResponse] = await Promise.all([
      getOverview(days.value),
      getStoreAnalytics(days.value)
    ])
    
    // 检查并设置数据
    if (overviewResponse) {
      overview.value = overviewResponse
    }
    if (storeAnalyticsResponse) {
      storeData.value = storeAnalyticsResponse
    }
    
    // 更新图表
    await updateCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = async () => {
  if (!trendChart || !pieChart) {
    console.warn('图表实例未初始化，重新初始化...')
    await nextTick()
    initCharts()
  }
  
  try {
    const [trendResponse, serviceResponse] = await Promise.all([
      getRevenueTrend(days.value),
      getServiceDistribution()
    ])
    
    const trendData = trendResponse.data
    const serviceData = serviceResponse.data
    
    if (trendChart && Array.isArray(trendData) && trendData.length > 0) {
      trendChart.setOption({
        tooltip: {
          trigger: 'axis',
          formatter: (params: any) => {
            const data = params[0]
            return `${data.name}<br/>营收：¥${formatNumber(data.value)}`
          }
        },
        xAxis: {
          type: 'category',
          data: trendData.map(item => item.date),
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: (value: number) => `¥${formatNumber(value)}`
          }
        },
        series: [{
          data: trendData.map(item => item.revenue),
          type: 'line',
          smooth: true,
          areaStyle: {
            opacity: 0.3
          }
        }]
      })
    }
    
    if (pieChart && Array.isArray(serviceData) && serviceData.length > 0) {
      pieChart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            return `${params.name}<br/>营收：¥${formatNumber(params.value)}<br/>占比：${params.percent}%`
          }
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center'
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: serviceData.map(item => ({
            name: item.type_name,
            value: item.revenue
          }))
        }]
      })
    }
  } catch (error) {
    console.error('更新图表失败:', error)
  }
}

// 显示门店详情
const showStoreDetail = async (store: StoreAnalytics) => {
  selectedStore.value = store
  drawerVisible.value = true
  
  await nextTick()
  initStoreCharts()
  
  try {
    const [servicesResponse, trendResponse] = await Promise.all([
      getStoreServiceDistribution(store.store_id),
      getStoreDailyTrend(store.store_id, days.value)
    ])
    
    const services = servicesResponse.data
    const trend = trendResponse.data
    
    updateStoreCharts(services, trend)
  } catch (error) {
    console.error('加载门店详情失败:', error)
  }
}

// 图表引用
const trendChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
const storeServiceChartRef = ref<HTMLElement>()
const storeTrendChartRef = ref<HTMLElement>()

// 初始化图表
const initCharts = () => {
  try {
    if (trendChartRef.value) {
      trendChart?.dispose()  // 销毁已存在的实例
      trendChart = echarts.init(trendChartRef.value, undefined, {
        renderer: 'canvas',
        useDirtyRect: true,
        useCoarsePointer: true
      })
    }
    if (pieChartRef.value) {
      pieChart?.dispose()  // 销毁已存在的实例
      pieChart = echarts.init(pieChartRef.value, undefined, {
        renderer: 'canvas',
        useDirtyRect: true,
        useCoarsePointer: true
      })
    }
  } catch (error) {
    console.error('初始化图表失败:', error)
  }
}

// 初始化门店详情图表
const initStoreCharts = () => {
  if (storeServiceChartRef.value) {
    storeServiceChart?.dispose()  // 销毁已存在的实例
    storeServiceChart = echarts.init(storeServiceChartRef.value, undefined, {
      renderer: 'canvas',
      useDirtyRect: true,
      useCoarsePointer: true
    })
  }
  if (storeTrendChartRef.value) {
    storeTrendChart?.dispose()  // 销毁已存在的实例
    storeTrendChart = echarts.init(storeTrendChartRef.value, undefined, {
      renderer: 'canvas',
      useDirtyRect: true,
      useCoarsePointer: true
    })
  }
}

// 更新门店详情图表
const updateStoreCharts = (services: ServiceDistribution[], trend: DailyTrend[]) => {
  if (!storeServiceChart || !storeTrendChart) {
    console.warn('门店图表实例未初始化')
    return
  }

  // 更新门店服务分布图
  storeServiceChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `${params.name}<br/>营收：¥${formatNumber(params.value)}<br/>占比：${params.percent}%`
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: services.map(item => ({
        name: item.type_name,
        value: item.revenue
      }))
    }]
  })

  // 更新门店营收趋势图
  storeTrendChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['营收', '订单数']
    },
    xAxis: {
      type: 'category',
      data: trend.map(item => item.date),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '营收',
        axisLabel: {
          formatter: (value: number) => `¥${formatNumber(value)}`
        }
      },
      {
        type: 'value',
        name: '订单数',
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: '营收',
        type: 'bar',
        data: trend.map(item => item.revenue)
      },
      {
        name: '订单数',
        type: 'line',
        yAxisIndex: 1,
        data: trend.map(item => item.order_count)
      }
    ]
  })
}

// 监听窗口大小变化
const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
  storeServiceChart?.resize()
  storeTrendChart?.resize()
}

// 生命周期钩子
onMounted(async () => {
  try {
    loading.value = true
    await nextTick()
    await loadData() // 先加载数据
    initCharts()     // 再初始化图表
    window.addEventListener('resize', handleResize)
  } catch (error) {
    console.error('初始化失败:', error)
  } finally {
    loading.value = false
  }
})

// 在组件卸载时销毁图表实例
onUnmounted(() => {
  trendChart?.dispose()
  pieChart?.dispose()
  storeServiceChart?.dispose()
  storeTrendChart?.dispose()
  window.removeEventListener('resize', handleResize)
})

// 监听天数变化
watch(days, () => {
  loadData()
})
// 监听抽屉显示状态
watch(drawerVisible, async (visible) => {
  if (visible) {
    await nextTick()
    initStoreCharts()
    if (selectedStore.value) {
      try {
        const [services, trend] = await Promise.all([
          getStoreServiceDistribution(selectedStore.value.store_id),
          getStoreDailyTrend(selectedStore.value.store_id, days.value)
        ])
        updateStoreCharts(services.data, trend.data)
      } catch (error) {
        console.error('加载门店详情失败:', error)
      }
    }
  } else {
    // 关闭抽屉时销毁图表实例
    storeServiceChart?.dispose()
    storeTrendChart?.dispose()
  }
})
</script>

<style scoped>
.analytics-container {
  padding: 24px;
}

.overview-cards {
  margin-bottom: 24px;
}

.overview-cards :deep(.ant-card) {
  height: 100%;
}

.card-footer {
  color: #999;
  font-size: 12px;
}

.chart-section {
  margin-bottom: 24px;
}

.store-section {
  margin-bottom: 24px;
}

.store-overview {
  margin-bottom: 24px;
}
</style>