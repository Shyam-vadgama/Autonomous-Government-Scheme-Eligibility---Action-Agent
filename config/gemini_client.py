"""
Gemini AI Configuration
Handles Google Gemini AI integration for the government scheme agent system
"""
import os
import google.genai as genai
from typing import Optional, Dict, Any
import json
import asyncio
import time
from loguru import logger


class GeminiConfig:
    """Gemini AI configuration settings"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "30"))
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")


class GeminiClient:
    """
    Google Gemini AI client for the agent system
    Provides structured communication with Gemini API
    """
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or GeminiConfig()
        self._model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with API key and settings"""
        try:
            # Configure the client with API key
            self.client = genai.Client(api_key=self.config.api_key)
            
            logger.info(f"Gemini client initialized with model: {self.config.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise
    
    async def check_connection(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            # Simple test generation
            response = self.client.models.generate_content(
                model=self.config.model_name,
                contents="Test connection"
            )
            return response and response.text
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Generate response from Gemini with retry logic
        
        Args:
            prompt: The user prompt
            system_instruction: System instruction for the model
            max_retries: Maximum retry attempts for quota issues
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        for attempt in range(max_retries + 1):
            try:
                # Combine system instruction with prompt if provided
                if system_instruction:
                    full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"
                else:
                    full_prompt = prompt
                
                # Generate response using new API
                response = self.client.models.generate_content(
                    model=self.config.model_name,
                    contents=full_prompt
                )
                
                if response and response.text:
                    return response.text.strip()
                else:
                    logger.warning("Empty response from Gemini")
                    return ""
                    
            except Exception as e:
                error_str = str(e)
                
                # Check for quota exhaustion
                if "429" in error_str and "RESOURCE_EXHAUSTED" in error_str:
                    if attempt < max_retries:
                        # Extract retry delay from error message
                        retry_delay = 10  # Default 10 seconds
                        try:
                            # Try to extract delay from error
                            if "retry in" in error_str:
                                import re
                                delay_match = re.search(r'retry in ([0-9.]+)s', error_str)
                                if delay_match:
                                    retry_delay = float(delay_match.group(1)) + 1
                        except:
                            pass
                        
                        logger.warning(f"Quota exceeded, retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_retries + 1})")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"Max retries exceeded for quota: {error_str}")
                        # Return a graceful fallback instead of raising
                        return "Service temporarily unavailable due to quota limits. Please try again later."
                else:
                    logger.error(f"Error generating Gemini response: {error_str}")
                    if attempt < max_retries:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise
        
        return "Service unavailable after retries."
    
    async def generate_structured_response(
        self, 
        prompt: str, 
        response_schema: Dict[str, Any],
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from Gemini
        
        Args:
            prompt: The user prompt
            response_schema: Expected JSON schema
            system_instruction: System instruction for the model
            
        Returns:
            Parsed JSON response
        """
        try:
            # Create structured prompt
            schema_description = json.dumps(response_schema, indent=2)
            structured_prompt = f"""
{system_instruction or "You are a helpful assistant."}

Please respond with valid JSON that matches this schema:
{schema_description}

User request: {prompt}

Response (JSON only):
"""
            
            response_text = await self.generate_response(structured_prompt)
            
            # Extract JSON from response
            try:
                # Try to find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end != 0:
                    json_text = response_text[json_start:json_end]
                    return json.loads(json_text)
                else:
                    # If no JSON found, try parsing the entire response
                    return json.loads(response_text)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                
                # Return a default structure with the raw response
                return {
                    "error": "Failed to parse structured response",
                    "raw_response": response_text,
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            return {
                "error": str(e),
                "success": False
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_name": self.config.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "api_configured": bool(self.config.api_key)
        }


# Global Gemini client instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get global Gemini client instance"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client


def reset_gemini_client():
    """Reset global Gemini client instance"""
    global _gemini_client
    _gemini_client = None