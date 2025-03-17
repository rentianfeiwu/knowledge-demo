<template>
  <div class="marketing-container">
    <!-- 营销活动列表 -->
    <a-tabs v-model:activeKey="activeTab">
      <a-tab-pane key="campaigns" tab="营销活动">
        <a-list :data-source="campaigns">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-card :title="item.title" style="width: 100%">
                <template #extra>
                  <a-tag :color="item.status === 'active' ? 'green' : 'default'">
                    {{ item.status === 'active' ? '进行中' : '已结束' }}
                  </a-tag>
                </template>
                <p>{{ item.description }}</p>
                <a-progress :percent="item.progress" />
              </a-card>
            </a-list-item>
          </template>
        </a-list>
      </a-tab-pane>
      
      <a-tab-pane key="coupons" tab="优惠券管理">
        <!-- 优惠券管理内容 -->
      </a-tab-pane>
    </a-tabs>
  </div>
</template> 