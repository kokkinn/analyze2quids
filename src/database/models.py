"""
The Module for SQL Alchemy
"""
import hashlib

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RawTransaction(Base):
    __tablename__ = 'raw_transactions_tb'

    id = Column(Integer, primary_key=True)
    date = Column(String(20), nullable=False)
    type = Column(String(100),
                  nullable=True)  # Payment to / Contactless Payment / Visa purchase / Bank credit IN/OUT
    description = Column(String(200), nullable=False)  # Business/intermediate name / Bank credit IN/OUT / ?Card Number?
    paid_out = Column(String(20), nullable=False)
    paid_in = Column(String(20), nullable=False)
    balance = Column(String(20), nullable=True)
    card_name = Column(String(50), nullable=False)  # name displayed in statement
    location = Column(String(40), nullable=True)  # location of the transaction
    source = Column(String(20), nullable=False)  # bank name
    checksum = Column(String(64), nullable=False, unique=True)
    filename = Column(String(100), nullable=False)
    enhanced_transaction = relationship("EnhancedTransaction", back_populates="raw_transaction")
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def calculate_checksum(self) -> str:
        data = f"{self.date}{self.type}{self.description}{self.paid_out}{self.paid_in}{self.balance}"
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return checksum

    def __repr__(self) -> str:
        return f'<Raw Transaction {self.id}, {self.paid_in if self.paid_in else self.paid_out} {"in" if self.paid_in else "out"}>'


class EnhancedTransaction(Base):
    __tablename__ = 'enhanced_transactions_tb'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    type = Column(String(100), nullable=True)
    entity = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # derived at a runtime of ETL
    value = Column(Float, nullable=False)
    direction = Column(String(3), nullable=False)
    location = Column(String(40), nullable=True)
    balance = Column(Float, nullable=True)
    card_name = Column(String(50), nullable=False)
    source = Column(String(20), nullable=False)
    raw_transaction_id = Column(Integer, ForeignKey('raw_transactions_tb.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    raw_transaction = relationship("RawTransaction", back_populates="enhanced_transaction")

    def calculate_checksum(self) -> str:
        data = f"{self.date}{self.type}{self.entity}{self.value}{self.direction}{self.balance}"
        checksum = hashlib.sha256(data.encode()).hexdigest()
        return checksum

    def __repr__(self) -> str:
        return f'<Enhanced Transaction {self.id}, {self.type} {self.entity} {self.value} {self.direction}>'


class PersonalCategoryRegex(Base):
    __tablename__ = 'personal_categories_tb'

    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False, unique=True)
    regex = Column(String(50), nullable=False)
    hide = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Personal Category {self.category}>'