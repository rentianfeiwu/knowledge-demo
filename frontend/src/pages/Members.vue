<template>
  <div class="members-container">
    <!-- 会员搜索和筛选 -->
    <a-form layout="inline" class="search-form">
      <a-form-item>
        <a-input-search
          v-model:value="searchQuery"
          placeholder="搜索会员姓名/手机号"
          @search="handleSearch"
        />
      </a-form-item>
      <a-form-item>
        <a-select v-model:value="memberLevel" style="width: 120px">
          <a-select-option value="">全部等级</a-select-option>
          <a-select-option value="vip">VIP会员</a-select-option>
          <a-select-option value="regular">普通会员</a-select-option>
        </a-select>
      </a-form-item>
    </a-form>

    <!-- 会员列表 -->
    <a-table
      :columns="columns"
      :data-source="memberList"
      :loading="loading"
      :pagination="pagination"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="showMemberDetail(record)">详情</a>
            <a @click="showServiceHistory(record)">服务记录</a>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template> 