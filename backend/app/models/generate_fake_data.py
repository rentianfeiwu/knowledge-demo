from faker import Faker
import random
from sqlalchemy import create_engine, Column, Integer, String, DateTime, SmallInteger, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta

# 创建数据库连接
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/knowledge_base"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 定义数据模型
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

# 初始化Faker
fake = Faker("zh_CN")

# 创建会话
db = SessionLocal()

# 清空现有数据（可选）
# db.query(OrderDetail).delete()
# db.query(Order).delete()
# db.commit()

# 生成假数据
def generate_fake_data():
    try:
        # 生成30天内的订单
        start_date = datetime.now() - timedelta(days=30)
        
        for _ in range(100):  # 生成100个订单
            # 随机选择一个门店（假设门店ID范围是1-10）
            store_id = random.randint(1, 10)
            
            # 随机选择一个会员（假设会员ID范围是1-100）
            member_id = random.randint(1, 100)
            
            # 随机选择订单类型
            order_type = random.choice([1, 2, 3, 4])  # 假设有3种订单类型
            
            # 随机选择订单状态
            order_status = random.choice([0, 1, 2, 3])  # 假设有4种状态
            
            # 随机生成订单金额
            should_money = round(random.uniform(100, 5000), 2)
            actual_money = round(random.uniform(80, should_money), 2)
            paid_money = actual_money if order_status == 3 else round(random.uniform(0, actual_money), 2)
            serve_money = round(random.uniform(0, paid_money), 2)
            
            # 随机生成创建时间和支付时间
            create_time = fake.date_time_between(start_date=start_date, end_date=datetime.now())
            pay_time = create_time + timedelta(minutes=random.randint(10, 60)) if order_status >= 2 else None
            
            # 创建订单
            order = Order(
                order_no=fake.uuid4().replace("-", "")[:20],
                type=order_type,
                status=order_status,
                should_money=should_money,
                actual_money=actual_money,
                paid_money=paid_money,
                serve_money=serve_money,
                store_id=store_id,
                create_time=create_time,
                pay_time=pay_time,
                user_id=member_id
            )
            
            db.add(order)
            db.flush()  # 冲刷会话，生成order.id
            
            # 为每个订单生成1-5个明细
            detail_count = random.randint(1, 5)
            for __ in range(detail_count):
                # 随机选择产品类型
                pro_type = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
                
                # 随机生成产品价格和数量
                price = round(random.uniform(50, 1000), 2)
                num = random.randint(1, 5)
                total_money = round(price * num, 2)
                
                # 随机生成产品名称
                pro_name = fake.word() + "服务"
                
                detail = OrderDetail(
                    order_no=order.order_no,
                    pro_type=pro_type,
                    price=price,
                    total_money=total_money,
                    num=num,
                    pro_name=pro_name
                )
                
                db.add(detail)
            
        db.commit()
        print("假数据生成成功！")
    except Exception as e:
        db.rollback()
        print(f"生成假数据时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_fake_data()