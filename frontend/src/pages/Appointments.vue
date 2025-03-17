<template>
  <div class="appointments-container">
    <!-- 日历视图 -->
    <a-calendar
      :value="selectedDate"
      @select="onDateSelect"
      @panelChange="onPanelChange"
    >
      <template #dateCellRender="{ current }">
        <div class="appointments-cell">
          <a-badge
            v-for="item in getAppointments(current)"
            :key="item.id"
            :status="item.status"
            :text="item.time"
          />
        </div>
      </template>
    </a-calendar>

    <!-- 预约详情抽屉 -->
    <a-drawer
      v-model:visible="drawerVisible"
      title="预约详情"
      width="400"
    >
      <!-- 预约表单 -->
      <a-form :model="appointmentForm">
        <!-- 表单内容 -->
      </a-form>
    </a-drawer>
  </div>
</template> 