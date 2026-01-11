"""
Ollama Integration Module for Government Scheme Agent
Handles local model connections and API calls
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
import ollama
from loguru import logger
from pydantic import BaseModel


class OllamaConfig(BaseModel):
    """Configuration for Ollama connection"""
    base_url: str = "http://localhost:11434"
    model: str = "llama2:7b"
    timeout: int = 300
    temperature: float = 0.7
    max_tokens: int = 2048


class OllamaClient:
    """Ollama client for local model inference"""
    
    def __init__(self, config: OllamaConfig = None):
        self.config = config or OllamaConfig()
        self.client = ollama.Client(host=self.config.base_url)
        
    async def check_model_availability(self) -> bool:
        """Check if the specified model is available"""
        try:
            models = self.client.list()
            available_models = [model['name'] for model in models.get('models', [])]
            return self.config.model in available_models
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    async def pull_model_if_needed(self) -> bool:
        """Pull the model if it's not available locally"""
        try:
            if not await self.check_model_availability():
                logger.info(f"Pulling model {self.config.model}...")
                self.client.pull(self.config.model)
                logger.info(f"Model {self.config.model} pulled successfully")
            return True
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate response from Ollama model"""
        try:
            # Ensure model is available
            await self.pull_model_if_needed()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat(
                model=self.config.model,
                messages=messages,
                options={
                    "temperature": temperature or self.config.temperature,
                    "num_predict": max_tokens or self.config.max_tokens,
                }
            )
            
            return {
                "success": True,
                "response": response['message']['content'],
                "model": self.config.model,
                "prompt_tokens": response.get('prompt_eval_count', 0),
                "completion_tokens": response.get('eval_count', 0)
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    async def generate_structured_response(
        self, 
        prompt: str, 
        system_prompt: str,
        response_schema: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate structured response with JSON formatting"""
        
        structured_system_prompt = f"""{system_prompt}

IMPORTANT: Your response must be in valid JSON format following this structure:
{{
    "reasoning": "Your step-by-step reasoning process",
    "conclusion": "Your final conclusion or decision",
    "confidence_score": 0.85,
    "additional_data": {{}}
}}

Ensure your response is valid JSON that can be parsed."""
        
        result = await self.generate_response(
            prompt=prompt,
            system_prompt=structured_system_prompt,
            temperature=0.3  # Lower temperature for more structured responses
        )
        
        if result["success"]:
            try:
                import json
                # Try to parse the response as JSON
                parsed_response = json.loads(result["response"])
                result["structured_data"] = parsed_response
                result["is_structured"] = True
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse structured response as JSON: {e}")
                result["is_structured"] = False
                result["parse_error"] = str(e)
        
        return result


# Global Ollama client instance
_ollama_client = None

def get_ollama_client() -> OllamaClient:
    """Get or create global Ollama client instance"""
    global _ollama_client
    if _ollama_client is None:
        config = OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama2:7b")
        )
        _ollama_client = OllamaClient(config)
    return _ollama_client


async def test_ollama_connection():
    """Test Ollama connection and model availability"""
    client = get_ollama_client()
    
    # Test basic connectivity
    logger.info("Testing Ollama connection...")
    if not await client.check_model_availability():
        logger.warning("Model not available, attempting to pull...")
        if not await client.pull_model_if_needed():
            logger.error("Failed to pull model")
            return False
    
    # Test generation
    logger.info("Testing response generation...")
    result = await client.generate_response(
        prompt="Hello, please respond with 'Ollama connection successful'",
        system_prompt="You are a helpful assistant."
    )
    
    if result["success"]:
        logger.info(f"Ollama test successful: {result['response']}")
        return True
    else:
        logger.error(f"Ollama test failed: {result.get('error')}")
        return False


if __name__ == "__main__":
    # Test the Ollama connection when run directly
    asyncio.run(test_ollama_connection())