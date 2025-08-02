import json
from typing import Dict
from agents.base_agent import BaseAgent
from services.llama_service import LlamaService

class BuyerAgent(BaseAgent):
    def __init__(self, name: str = "Alex the Buyer"):
        super().__init__(
            name=name,
            role="buyer",
            personality="The Smooth Diplomat: Wins with charm, collaboration, and win-win pitches"
        )
        self.llama_service = LlamaService()
        self.budget_limit = None
        
    def generate_response(self, message: str, context: Dict) -> str:
        """Generate buyer response using Llama API"""
        negotiation_context = self.get_negotiation_context()
        negotiation_context.update(context)
        
        # Build prompt for buyer
        prompt = f"""
        NEGOTIATION CONTEXT:
        - You are {self.name}, a diplomatic buyer
        - Item being negotiated: {context.get('item', 'Unknown item')}
        - Seller's last message: "{message}"
        - Your target price: ${self.target_price}
        - Your maximum budget: ${self.max_acceptable}
        
        RECENT CONVERSATION:
        {self._format_history()}
        
        INSTRUCTIONS:
        - Respond as a charming, collaborative buyer
        - Try to find win-win solutions
        - Be diplomatic but firm about your budget
        - Make counteroffers when appropriate
        - Keep responses under 100 words
        - If the price is acceptable, show enthusiasm
        
        Generate your response:
        """
        
        response = self.llama_service.generate_response(prompt, negotiation_context)
        self.add_to_history(response, self.name)
        return response
    
    def evaluate_offer(self, offer: Dict) -> bool:
        """Evaluate if seller's offer is acceptable"""
        offered_price = offer.get('price', float('inf'))
        
        if self.max_acceptable and offered_price <= self.max_acceptable:
            return True
        return False
    
    def make_initial_offer(self, item: str, starting_price: float) -> str:
        """Make initial offer for an item"""
        context = {
            'item': item,
            'starting_price': starting_price
        }
        
        prompt = f"""
        You are {self.name}, starting a negotiation for {item}.
        The seller's asking price is ${starting_price}.
        Your target price is ${self.target_price}.
        
        Make an engaging opening offer that:
        - Shows interest in the item
        - Presents a reasonable counter-offer
        - Builds rapport with the seller
        - Explains your perspective diplomatically
        
        Keep it under 80 words and sound natural.
        """
        
        response = self.llama_service.generate_response(prompt, self.get_negotiation_context())
        self.add_to_history(response, self.name)
        return response
    
    def _format_history(self) -> str:
        """Format conversation history for context"""
        if not self.conversation_history:
            return "No previous conversation."
            
        formatted = []
        for entry in self.conversation_history[-3:]:  # Last 3 exchanges
            formatted.append(f"{entry['sender']}: {entry['message']}")
        return "\n".join(formatted)
    
    def set_budget(self, target: float, max_budget: float):
        """Set buyer's budget parameters"""
        self.set_negotiation_params(target, target * 0.8, max_budget)
        self.budget_limit = max_budget
