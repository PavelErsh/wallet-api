from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid
from app import models, schemas
from decimal import Decimal


def get_wallet(db: Session, wallet_id: str):
    stmt = select(models.Wallet).where(models.Wallet.id == wallet_id).with_for_update()
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def create_wallet(db: Session, wallet: schemas.WalletCreate):
    existing_wallet = get_wallet(db, wallet.id)
    if existing_wallet:
        return None, "Wallet already exists"

    db_wallet = models.Wallet(id=wallet.id, balance=Decimal("0.00"))
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet, None


def perform_operation(db: Session, wallet_id: str, operation: schemas.OperationBase):
    try:
        wallet = get_wallet(db, wallet_id)

        if not wallet:
            return None, "Wallet not found"

        amount_decimal = Decimal(str(operation.amount))
        new_balance = wallet.balance

        if operation.operation_type == "DEPOSIT":
            new_balance += amount_decimal
        elif operation.operation_type == "WITHDRAW":
            if wallet.balance < amount_decimal:
                return None, "Insufficient funds"
            new_balance -= amount_decimal

        wallet.balance = new_balance

        transaction = models.Transaction(
            id=str(uuid.uuid4()),
            wallet_id=wallet_id,
            operation_type=operation.operation_type,
            amount=amount_decimal,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction, None

    except Exception as e:
        db.rollback()
        return None, f"Operation failed: {str(e)}"
