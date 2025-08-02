import json
import time
from typing import Dict, List, Tuple, Optional
from agents.buyer_agent import BuyerAgent
from agents.seller_agent import SellerAgent
from services.voice_service import VoiceService

class NegotiationService:
    def __init__(self):
        self.buyer = BuyerAgent("Alex the Buyer")
        self.seller = SellerAgent("Maria the Seller")
        self.voice_service = VoiceService()
        
        self.current_item = None
        self.negotiation_active = False
        self.rounds_completed = 0
        self.max_rounds = 10
        self.negotiation_history = []
        
    def start_negotiation(self, item: str, item_details: str, 
                         seller_cost: float, seller_target: float, seller_min: float,
                         buyer_target: float, buyer_max: float) -> Dict:
        """Start a new negotiation session"""
        try:
            # Reset negotiation state
            self.negotiation_active = True
            self.rounds_completed = 0
            self.current_item = item
            self.negotiation_history = []
            
            # Set agent parameters
            self.seller.set_pricing(seller_cost, seller_target, seller_min)
            self.buyer.set_budget(buyer_target, buyer_max)
            
            # Seller creates initial listing
            seller_opening = self.seller.make_initial_listing(item, item_details)
            self._add_to_history("seller", seller_opening)
            
            # Voice output for seller
            self.voice_service.text_to_speech(seller_opening, "seller")
            
            return {
                'success': True,
                'message': seller_opening,
                'speaker': 'seller',
                'negotiation_id': int(time.time()),
                'round': 0
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_buyer_response(self, context: Dict) -> Dict:
        """Process buyer's response in negotiation"""
        try:
            if not self.negotiation_active:
                return {'success': False, 'error': 'No active negotiation'}
            
            # Get seller's last message
            last_seller_message = self._get_last_message('seller')
            
            # Generate buyer response
            buyer_response = self.buyer.generate_response(last_seller_message, {
                'item': self.current_item,
                'round': self.rounds_completed
            })
            
            self._add_to_history("buyer", buyer_response)
            
            # Voice output for buyer
            self.voice_service.text_to_speech(buyer_response, "buyer")
            
            self.rounds_completed += 1
            
            return {
                'success': True,
                'message': buyer_response,
                'speaker': 'buyer',
                'round': self.rounds_completed
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_seller_response(self, context: Dict) -> Dict:
        """Process seller's response in negotiation"""
        try:
            if not self.negotiation_active:
                return {'success': False, 'error': 'No active negotiation'}
            
            # Get buyer's last message
            last_buyer_message = self._get_last_message('buyer')
            
            # Generate seller response
            seller_response = self.seller.generate_response(last_buyer_message, {
                'item': self.current_item,
                'round': self.rounds_completed
            })
            
            self._add_to_history("seller", seller_response)
            
            # Voice output for seller
            self.voice_service.text_to_speech(seller_response, "seller")
            
            # Check for deal conclusion
            deal_status = self._check_deal_conclusion(seller_response)
            
            return {
                'success': True,
                'message': seller_response,
                'speaker': 'seller',
                'round': self.rounds_completed,
                'deal_concluded': deal_status['concluded'],
                'final_price': deal_status.get('price')
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def auto_negotiate(self, rounds: int = 5) -> List[Dict]:
        """Run automatic negotiation between agents"""
        results = []
        
        try:
            for round_num in range(rounds):
                if not self.negotiation_active:
                    break
                
                # Buyer's turn
                buyer_result = self.process_buyer_response({})
                if buyer_result['success']:
                    results.append(buyer_result)
                
                # Small delay for realism
                time.sleep(2)
                
                # Seller's turn
                seller_result = self.process_seller_response({})
                if seller_result['success']:
                    results.append(seller_result)
                    
                    # Check if deal is concluded
                    if seller_result.get('deal_concluded'):
                        break
                
                time.sleep(2)
                
                # Check max rounds
                if self.rounds_completed >= self.max_rounds:
                    self.negotiation_active = False
                    break
            
            return results
            
        except Exception as e:
            return [{'success': False, 'error': str(e)}]
    
    def _add_to_history(self, speaker: str, message: str):
        """Add message to negotiation history"""
        self.negotiation_history.append({
            'speaker': speaker,
            'message': message,
            'timestamp': time.time(),
            'round': self.rounds_completed
        })
    
    def _get_last_message(self, speaker: str) -> str:
        """Get the last message from specified speaker"""
        for entry in reversed(self.negotiation_history):
            if entry['speaker'] == speaker:
                return entry['message']
        return ""
    
    def _check_deal_conclusion(self, message: str) -> Dict:
        """Check if the negotiation has concluded with a deal"""
        # Simple keyword-based detection (can be enhanced with NLP)
        conclusion_keywords = ['deal', 'agreed', 'accept', 'sold', 'final price', 'shake hands']
        price_indicators = ['$', 'dollar', 'price']
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in conclusion_keywords):
            # Try to extract price (basic implementation)
            import re
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', message)
            final_price = float(price_match.group(1)) if price_match else None
            
            self.negotiation_active = False
            return {
                'concluded': True,
                'price': final_price
            }
        
        return {'concluded': False}
    
    def get_negotiation_summary(self) -> Dict:
        """Get summary of current negotiation"""
        return {
            'item': self.current_item,
            'active': self.negotiation_active,
            'rounds': self.rounds_completed,
            'history': self.negotiation_history,
            'buyer_target': self.buyer.target_price,
            'seller_target': self.seller.target_price
        }
