import json
from typing import Dict
from agents.base_agent import BaseAgent
from services.llama_service import LlamaService

class SellerAgent(BaseAgent):
    def __init__(self, name: str = "Maria the Seller"):
        super().__init__(
            name=name,
            role="seller",
            personality="Professional and value-focused merchant"
        )
        self.llama_service = LlamaService()
        self.cost_price = None
        
    def generate_response(self, message: str, context: Dict) -> str:
        """Generate seller response using Llama API"""
        negotiation_context = self.get_negotiation_context()
        negotiation_context.update(context)
        
        prompt = f"""
        NEGOTIATION CONTEXT:
        - You are {self.name}, a professional seller
        - Item being sold: {context.get('item', 'Unknown item')}
        - Buyer's message: "{message}"
        - Your target price: ${self.target_price}
        - Your minimum acceptable: ${self.min_acceptable}
        - Item cost: ${self.cost_price}
        
        RECENT CONVERSATION:
        {self._format_history()}
        
        INSTRUCTIONS:
        - Respond as a professional, value-focused seller
        - Emphasize the quality and benefits of your item
        - Be firm but fair with pricing
        - Make counteroffers when buyer's offer is too low
        - Show flexibility while protecting your margins
        - Keep responses under 100 words
        - If buyer's offer is acceptable, show appreciation
        
        Generate your response:
        """
        
        response = self.llama_service.generate_response(prompt, negotiation_context)
        self.add_to_history(response, self.name)
        return response
    
    def evaluate_offer(self, offer: Dict) -> bool:
        """Evaluate if buyer's offer is acceptable"""
        offered_price = offer.get('price', 0)
        
        if self.min_acceptable and offered_price >= self.min_acceptable:
            return True
        return False
    
    def make_initial_listing(self, item: str, quality_details: str) -> str:
        """Create initial item listing"""
        context = {
            'item': item,
            'quality_details': quality_details
        }
        
        prompt = f"""
        You are {self.name}, listing {item} for sale.
        
        Item details: {quality_details}
        Your asking price: ${self.target_price}
        
        Create an attractive listing that:
        - Highlights the item's quality and value
        - Justifies the asking price
        - Invites negotiation
        - Sounds professional and trustworthy
        
        Keep it under 80 words and make it compelling.
        """
        
        response = self.llama_service.generate_response(prompt, self.get_negotiation_context())
        self.add_to_history(response, self.name)
        return response
    
    def _format_history(self) -> str:
        """Format conversation history for context"""
        if not self.conversation_history:
            return "No previous conversation."
            
        formatted = []
        for entry in self.conversation_history[-3:]:
            formatted.append(f"{entry['sender']}: {entry['message']}")
        return "\n".join(formatted)
    
    def set_pricing(self, cost: float, target: float, min_price: float):
        """Set seller's pricing parameters"""
        self.cost_price = cost
        self.set_negotiation_params(target, min_price, target * 1.5)
