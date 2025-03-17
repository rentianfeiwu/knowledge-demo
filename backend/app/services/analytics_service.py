from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, case, distinct
from datetime import datetime, timedelta
from typing import List, Dict
from app.models.order import Order, OrderDetail

class AnalyticsService:
    # 服务类型映射
    PRO_TYPE_MAP = {
        1: "产品",
        2: "项目",
        3: "疗程卡",
        4: "储值卡",
        5: "次卡",
        6: "虚拟卡券",
        7: "套餐",
        8: "赠送优惠券"
    }

    @staticmethod
    async def get_revenue_overview(db: Session, days: int = 30) -> Dict:
        """获取营收概览"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 修改查询条件，移除 status 过滤
        total_revenue = db.query(func.sum(Order.paid_money))\
            .filter(Order.create_time.between(start_date, end_date))\
            .scalar() or 0
    
        # 获取所有订单数
        total_orders = db.query(func.count(Order.id))\
            .filter(Order.create_time.between(start_date, end_date))\
            .scalar() or 0
    
        # 平均客单价
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
        # 支付转化率（已支付订单数 / 总订单数）
        paid_orders = db.query(func.count(Order.id))\
            .filter(Order.status == 3)\
            .filter(Order.create_time.between(start_date, end_date))\
            .scalar() or 0
        
        conversion_rate = paid_orders / total_orders if total_orders > 0 else 0
    
        return {
            # 保留两位小数
            "total_revenue": round(float(total_revenue), 2),
            "total_orders": int(total_orders),  # 确保返回整数
            "avg_order_value": round(float(avg_order_value), 2),
            "conversion_rate": round(float(conversion_rate), 2)
        }

    @staticmethod
    async def get_revenue_trend(db: Session, days: int = 30) -> List[Dict]:
        """获取每日营收趋势"""
        start_date = datetime.now() - timedelta(days=days)
        
        daily_revenue = db.query(
            func.date(Order.create_time).label('date'),
            func.sum(Order.paid_money).label('revenue')
        )\
        .filter(Order.status == 3)\
        .filter(Order.create_time >= start_date)\
        .group_by(func.date(Order.create_time))\
        .order_by('date')\
        .all()

        return [
            {"date": str(day.date), "revenue": float(day.revenue)}
            for day in daily_revenue
        ]

    @staticmethod
    async def get_store_analytics(db: Session, days: int = 30) -> List[Dict]:
        """获取门店维度分析"""
        start_date = datetime.now() - timedelta(days=days)
        
        store_stats = db.query(
            Order.store_id,
            func.count(Order.id).label('order_count'),
            func.sum(Order.paid_money).label('total_revenue'),
            func.avg(Order.paid_money).label('avg_order_value'),
            func.sum(case([(Order.status == 3, 1)], else_=0)).label('completed_orders'),
            func.count(distinct(Order.user_id)).label('customer_count')
        )\
        .filter(Order.create_time >= start_date)\
        .group_by(Order.store_id)\
        .order_by(desc('total_revenue'))\
        .all()

        return [{
            "store_id": item.store_id,
            "order_count": item.order_count,
            "total_revenue": float(item.total_revenue or 0),
            "avg_order_value": float(item.avg_order_value or 0),
            "completion_rate": item.completed_orders / item.order_count if item.order_count > 0 else 0,
            "customer_count": item.customer_count
        } for item in store_stats]

    @staticmethod
    async def get_store_service_distribution(db: Session, store_id: int) -> List[Dict]:
        """获取指定门店的服务类型分布"""
        service_stats = db.query(
            OrderDetail.pro_type,
            func.sum(OrderDetail.total_money).label('revenue'),
            func.count(OrderDetail.id).label('count')
        )\
        .join(Order, Order.order_no == OrderDetail.order_no)\
        .filter(Order.store_id == store_id)\
        .filter(Order.status == 3)\
        .group_by(OrderDetail.pro_type)\
        .order_by(desc('revenue'))\
        .all()

        return [{
            "type": item.pro_type,
            "type_name": AnalyticsService.PRO_TYPE_MAP.get(item.pro_type, "未知类型"),
            "revenue": float(item.revenue or 0),
            "count": item.count
        } for item in service_stats]

    @staticmethod
    async def get_store_daily_trend(db: Session, store_id: int, days: int = 30) -> List[Dict]:
        """获取指定门店的每日营收趋势"""
        start_date = datetime.now() - timedelta(days=days)
        
        daily_stats = db.query(
            func.date(Order.create_time).label('date'),
            func.sum(Order.paid_money).label('revenue'),
            func.count(Order.id).label('order_count')
        )\
        .filter(and_(
            Order.store_id == store_id,
            Order.status == 3,
            Order.create_time >= start_date
        ))\
        .group_by(func.date(Order.create_time))\
        .order_by('date')\
        .all()

        return [{
            "date": str(item.date),
            "revenue": float(item.revenue or 0),
            "order_count": item.order_count
        } for item in daily_stats]

    @staticmethod
    async def get_service_distribution(db: Session) -> List[Dict]:
        """获取服务类型分布"""
        service_stats = db.query(
            OrderDetail.pro_type,
            func.sum(OrderDetail.total_money).label('revenue'),
            func.count(OrderDetail.id).label('count')
        )\
        .join(Order, Order.order_no == OrderDetail.order_no)\
        .filter(Order.status == 3)\
        .group_by(OrderDetail.pro_type)\
        .order_by(desc('revenue'))\
        .all()

        return [{
            "type": item.pro_type,
            "type_name": AnalyticsService.PRO_TYPE_MAP.get(item.pro_type, "未知类型"),
            "revenue": float(item.revenue or 0),
            "count": item.count
        } for item in service_stats]