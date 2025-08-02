import requests
import json
from typing import Dict, Any
from config import Config

class LlamaService:
    def __init__(self):
        self.api_key = Config.LLAMA_API_KEY
        self.api_url = Config.LLAMA_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Debug output
        print(f"🔑 LlamaService initialized with API key: {self.api_key[:10]}...")
        print(f"🌐 Using endpoint: {self.api_url}")
    
    def generate_response(self, prompt: str, context: Dict = None) -> str:
        """Generate response using Llama 3 8B model"""
        try:
            payload = {
                "model": "meta-llama/Meta-Llama-3-8B-Instruct-Lite",
                "messages": [
                    {
                        "role": "system",
                        "content": self._build_system_prompt(context)
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            print(f"🔧 Making API request to: {self.api_url}")
            print(f"🔧 Using model: {payload['model']}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API Response received")
                
                # Check if response has expected structure
                if 'choices' in result and len(result['choices']) > 0:
                    if 'message' in result['choices'][0]:
                        return result['choices'][0]['message']['content'].strip()
                    elif 'text' in result['choices'][0]:
                        return result['choices'][0]['text'].strip()
                
                return f"Unexpected response structure: {result}"
                
            elif response.status_code == 401:
                return "❌ Authentication Error: Invalid API key"
            elif response.status_code == 403:
                return "❌ Access Denied: Check your API permissions"
            elif response.status_code == 429:
                return "❌ Rate Limited: Too many requests"
            else:
                return f"❌ HTTP Error {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return "❌ Request timeout - API took too long to respond"
        except requests.exceptions.ConnectionError:
            return "❌ Connection error - Check your internet connection"
        except ValueError as e:
            return f"❌ JSON parsing error: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt based on agent context"""
        if not context:
            return "You are a helpful AI assistant in a negotiation."
            
        role = context.get('role', 'participant')
        personality = context.get('personality', 'diplomatic')
        
        if role == 'buyer':
            base_prompt = f"""You are a {personality} buyer in a negotiation. Your goal is to get the best price while maintaining a good relationship. 
            Be strategic, friendly, and persuasive. Always respond as the buyer character."""
        else:
            base_prompt = f"""You are a {personality} seller in a negotiation. Your goal is to maximize profit while ensuring customer satisfaction. 
            Be professional, convincing, and value-focused. Always respond as the seller character."""
            
        if context.get('target_price'):
            base_prompt += f" Your target price is ${context['target_price']}."
            
        return base_prompt
