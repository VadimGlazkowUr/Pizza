from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
import datetime


class Association(SqlAlchemyBase):
    __tablename__ = 'association'
    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    pizza_id = Column(Integer, ForeignKey('pizza.id'), primary_key=True)
    count = Column(Integer)
    pizza = relationship("Pizza", back_populates="orders")
    order = relationship("Order", back_populates="pizzas")


class Order(SqlAlchemyBase):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    time_order = Column(DateTime, default=datetime.datetime.now)
    time_delivery = Column(DateTime, nullable=True)
    pizzas = relationship("Association", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order> {self.user_name}'
