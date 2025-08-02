import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, personality: str):
        self.name = name
        self.role = role  # 'buyer' or 'seller'
        self.personality = personality
        self.conversation_history = []
        self.current_offer = None
        self.target_price = None
        self.min_acceptable = None
        self.max_acceptable = None
        
    @abstractmethod
    def generate_response(self, message: str, context: Dict) -> str:
        """Generate response based on message and context"""
        pass
    
    @abstractmethod
    def evaluate_offer(self, offer: Dict) -> bool:
        """Evaluate if an offer is acceptable"""
        pass
    
    def add_to_history(self, message: str, sender: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'message': message,
            'sender': sender,
            'timestamp': time.time()
        })
    
    def get_negotiation_context(self) -> Dict:
        """Get current negotiation context"""
        return {
            'role': self.role,
            'personality': self.personality,
            'history': self.conversation_history[-5:],  # Last 5 messages
            'current_offer': self.current_offer,
            'target_price': self.target_price
        }
    
    def set_negotiation_params(self, target: float, min_price: float, max_price: float):
        """Set negotiation parameters"""
        self.target_price = target
        self.min_acceptable = min_price
        self.max_acceptable = max_price
