from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class Product:
    name: str
    category: str
    specifications: Dict[str, Any] = field(default_factory=dict)
    base_price: float = 0.0
    unit: str = "piece"
    
    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category,
            'specifications': self.specifications,
            'base_price': self.base_price,
            'unit': self.unit
        }

@dataclass
class NegotiationOffer:
    agent_type: str  # 'buyer' or 'seller'
    price: float
    quantity: int
    conditions: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'agent_type': self.agent_type,
            'price': self.price,
            'quantity': self.quantity,
            'conditions': self.conditions,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class NegotiationSession:
    session_id: str
    product: Product
    buyer_max_price: float
    seller_min_price: float
    current_buyer_offer: Optional[float] = None
    current_seller_offer: Optional[float] = None
    offers_history: List[NegotiationOffer] = field(default_factory=list)
    status: str = "active"  # active, completed, failed
    final_price: Optional[float] = None
    
    def add_offer(self, offer: NegotiationOffer):
        self.offers_history.append(offer)
        if offer.agent_type == 'buyer':
            self.current_buyer_offer = offer.price
        else:
            self.current_seller_offer = offer.price
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'product': self.product.to_dict(),
            'buyer_max_price': self.buyer_max_price,
            'seller_min_price': self.seller_min_price,
            'current_buyer_offer': self.current_buyer_offer,
            'current_seller_offer': self.current_seller_offer,
            'offers_history': [offer.to_dict() for offer in self.offers_history],
            'status': self.status,
            'final_price': self.final_price
        }