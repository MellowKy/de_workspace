from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, PositiveFloat

class CurrencyEnum(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class OrderContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(..., description="Unique Event UUID")
    timestamp: datetime = Field(..., description="UTC ISO timestamp")
    customer_id: str = Field(..., description="Customer UUID string")
    amount: PositiveFloat = Field(..., description="Positive order value")
    currency: CurrencyEnum = Field(..., description="ISO 4217 Currency Code")
