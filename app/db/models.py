from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Ticker(Base):

    __tablename__ = 'ticker'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ticker = Column(String(10))
    prices = relationship("TickerPrice")


class TickerPrice(Base):

    __tablename__ = 'ticker_price'
    id = Column(Integer, autoincrement=True, primary_key=True)
    ticker_id = Column(ForeignKey('ticker.id'))
    price = Column(Integer)
