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

#{'client_id': 'bm-dev', 'purchase_order_id': 117, 
# 'status': 'pending-supplier', 'modified': '2026-07-09 20:05:06', 'data': 
# [{'line': 1, 'artist_id': 102, 'artist': 'Corpus Christii', 
#   'album_id': 1002, 'album': 'Rising', 'quantity': 1, 'line_total': Decimal('6.53')}], 
# 'estimated_delivery': '2026-07-13 12:30', 'dispatch_cost': Decimal('0.98')}