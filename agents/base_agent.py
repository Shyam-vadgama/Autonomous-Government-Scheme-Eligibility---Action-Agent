"""
Base Agent Class following Google Agent Development Kit patterns
Provides the foundation for all specialized agents
"""
import asyncio
import json
import uuid
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from loguru import logger

from config.gemini_client import get_gemini_client, GeminiClient


class AgentMessage(BaseModel):
    """Standard message format between agents"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    sender: str
    recipient: str
    message_type: str  # 'request', 'response', 'error', 'notification'
    content: Dict[str, Any]
    priority: str = "normal"  # 'low', 'normal', 'high', 'urgent'


class AgentState(BaseModel):
    """Agent state tracking"""
    agent_id: str
    status: str = "idle"  # 'idle', 'processing', 'error', 'busy'
    last_activity: datetime = Field(default_factory=datetime.now)
    current_task: Optional[str] = None
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base Agent class following Google ADK patterns
    Provides common functionality for all specialized agents
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: List[str]
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        
        self.state = AgentState(agent_id=agent_id)
        self.llm_client = get_gemini_client()
        
        # Message queues
        self.inbox: List[AgentMessage] = []
        self.outbox: List[AgentMessage] = []
        
        # Performance tracking
        self.task_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized agent '{self.name}' with ID: {self.agent_id}")
    
    async def initialize(self) -> bool:
        """Initialize the agent and its dependencies"""
        try:
            # Check if we should skip initialization to preserve quota
            skip_init = os.environ.get('SKIP_AGENT_INIT_TEST', '').lower() in ('true', '1', 'yes')
            minimal_init = os.environ.get('MINIMAL_INIT', '').lower() in ('true', '1', 'yes')
            
            if skip_init or minimal_init:
                logger.info(f"Skipping full initialization for {self.name} (quota conservation)")
                self.state.status = "quota_limited"
                self.state.last_activity = datetime.now()
                return True
            
            # Test Gemini connection
            logger.info(f"Initializing agent {self.name}...")
            
            # Test basic model connectivity
            test_result = await self.llm_client.generate_response(
                "Test connection",
                system_instruction=f"You are the {self.name}. Respond with 'Ready to serve.'"
            )
            
            if test_result:
                self.state.status = "idle"
                logger.info(f"Agent {self.name} initialized successfully")
                return True
            else:
                self.state.status = "error"
                logger.error(f"Failed to initialize agent {self.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing agent {self.name}: {e}")
            self.state.status = "error"
            return False
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """Handle incoming messages"""
        self.inbox.append(message)
        self.state.last_activity = datetime.now()
        self.state.current_task = message.message_type
        
        try:
            self.state.status = "processing"
            logger.info(f"Agent {self.name} processing message from {message.sender}")
            
            # Process the request
            if message.message_type == "request":
                result = await self.process_request(message.content)
                
                response = AgentMessage(
                    sender=self.agent_id,
                    recipient=message.sender,
                    message_type="response",
                    content=result
                )
            else:
                # Handle other message types
                response = AgentMessage(
                    sender=self.agent_id,
                    recipient=message.sender,
                    message_type="notification",
                    content={"status": "message_received", "original_type": message.message_type}
                )
            
            self.outbox.append(response)
            self.state.status = "idle"
            self.state.current_task = None
            
            # Update performance metrics
            self._update_performance_metrics(message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling message in {self.name}: {e}")
            self.state.status = "error"
            
            error_response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="error",
                content={"error": str(e), "agent": self.name}
            )
            self.outbox.append(error_response)
            return error_response
    
    async def generate_llm_response(
        self,
        prompt: str,
        structured: bool = False,
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate response using the local LLM"""
        system_prompt = self.get_system_prompt()
        
        if structured:
            if not response_schema:
                # Default schema for structured responses
                response_schema = {
                    "response": "string",
                    "success": "boolean"
                }
            structured_response = await self.llm_client.generate_structured_response(
                prompt=prompt,
                response_schema=response_schema,
                system_instruction=system_prompt
            )
            
            # Ensure we always have a success indicator
            if structured_response and isinstance(structured_response, dict):
                if "success" not in structured_response and "error" not in structured_response:
                    # If we have valid data and no error, mark as successful
                    structured_response["success"] = True
                elif "error" in structured_response and not structured_response.get("success", False):
                    # If there's an error and no explicit success flag, mark as failed
                    structured_response["success"] = False
            
            return structured_response
        else:
            response_text = await self.llm_client.generate_response(
                prompt=prompt,
                system_instruction=system_prompt
            )
            return {
                "response": response_text,
                "success": bool(response_text)
            }
    
    def _update_performance_metrics(self, request: AgentMessage, response: AgentMessage):
        """Update performance metrics"""
        processing_time = (response.timestamp - request.timestamp).total_seconds()
        
        self.state.performance_metrics.update({
            "total_requests": self.state.performance_metrics.get("total_requests", 0) + 1,
            "avg_processing_time": (
                self.state.performance_metrics.get("avg_processing_time", 0) + processing_time
            ) / 2,
            "last_processing_time": processing_time,
            "success_rate": self._calculate_success_rate()
        })
        
        # Add to task history
        self.task_history.append({
            "timestamp": request.timestamp,
            "processing_time": processing_time,
            "request_type": request.message_type,
            "success": response.message_type != "error"
        })
        
        # Keep only last 100 entries
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate from task history"""
        if not self.task_history:
            return 1.0
        
        successful_tasks = sum(1 for task in self.task_history if task["success"])
        return successful_tasks / len(self.task_history)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.state.status,
            "last_activity": self.state.last_activity,
            "current_task": self.state.current_task,
            "performance_metrics": self.state.performance_metrics,
            "capabilities": self.capabilities,
            "queue_size": len(self.inbox)
        }
    
    def get_health_check(self) -> Dict[str, Any]:
        """Get agent health information"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "healthy": self.state.status != "error",
            "uptime": (datetime.now() - self.state.last_activity).total_seconds(),
            "performance_score": self.state.performance_metrics.get("success_rate", 0.0),
            "capabilities": self.capabilities
        }