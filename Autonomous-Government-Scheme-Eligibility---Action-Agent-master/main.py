"""
Government Scheme Eligibility Agent - Main Orchestrator
Coordinates all specialized agents to provide comprehensive scheme assistance
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger

# Import all agents
from agents.citizen_profile_agent import CitizenProfileAgent
from agents.scheme_discovery import SchemeDiscoveryAgent
from agents.eligibility_reasoning import EligibilityReasoningAgent
from agents.action_planner import ActionPlannerAgent
from agents.follow_up_agent import FollowUpAgent

# Import system tools
from tools.system_tools import (
    get_decision_logger, get_user_state_store, get_rule_engine,
    HumanReadableExplainer, SafeFailureHandler, DecisionLog
)

# Import data
from data.schemes_db import GOVERNMENT_SCHEMES


class UserRequest(BaseModel):
    """User request to the system"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    request_type: str  # 'new_application', 'follow_up', 'update_profile'
    user_input: str
    existing_profile: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemResponse(BaseModel):
    """Complete system response"""
    request_id: str
    user_id: str
    success: bool = True
    processing_time_ms: float = 0.0
    
    # Main results
    user_profile: Optional[Dict[str, Any]] = None
    discovered_schemes: Optional[List[Dict[str, Any]]] = None
    eligibility_assessments: Optional[List[Dict[str, Any]]] = None
    action_plans: Optional[List[Dict[str, Any]]] = None
    follow_up_analysis: Optional[Dict[str, Any]] = None
    
    # Interactive elements
    next_question: Optional[str] = None
    completion_percentage: Optional[int] = None
    
    # Human-readable content
    summary: str = ""
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    
    # Metadata
    agents_involved: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    error_details: Optional[Dict[str, Any]] = None


