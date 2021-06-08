import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Pizza(SqlAlchemyBase):
    __tablename__ = 'pizza'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    weight = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    orders = relationship("Association", back_populates="pizza")


    def __repr__(self):
        return f'<Pizza> {self.title}'
