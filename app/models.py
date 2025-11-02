from sqlalchemy import CheckConstraint, Column, DateTime, Numeric, String, func

from app.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    balance = Column(Numeric(scale=2), nullable=False, default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (CheckConstraint(balance >= 0, name="non_negative_balance"),)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, index=True)
    wallet_id = Column(String(36), nullable=False, index=True)
    operation_type = Column(String(10), nullable=False)  # 'DEPOSIT' or 'WITHDRAW'
    amount = Column(Numeric(scale=2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            operation_type.in_(["DEPOSIT", "WITHDRAW"]), name="valid_operation_type"
        ),
        CheckConstraint(amount > 0, name="positive_amount"),
    )
