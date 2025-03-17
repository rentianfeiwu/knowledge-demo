from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, SmallInteger, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = "ord_order"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True)
    type = Column(SmallInteger)
    status = Column(SmallInteger)
    should_money = Column(DECIMAL(10, 2))
    actual_money = Column(DECIMAL(10, 2))
    paid_money = Column(DECIMAL(10, 2))
    serve_money = Column(DECIMAL(10, 2))
    user_id = Column(Integer, index=True)
    store_id = Column(Integer, index=True)
    create_time = Column(DateTime)
    pay_time = Column(DateTime)

    details = relationship("OrderDetail", back_populates="order")

class OrderDetail(Base):
    __tablename__ = "ord_order_detail"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), ForeignKey("ord_order.order_no"))
    pro_type = Column(SmallInteger)
    price = Column(DECIMAL(10, 2))
    total_money = Column(DECIMAL(10, 2))
    num = Column(Integer)
    pro_name = Column(String(100))

    order = relationship("Order", back_populates="details")