class GovernmentSchemeAgent:
    """
    Main orchestrator for the Government Scheme Eligibility Agent system
    Coordinates all specialized agents to provide comprehensive assistance
    """
    
    def __init__(self):
        # Initialize all agents
        self.profile_analyzer = CitizenProfileAgent()  # Replaced ProfileAnalyzerAgent
        self.scheme_discovery = SchemeDiscoveryAgent()
        self.eligibility_reasoning = EligibilityReasoningAgent()
        self.action_planner = ActionPlannerAgent()
        self.follow_up_agent = FollowUpAgent()
        
        # Initialize system tools
        self.decision_logger = get_decision_logger()
        self.user_state_store = get_user_state_store()
        self.rule_engine = get_rule_engine()
        self.explainer = HumanReadableExplainer()
        self.failure_handler = SafeFailureHandler()
        
        # Track system status
        self.agents = {
            "profile_analyzer": self.profile_analyzer,  # Kept key same for compatibility
            "scheme_discovery": self.scheme_discovery,
            "eligibility_reasoning": self.eligibility_reasoning,
            "action_planner": self.action_planner,
            "follow_up_agent": self.follow_up_agent
        }
        
        logger.info("Government Scheme Agent system initialized")
    
    async def initialize_system(self) -> bool:
        """Initialize all agents and system components"""
        try:
            logger.info("Initializing Government Scheme Agent system...")
            
            # Initialize all agents
            init_tasks = []
            for agent_name, agent in self.agents.items():
                init_tasks.append(self._init_agent_safe(agent_name, agent))
            
            results = await asyncio.gather(*init_tasks)
            
            successful_agents = sum(1 for result in results if result)
            total_agents = len(self.agents)
            
            if successful_agents == total_agents:
                logger.info("All agents initialized successfully")
                return True
            elif successful_agents > total_agents // 2:
                logger.warning(f"Partial initialization: {successful_agents}/{total_agents} agents ready")
                return True
            else:
                logger.error(f"System initialization failed: only {successful_agents}/{total_agents} agents ready")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing system: {e}")
            return False
    
    async def quick_quota_test(self) -> bool:
        """Quick test to check if API quota is available"""
        try:
            # Test with just the first agent and a very short timeout
            first_agent = list(self.agents.values())[0]
            
            # Set a short timeout for quota detection
            import asyncio
            try:
                result = await asyncio.wait_for(
                    first_agent.llm_client.generate_response("test", "Hello"),
                    timeout=5.0  # 5 second timeout
                )
                return True
            except asyncio.TimeoutError:
                logger.warning("Quota test timed out - likely quota exceeded")
                return False
            except Exception as quota_error:
                if "quota" in str(quota_error).lower() or "resource_exhausted" in str(quota_error).lower():
                    logger.warning("Quota exhausted detected in quick test")
                    return False
                else:
                    # Other error, might still work
                    return True
                    
        except Exception as e:
            logger.error(f"Quick quota test failed: {e}")
            return False
    
    async def _init_agent_safe(self, agent_name: str, agent) -> bool:
        """Safely initialize an agent with error handling"""
        try:
            result = await agent.initialize()
            if result:
                logger.info(f"Agent {agent_name} initialized successfully")
            else:
                logger.error(f"Agent {agent_name} failed to initialize")
            return result
        except Exception as e:
            logger.error(f"Error initializing agent {agent_name}: {e}")
            return False
    
    async def process_user_request(self, request: UserRequest) -> SystemResponse:
        """Process complete user request through the agent workflow"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing user request: {request.request_id}")
            
            # Auto-load existing profile from DB if not provided in request
            if not request.existing_profile:
                saved_state = self.user_state_store.get_user_state(request.user_id)
                if saved_state and saved_state.profile:
                    logger.info(f"Loaded existing profile from DB for user {request.user_id}")
                    request.existing_profile = saved_state.profile

            # Route request based on type
            if request.request_type == "new_application":
                response = await self._process_new_application(request)
            elif request.request_type == "discover_schemes":
                response = await self._process_scheme_discovery(request)
            elif request.request_type == "follow_up":
                response = await self._process_follow_up(request)
            elif request.request_type == "update_profile":
                response = await self._process_profile_update(request)
            else:
                response = SystemResponse(
                    request_id=request.request_id,
                    user_id=request.user_id,
                    success=False,
                    error_details={"error": f"Unknown request type: {request.request_type}"}
                )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            response.processing_time_ms = processing_time
            
            # Log the complete interaction
            await self._log_system_interaction(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing user request: {e}")
            return SystemResponse(
                request_id=request.request_id,
                user_id=request.user_id,
                success=False,
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error_details={"error": str(e), "type": type(e).__name__}
            )

    async def _process_scheme_discovery(self, request: UserRequest) -> SystemResponse:
        """Process scheme discovery request (lighter weight than new_application)"""
        logger.info(f"Processing scheme discovery for user {request.user_id}")
        
        response = SystemResponse(request_id=request.request_id, user_id=request.user_id)
        agents_used = []
        
        try:
            # Step 1: Use existing profile directly
            response.user_profile = request.existing_profile
            
            if not response.user_profile:
                # Try to run analyzer if no profile
                logger.info("No profile found, running analyzer...")
                profile_request = {
                    "user_input": request.user_input or "Extract profile from history",
                    "existing_profile": {}
                }
                profile_result = await self._call_agent_safe("profile_analyzer", profile_request)
                if profile_result and profile_result.get("success"):
                    response.user_profile = profile_result["profile"]
                    agents_used.append("profile_analyzer")
                else:
                    return self._create_error_response(request, "No profile available", agents_used)

            # Step 2: Discover relevant schemes
            logger.info("Step 2: Discovering relevant schemes...")
            discovery_request = {
                "user_profile": response.user_profile,
                "options": request.options
            }
            
            discovery_result = await self._call_agent_safe("scheme_discovery", discovery_request)
            if discovery_result and discovery_result.get("success"):
                response.discovered_schemes = discovery_result["results"]["highly_relevant"][:10]
                agents_used.append("scheme_discovery")
                logger.info(f"✓ Found {len(response.discovered_schemes)} relevant schemes")
            else:
                return self._create_error_response(request, "Scheme discovery failed", agents_used)
            
            # Step 3: Evaluate eligibility for top schemes
            logger.info("Step 3: Evaluating eligibility for top schemes...")
            eligibility_assessments = []
            
            # Evaluate top 5 to be responsive
            for scheme in response.discovered_schemes[:5]:
                scheme_details = self._get_scheme_details(scheme["scheme_id"])
                if scheme_details:
                    eligibility_request = {
                        "user_profile": response.user_profile,
                        "scheme_details": scheme_details
                    }
                    eligibility_result = await self._call_agent_safe("eligibility_reasoning", eligibility_request)
                    if eligibility_result and eligibility_result.get("success"):
                        eligibility_assessments.append(eligibility_result["assessment"])
            
            response.eligibility_assessments = eligibility_assessments
            if eligibility_assessments:
                agents_used.append("eligibility_reasoning")
            
            response.summary = f"Found {len(response.discovered_schemes)} schemes based on your profile."
            response.confidence_score = self._calculate_overall_confidence(response)
            response.agents_involved = agents_used
            
            return response

        except Exception as e:
            logger.error(f"Error in scheme discovery: {e}")
            return self._create_error_response(request, str(e), agents_used)
    
    async def _process_new_application(self, request: UserRequest) -> SystemResponse:
        """Process new scheme application request"""
        logger.info(f"Processing new application for user {request.user_id}")
        
        response = SystemResponse(request_id=request.request_id, user_id=request.user_id)
        agents_used = []
        
        try:
            # Step 1: Analyze user profile
            logger.info("Step 1: Analyzing user profile...")
            profile_request = {
                "user_input": request.user_input,
                "existing_profile": request.existing_profile
            }
            
            profile_result = await self._call_agent_safe("profile_analyzer", profile_request)
            if profile_result and profile_result.get("success"):
                response.user_profile = profile_result["profile"]
                response.next_question = profile_result.get("next_question")
                response.completion_percentage = profile_result.get("completion_percentage")
                agents_used.append("profile_analyzer")
                logger.info("✓ Profile analysis completed")
            else:
                logger.error("✗ Profile analysis failed")
                error_msg = profile_result.get("error", "Profile analysis failed") if profile_result else "Profile analysis agent did not return a result."
                return self._create_error_response(request, error_msg, agents_used)
            
            # Step 2: Discover relevant schemes
            logger.info("Step 2: Discovering relevant schemes...")
            discovery_request = {
                "user_profile": response.user_profile,
                "options": request.options
            }
            
            discovery_result = await self._call_agent_safe("scheme_discovery", discovery_request)
            if discovery_result and discovery_result.get("success"):
                response.discovered_schemes = discovery_result["results"]["highly_relevant"][:5]  # Top 5
                agents_used.append("scheme_discovery")
                logger.info(f"✓ Found {len(response.discovered_schemes)} relevant schemes")
            else:
                logger.error("✗ Scheme discovery failed")
                return self._create_error_response(request, "Scheme discovery failed", agents_used)
            
            # Step 3: Evaluate eligibility for top schemes
            logger.info("Step 3: Evaluating eligibility...")
            eligibility_assessments = []
            
            for scheme in response.discovered_schemes[:3]:  # Evaluate top 3
                # Get full scheme details
                scheme_details = self._get_scheme_details(scheme["scheme_id"])
                if scheme_details:
                    eligibility_request = {
                        "user_profile": response.user_profile,
                        "scheme_details": scheme_details
                    }
                    
                    eligibility_result = await self._call_agent_safe("eligibility_reasoning", eligibility_request)
                    if eligibility_result and eligibility_result.get("success"):
                        eligibility_assessments.append(eligibility_result["assessment"])
            
            response.eligibility_assessments = eligibility_assessments
            if eligibility_assessments:
                agents_used.append("eligibility_reasoning")
                logger.info(f"✓ Evaluated eligibility for {len(eligibility_assessments)} schemes")
            
            # Step 4: Create action plans for eligible schemes
            logger.info("Step 4: Creating action plans...")
            action_plans = []
            
            for assessment in eligibility_assessments:
                if assessment["overall_status"] in ["eligible", "conditionally_eligible"]:
                    scheme_details = self._get_scheme_details(assessment["scheme_id"])
                    plan_request = {
                        "scheme_details": scheme_details,
                        "eligibility_assessment": assessment,
                        "user_profile": response.user_profile
                    }
                    
                    plan_result = await self._call_agent_safe("action_planner", plan_request)
                    if plan_result and plan_result.get("success"):
                        action_plans.append(plan_result["action_plan"])
            
            response.action_plans = action_plans
            if action_plans:
                agents_used.append("action_planner")
                logger.info(f"✓ Created {len(action_plans)} action plans")
            
            # Step 5: Generate summary and recommendations
            response.summary = self._generate_comprehensive_summary(response)
            response.recommendations = self._generate_recommendations(response)
            response.next_steps = self._generate_next_steps(response)
            response.confidence_score = self._calculate_overall_confidence(response)
            response.agents_involved = agents_used
            
            # Save user state
            await self._update_user_state(request.user_id, response)
            
            logger.info("✓ New application processing completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error in new application processing: {e}")
            return self._create_error_response(request, str(e), agents_used)
    
    async def _process_follow_up(self, request: UserRequest) -> SystemResponse:
        """Process follow-up request for existing application"""
        logger.info(f"Processing follow-up for user {request.user_id}")
        
        response = SystemResponse(request_id=request.request_id, user_id=request.user_id)
        agents_used = []
        
        try:
            # Get user state and active plans
            user_state = self.user_state_store.get_user_state(request.user_id)
            if not user_state or not user_state.active_plans:
                return SystemResponse(
                    request_id=request.request_id,
                    user_id=request.user_id,
                    success=False,
                    summary="No active applications found. Please start a new application.",
                    error_details={"error": "No active plans found"}
                )
            
            # Process follow-up for the most recent plan
            active_plan_id = user_state.active_plans[-1]  # Most recent
            
            # Mock: Get plan details (in real implementation, you'd retrieve from database)
            follow_up_request = {
                "user_profile": user_state.profile,
                "action_plan": {"plan_id": active_plan_id},  # Simplified for demo
                "progress_updates": [],  # Would come from user input
                "options": request.options
            }
            
            follow_up_result = await self._call_agent_safe("follow_up_agent", follow_up_request)
            if follow_up_result and follow_up_result.get("success"):
                response.follow_up_analysis = follow_up_result["analysis"]
                agents_used.append("follow_up_agent")
                
                response.summary = follow_up_result["summary"]
                response.recommendations = self._extract_recommendations_from_followup(follow_up_result)
                response.next_steps = self._extract_next_steps_from_followup(follow_up_result)
                response.confidence_score = 0.8
                response.agents_involved = agents_used
                
                logger.info("✓ Follow-up processing completed")
                return response
            else:
                return self._create_error_response(request, "Follow-up analysis failed", agents_used)
                
        except Exception as e:
            logger.error(f"Error in follow-up processing: {e}")
            return self._create_error_response(request, str(e), agents_used)
    
    async def _process_profile_update(self, request: UserRequest) -> SystemResponse:
        """Process profile update request"""
        logger.info(f"Processing profile update for user {request.user_id}")
        
        try:
            # Re-analyze updated profile
            profile_request = {
                "user_input": request.user_input,
                "existing_profile": request.existing_profile
            }
            
            profile_result = await self._call_agent_safe("profile_analyzer", profile_request)
            if profile_result and profile_result.get("success"):
                # Update user state
                success = self.user_state_store.update_user_profile(
                    request.user_id, 
                    profile_result["profile"]
                )
                
                if success:
                    return SystemResponse(
                        request_id=request.request_id,
                        user_id=request.user_id,
                        user_profile=profile_result["profile"],
                        next_question=profile_result.get("next_question"),
                        completion_percentage=profile_result.get("completion_percentage"),
                        summary="Profile updated successfully. Your eligibility may have changed.",
                        recommendations=["Review your active applications for any changes"],
                        next_steps=["Check if new schemes are now available"],
                        agents_involved=["profile_analyzer"],
                        confidence_score=0.9
                    )
                else:
                    raise Exception("Failed to save updated profile")
            else:
                error_msg = profile_result.get("error", "Profile analysis failed") if profile_result else "Profile analysis agent did not return a result."
                logger.error(f"Error in profile update: {error_msg}")
                return SystemResponse(
                    request_id=request.request_id,
                    user_id=request.user_id,
                    success=False,
                    summary=f"Failed to update profile: {error_msg}",
                    error_details={"error": error_msg}
                )
                
        except Exception as e:
            logger.error(f"Error in profile update: {e}")
            return SystemResponse(
                request_id=request.request_id,
                user_id=request.user_id,
                success=False,
                summary="Failed to update profile",
                error_details={"error": str(e)}
            )
    
    async def _call_agent_safe(self, agent_name: str, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Safely call an agent with error handling"""
        try:
            agent = self.agents.get(agent_name)
            if not agent:
                logger.error(f"Agent {agent_name} not found")
                return None
            
            # Create agent message
            from agents.base_agent import AgentMessage
            message = AgentMessage(
                sender="orchestrator",
                recipient=agent_name,
                message_type="request",
                content=request_data
            )
            
            # Call agent
            response_message = await agent.handle_message(message)
            
            if response_message.message_type == "response":
                return response_message.content
            elif response_message.message_type == "error":
                logger.error(f"Agent {agent_name} returned error: {response_message.content}")
                return None
            else:
                logger.warning(f"Unexpected response type from {agent_name}: {response_message.message_type}")
                return response_message.content
                
        except Exception as e:
            logger.error(f"Error calling agent {agent_name}: {e}")
            return None
    
    def _get_scheme_details(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        """Get full scheme details by ID"""
        for scheme in GOVERNMENT_SCHEMES:
            if scheme["scheme_id"] == scheme_id:
                return scheme
        return None
    
    def _create_error_response(self, request: UserRequest, error_message: str, agents_used: List[str]) -> SystemResponse:
        """Create error response with fallback content"""
        fallback = self.failure_handler.create_minimal_response(request.request_type)
        
        return SystemResponse(
            request_id=request.request_id,
            user_id=request.user_id,
            success=False,
            summary=f"Processing error: {error_message}",
            recommendations=fallback.get("suggested_actions", ["Please try again later"]),
            next_steps=["Contact support if the problem persists"],
            agents_involved=agents_used,
            error_details={"error": error_message, "fallback": fallback}
        )
    
    def _generate_comprehensive_summary(self, response: SystemResponse) -> str:
        """Generate comprehensive summary of results"""
        summary_parts = []
        
        if response.user_profile:
            profile_name = response.user_profile.get("name", "User")
            summary_parts.append(f"Profile analyzed for {profile_name}")
        
        if response.discovered_schemes:
            summary_parts.append(f"Found {len(response.discovered_schemes)} relevant schemes")
        
        if response.eligibility_assessments:
            eligible_count = sum(1 for a in response.eligibility_assessments if a["overall_status"] == "eligible")
            summary_parts.append(f"Eligible for {eligible_count} schemes")
        
        if response.action_plans:
            summary_parts.append(f"Created {len(response.action_plans)} action plans")
        
        if not summary_parts:
            return "Analysis completed"
        
        return " • ".join(summary_parts)
    
    def _generate_recommendations(self, response: SystemResponse) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        if response.eligibility_assessments:
            # Find best eligible scheme
            eligible_schemes = [a for a in response.eligibility_assessments if a["overall_status"] == "eligible"]
            if eligible_schemes:
                best_scheme = max(eligible_schemes, key=lambda x: x.get("confidence_score", 0))
                recommendations.append(f"Start with {best_scheme['scheme_name']} - you're fully eligible")
        
        if response.action_plans:
            # Get top priority action from first plan
            first_plan = response.action_plans[0]
            critical_steps = first_plan.get("critical_steps", [])
            if critical_steps:
                recommendations.append(f"Priority action: {critical_steps[0]['title']}")
        
        if not recommendations:
            recommendations.append("Review available schemes and prepare required documents")
        
        return recommendations
    
    def _generate_next_steps(self, response: SystemResponse) -> List[str]:
        """Generate immediate next steps"""
        next_steps = []
        
        if response.action_plans:
            plan = response.action_plans[0]
            critical_steps = plan.get("critical_steps", [])
            if critical_steps:
                next_steps.append(critical_steps[0]["title"])
                if len(critical_steps) > 1:
                    next_steps.append(critical_steps[1]["title"])
        
        if not next_steps:
            next_steps = [
                "Gather required identity documents",
                "Visit local government office for guidance"
            ]
        
        return next_steps
    
    def _calculate_overall_confidence(self, response: SystemResponse) -> float:
        """Calculate overall confidence score"""
        confidence_factors = []
        
        if response.user_profile:
            confidence_factors.append(response.user_profile.get("confidence_score", 0.5))
        
        if response.eligibility_assessments:
            avg_confidence = sum(a.get("confidence_score", 0.5) for a in response.eligibility_assessments) / len(response.eligibility_assessments)
            confidence_factors.append(avg_confidence)
        
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.5
    
    def _extract_recommendations_from_followup(self, follow_up_result: Dict[str, Any]) -> List[str]:
        """Extract recommendations from follow-up analysis"""
        analysis = follow_up_result.get("analysis", {})
        urgent_recs = analysis.get("urgent_recommendations", [])
        standard_recs = analysis.get("standard_recommendations", [])
        
        recommendations = []
        for rec in urgent_recs[:2]:
            recommendations.append(rec.get("title", "Complete urgent action"))
        for rec in standard_recs[:1]:
            recommendations.append(rec.get("title", "Complete recommended action"))
        
        return recommendations or ["Continue working on your action plan"]
    
    def _extract_next_steps_from_followup(self, follow_up_result: Dict[str, Any]) -> List[str]:
        """Extract next steps from follow-up analysis"""
        analysis = follow_up_result.get("analysis", {})
        urgent_recs = analysis.get("urgent_recommendations", [])
        
        next_steps = []
        for rec in urgent_recs[:2]:
            if rec.get("specific_instructions"):
                next_steps.extend(rec["specific_instructions"][:2])
        
        return next_steps or ["Follow your action plan", "Check back for updates"]
    
    async def _update_user_state(self, user_id: str, response: SystemResponse):
        """Update user state with new information"""
        try:
            # Update profile
            if response.user_profile:
                self.user_state_store.update_user_profile(user_id, response.user_profile)
            
            # Add active plans
            if response.action_plans:
                for plan in response.action_plans:
                    plan_id = plan.get("plan_id")
                    if plan_id:
                        self.user_state_store.add_active_plan(user_id, plan_id)
        except Exception as e:
            logger.error(f"Error updating user state: {e}")
    
    async def _log_system_interaction(self, request: UserRequest, response: SystemResponse):
        """Log complete system interaction"""
        try:
            decision = DecisionLog(
                agent_id="orchestrator",
                user_id=request.user_id,
                decision_type=request.request_type,
                input_data={
                    "request_id": request.request_id,
                    "user_input": request.user_input[:200],  # Truncated for privacy
                    "options": request.options
                },
                output_data={
                    "success": response.success,
                    "agents_involved": response.agents_involved,
                    "confidence_score": response.confidence_score
                },
                reasoning=response.summary,
                confidence_score=response.confidence_score,
                execution_time_ms=response.processing_time_ms,
                success=response.success
            )
            
            self.decision_logger.log_decision(decision)
        except Exception as e:
            logger.error(f"Error logging system interaction: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        agent_statuses = {}
        for agent_name, agent in self.agents.items():
            try:
                agent_statuses[agent_name] = agent.get_status()
            except Exception as e:
                agent_statuses[agent_name] = {"error": str(e)}
        
        return {
            "system": "Government Scheme Eligibility Agent",
            "version": "1.0.0",
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "agents": agent_statuses
        }


# Global system instance
_government_scheme_agent = None

def get_government_scheme_agent() -> GovernmentSchemeAgent:
    """Get or create the global government scheme agent instance"""
    global _government_scheme_agent
    if _government_scheme_agent is None:
        _government_scheme_agent = GovernmentSchemeAgent()
    return _government_scheme_agent


# Main entry point for testing
async def main():
    """Main function for testing the system"""
    logger.info("Starting Government Scheme Eligibility Agent System")
    
    # Initialize system
    agent_system = get_government_scheme_agent()
    success = await agent_system.initialize_system()
    
    if not success:
        logger.error("Failed to initialize system")
        return
    
    logger.info("System initialized successfully")
    
    # Test with sample request
    test_request = UserRequest(
        user_id="test_user_001",
        request_type="new_application",
        user_input="""
        My name is Ravi Kumar. I am 45 years old, married with 2 children.
        I am a farmer in village Kheda, Gujarat. My annual income is around 80,000 rupees.
        I belong to OBC category. I need help finding government schemes for farmers.
        I have Aadhaar card and voter ID. I need income certificate.
        """,
        existing_profile={},
        options={"max_schemes": 5}
    )
    
    logger.info("Processing test request...")
    response = await agent_system.process_user_request(test_request)
    
    logger.info("=== TEST RESPONSE ===")
    logger.info(f"Success: {response.success}")
    logger.info(f"Processing Time: {response.processing_time_ms:.0f}ms")
    logger.info(f"Agents Used: {response.agents_involved}")
    logger.info(f"Summary: {response.summary}")
    logger.info("Recommendations:")
    for rec in response.recommendations:
        logger.info(f"  • {rec}")
    
    if response.discovered_schemes:
        logger.info("\nTop Schemes Found:")
        for scheme in response.discovered_schemes[:3]:
            logger.info(f"  • {scheme.get('name', 'Unknown')} (Score: {scheme.get('relevance_score', 0):.2f})")
    
    logger.info("\n=== SYSTEM STATUS ===")
    status = agent_system.get_system_status()
    logger.info(f"System Status: {status['status']}")
    for agent_name, agent_status in status['agents'].items():
        health = "✓" if agent_status.get('status') == 'idle' else "⚠"
        logger.info(f"  {health} {agent_name}: {agent_status.get('status', 'unknown')}")


if __name__ == "__main__":
    asyncio.run(main())