from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, condecimal


class WalletBase(BaseModel):
    id: str


class WalletCreate(WalletBase):
    pass


class WalletResponse(WalletBase):
    balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OperationBase(BaseModel):
    operation_type: Literal["DEPOSIT", "WITHDRAW"]
    amount: condecimal(gt=0)


class OperationResponse(OperationBase):
    id: str
    wallet_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
