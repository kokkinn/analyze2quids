"""
The Module for SQL Alchemy
"""
import hashlib

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RawTransaction(Base):
    __tablename__ = 'raw_transactions_tb'

    id = Column(Integer, primary_key=True)
    date = Column(String(20), nullable=False)
    transaction_type = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    paid_out = Column(String(20), nullable=False)
    paid_in = Column(String(20), nullable=False)
    balance = Column(String(20), nullable=False)
    source = Column(String(20), nullable=False)
    checksum = Column(String(64), nullable=False, unique=True)
    enhanced_transaction = relationship("EnhancedTransaction", back_populates="raw_transaction")
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def calculate_checksum(self) -> str:
        data = f"{self.date}{self.transaction_type}{self.description}{self.paid_out}{self.paid_in}{self.balance}"
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return checksum

    def __repr__(self) -> str:
        return f'<Raw Transaction {self.id}, {self.paid_in if self.paid_in else self.paid_out} {"in" if self.paid_in else "out"}>'


class EnhancedTransaction(Base):
    __tablename__ = 'enhanced_transactions_tb'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    type = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    direction = Column(String(3), nullable=False)
    balance = Column(Float, nullable=False)
    source = Column(String(20), nullable=False)
    raw_transaction_id = Column(Integer, ForeignKey('raw_transactions_tb.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    raw_transaction = relationship("RawTransaction", back_populates="enhanced_transaction")

    def calculate_checksum(self) -> str:
        data = f"{self.date}{self.type}{self.entity}{self.value}{self.direction}{self.balance}"
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return checksum
