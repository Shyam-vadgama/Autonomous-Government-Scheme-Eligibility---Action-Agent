"""
OpenAI Client for Government Scheme Agent
Drop-in replacement for Gemini client when quota issues occur
"""
import os
import asyncio
from typing import Optional, Dict, Any
import json
from loguru import logger

class OpenAIConfig:
    """OpenAI configuration settings"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
        self.timeout = int(os.getenv("OPENAI_TIMEOUT", "30"))
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

class OpenAIClient:
    """
    OpenAI client that mimics the Gemini client interface
    Provides drop-in replacement for quota issues
    """
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        self.config = config or OpenAIConfig()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.config.api_key)
            logger.info(f"OpenAI client initialized with model: {self.config.model_name}")
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    async def generate_response(self, system_prompt: str, user_prompt: str, 
                              response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate response using OpenAI API
        Compatible with Gemini client interface
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Handle JSON response format if requested
            kwargs = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            if response_format and response_format.get("type") == "json_object":
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            
            # Check for specific error types
            if "rate_limit" in str(e).lower():
                logger.warning("OpenAI rate limit exceeded")
                await asyncio.sleep(1)
                raise
            elif "quota" in str(e).lower():
                logger.warning("OpenAI quota exceeded")
                raise
            else:
                raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": "OpenAI",
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }