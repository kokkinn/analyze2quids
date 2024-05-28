"""
The Module for SQL Alchemy
"""
import hashlib

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RawTransaction(Base):
    __tablename__ = 'raw_transactions_tb'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    transaction_type = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    paid_out = Column(String(20), nullable=False)
    paid_in = Column(String(20), nullable=False)
    balance = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    checksum = Column(String(64), nullable=False, unique=True)

    def calculate_checksum(self) -> str:
        data = f"{self.date}{self.transaction_type}{self.description}{self.paid_in}{self.paid_out}{self.balance}"
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return checksum

    def __repr__(self) -> str:
        return f'<Raw Transaction {self.id}, {self.paid_in if self.paid_in else self.paid_out} {"in" if self.paid_in else "out"}>'


class EnhancedTransaction(Base):
    __tablename__ = 'enhanced_transactions_tb'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    type = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    direction = Column(Enum('in', 'out', name='transaction_direction'), nullable=False)
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
