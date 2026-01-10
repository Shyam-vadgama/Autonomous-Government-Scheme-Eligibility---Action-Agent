"""
Multi-Provider AI Client
Automatically switches between AI providers when quota issues occur
Supports Gemini, OpenAI, and local models
"""
import os
import asyncio
from typing import Optional, Dict, Any, List
import json
from loguru import logger

class MultiProviderClient:
    """
    AI client that can use multiple providers with automatic fallback
    Handles quota limitations across different AI services
    """
    
    def __init__(self):
        self.providers = []
        self.current_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers in priority order"""
        
        print(f"DEBUG: GEMINI_API_KEY before check: {os.getenv('GEMINI_API_KEY')}")
        # 1. Try Gemini first (if configured)
        if os.getenv("GEMINI_API_KEY"):
            try:
                from config.gemini_client import GeminiClient
                gemini_client = GeminiClient()
                self.providers.append({
                    "name": "Gemini",
                    "client": gemini_client,
                    "active": True
                })
                logger.info("✅ Gemini provider initialized")
            except Exception as e:
                logger.warning(f"⚠️ Gemini provider failed: {str(e)}")
        
        # 2. Try OpenAI as fallback (if configured)
        if os.getenv("OPENAI_API_KEY"):
            try:
                from config.openai_client import OpenAIClient
                openai_client = OpenAIClient()
                self.providers.append({
                    "name": "OpenAI",
                    "client": openai_client,
                    "active": True
                })
                logger.info("✅ OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI provider failed: {str(e)}")
        
        # 3. Try local Ollama (if available)
        if self._check_ollama_available():
            try:
                ollama_client = self._create_ollama_client()
                self.providers.append({
                    "name": "Ollama",
                    "client": ollama_client,
                    "active": True
                })
                logger.info("✅ Ollama provider initialized")
            except Exception as e:
                logger.warning(f"⚠️ Ollama provider failed: {str(e)}")
        
        # Set current provider to the first available
        if self.providers:
            self.current_provider = self.providers[0]
            logger.info(f"🎯 Using {self.current_provider['name']} as primary provider")
        else:
            logger.error("❌ No AI providers available!")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _create_ollama_client(self):
        """Create a simple Ollama client"""
        return OllamaClient()
    
    async def generate_response(self, system_prompt: str, user_prompt: str, 
                              response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate response with automatic provider fallback
        """
        last_error = None
        
        for provider in self.providers:
            if not provider["active"]:
                continue
                
            try:
                logger.info(f"🔄 Trying {provider['name']} provider...")
                
                response = await provider["client"].generate_response(
                    system_prompt, user_prompt, response_format
                )
                
                logger.info(f"✅ {provider['name']} succeeded")
                self.current_provider = provider
                return response
                
            except Exception as e:
                error_msg = str(e).lower()
                logger.warning(f"⚠️ {provider['name']} failed: {str(e)[:100]}")
                last_error = e
                
                # Check if it's a quota/rate limit error
                if any(keyword in error_msg for keyword in ["quota", "rate_limit", "resource_exhausted"]):
                    logger.warning(f"🚫 {provider['name']} quota exhausted, trying next provider...")
                    provider["active"] = False  # Temporarily disable
                    continue
                else:
                    # Other error, might be temporary
                    continue
        
        # If all providers failed
        if last_error:
            logger.error("❌ All AI providers failed!")
            raise last_error
        else:
            raise Exception("No active AI providers available")
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        if self.current_provider:
            info = {
                "provider": self.current_provider["name"],
                "active": self.current_provider["active"]
            }
            
            # Get model info if available
            if hasattr(self.current_provider["client"], "get_model_info"):
                info.update(self.current_provider["client"].get_model_info())
            
            return info
        else:
            return {"provider": "None", "active": False}
    
    def get_all_providers_status(self) -> List[Dict[str, Any]]:
        """Get status of all providers"""
        return [
            {
                "name": provider["name"],
                "active": provider["active"],
                "current": provider == self.current_provider
            }
            for provider in self.providers
        ]

class OllamaClient:
    """Simple Ollama client for local inference"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = os.getenv("OLLAMA_MODEL", "llama2")
    
    async def generate_response(self, system_prompt: str, user_prompt: str, 
                              response_format: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using local Ollama"""
        try:
            import aiohttp
            
            prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        raise Exception(f"Ollama error: {response.status}")
                        
        except ImportError:
            raise ImportError("aiohttp required for Ollama. Install with: pip install aiohttp")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Ollama model info"""
        return {
            "provider": "Ollama",
            "model": self.model,
            "local": True,
            "cost": "Free"
        }