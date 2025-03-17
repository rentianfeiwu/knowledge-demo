<template>
  <div class="inventory-container">
    <!-- 产品分类树 -->
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card title="产品分类">
          <a-tree
            v-model:selectedKeys="selectedKeys"
            :tree-data="categoryTree"
            @select="onCategorySelect"
          />
        </a-card>
      </a-col>
      
      <!-- 产品列表 -->
      <a-col :span="18">
        <a-table
          :columns="columns"
          :data-source="productList"
          :loading="loading"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'stock'">
              <a-tag :color="record.stock < record.alertThreshold ? 'red' : 'green'">
                {{ record.stock }}
              </a-tag>
            </template>
          </template>
        </a-table>
      </a-col>
    </a-row>
  </div>
</template> 