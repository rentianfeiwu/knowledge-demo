from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, select
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.models.order import Order, OrderDetail
from datetime import datetime, timedelta
from typing import List

router = APIRouter()

@router.get("/overview")
async def get_overview(days: int = 30, db: Session = Depends(get_db)):
    """获取营收概览"""
    return await AnalyticsService.get_revenue_overview(db, days)

@router.get("/revenue-trend")
async def get_revenue_trend(days: int = 30, db: Session = Depends(get_db)):
    """获取每日营收趋势"""
    return await AnalyticsService.get_revenue_trend(db, days)

@router.get("/service-distribution")
async def get_service_distribution(db: Session = Depends(get_db)):
    """获取服务类型分布"""
    return await AnalyticsService.get_service_distribution(db)

@router.get("/store/overview")
async def get_store_overview(days: int = Query(30, ge=1, le=365)):
    db = next(get_db())
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        # 使用 select 构建查询
        query = (
            select(
                Order.store_id,
                func.count(Order.id).label('order_count'),
                func.sum(Order.paid_money).label('total_revenue'),
                func.count(case(
                    (Order.status == 3, 1),
                )).label('completed_orders'),
                func.count(func.distinct(Order.user_id)).label('customer_count')
            )
            .where(
                Order.create_time.between(start_date, end_date)
            )
            .group_by(Order.store_id)
        )
        
        # 执行查询
        results = db.execute(query).all()
        
        # 转换结果
        store_analytics = [
            {
                "store_id": row.store_id,
                "order_count": row.order_count,
                "total_revenue": float(row.total_revenue or 0),
                "avg_order_value": float(row.total_revenue or 0) / row.order_count if row.order_count > 0 else 0,
                "completion_rate": row.completed_orders / row.order_count if row.order_count > 0 else 0,
                "customer_count": row.customer_count
            }
            for row in results
        ]
        
        return store_analytics
        
    except Exception as e:
        print(f"Error in get_store_overview: {str(e)}")
        raise

@router.get("/store/{store_id}/services")
async def get_store_service_distribution(
    store_id: int,
    db: Session = Depends(get_db)
):
    """获取指定门店的服务类型分布"""
    return await AnalyticsService.get_store_service_distribution(db, store_id)

@router.get("/store/{store_id}/trend")
async def get_store_daily_trend(
    store_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取指定门店的每日营收趋势"""
    return await AnalyticsService.get_store_daily_trend(db, store_id, days)