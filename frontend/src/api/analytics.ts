import request from '../utils/request'
import type { AxiosResponse } from 'axios'

export interface OverviewData {
  total_revenue: number;
  total_orders: number;
  avg_order_value: number;
  conversion_rate: number;
}

export interface StoreAnalytics {
  store_id: number;
  order_count: number;
  total_revenue: number;
  avg_order_value: number;
  completion_rate: number;
  customer_count: number;
}

export interface ServiceDistribution {
  type: number;
  type_name: string;
  revenue: number;
  count: number;
}

export interface DailyTrend {
  date: string;
  revenue: number;
  order_count: number;
}

export const getOverview = (days: number = 30): Promise<AxiosResponse<OverviewData>> => {
  return request({
    url: '/api/analytics/overview',  // 添加 /api 前缀
    method: 'get',
    params: { days }
  })
}

export const getServiceDistribution = (): Promise<AxiosResponse<ServiceDistribution[]>> => {
  return request({
    url: '/api/analytics/service-distribution',  // 添加 /api 前缀
    method: 'get'
  })
}

export const getStoreAnalytics = (days: number = 30): Promise<AxiosResponse<StoreAnalytics[]>> => {
  return request({
    url: '/api/analytics/store/overview',  // 添加 /api 前缀
    method: 'get',
    params: { days }
  })
}

export const getStoreServiceDistribution = (storeId: number): Promise<AxiosResponse<ServiceDistribution[]>> => {
  return request({
    url: `/api/analytics/store/${storeId}/services`,  // 添加 /api 前缀
    method: 'get'
  })
}

// 以下两个接口已经包含了 /api 前缀，无需修改
export const getStoreDailyTrend = (storeId: number, days: number = 30): Promise<AxiosResponse<DailyTrend[]>> => {
  return request({
    url: `/api/analytics/store/${storeId}/trend`,
    method: 'get',
    params: { days }
  })
}

export const getRevenueTrend = (days: number = 30): Promise<AxiosResponse<DailyTrend[]>> => {
  return request({
    url: '/api/analytics/revenue-trend',
    method: 'get',
    params: { days }
  })
}