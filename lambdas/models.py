from decimal import Decimal
from pydantic import BaseModel
from typing import Literal, List

class User(BaseModel):
    username: str
    password: str

class PurchaseOrderLine(BaseModel):
    line: int
    artist_id: int
    artist: str
    album_id: int
    album: str
    quantity: int
    line_total: Decimal

class PurchaseOrder(BaseModel):
    client_id: str
    purchase_order_id: int
    status: Literal["pending-supplier", "pending-buyer", "confirmed"]
    modified: str
    data: List[PurchaseOrderLine]
    estimated_delivery: str
    dispatch_cost: Decimal

class DispatchUpdate:
    client: str
    status: Literal['received','pending-supplier','shipped','rescheduled']