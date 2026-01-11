"""
Action Planner Agent
Creates detailed, step-by-step action plans for scheme applications
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from loguru import logger

from agents.base_agent import BaseAgent


class ActionPriority(str, Enum):
    """Priority levels for action steps"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionStatus(str, Enum):
    """Status of action steps"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    OPTIONAL = "optional"


class ActionStep(BaseModel):
    """Individual action step in the application plan"""
    step_id: str
    title: str
    description: str
    category: str  # 'document', 'application', 'verification', 'follow_up'
    priority: ActionPriority
    estimated_time: str  # e.g., "30 minutes", "2-3 days"
    estimated_cost: float = 0.0
    
    # Dependencies and sequencing
    depends_on: List[str] = Field(default_factory=list)  # Other step IDs
    can_parallel: bool = True  # Can be done in parallel with other steps
    
    # Detailed instructions
    detailed_instructions: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    online_resources: List[str] = Field(default_factory=list)
    offline_locations: List[str] = Field(default_factory=list)
    
    # Contact information
    helpline_numbers: List[str] = Field(default_factory=list)
    email_contacts: List[str] = Field(default_factory=list)
    
    # Timing and deadlines
    suggested_start_date: Optional[str] = None
    expected_completion: Optional[str] = None
    deadline: Optional[str] = None
    
    # Status tracking
    status: ActionStatus = ActionStatus.NOT_STARTED
    completion_notes: str = ""
    
    # Tips and warnings
    helpful_tips: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    fallback_options: List[str] = Field(default_factory=list)


class ActionPlan(BaseModel):
    """Complete action plan for scheme application"""
    plan_id: str
    scheme_id: str
    scheme_name: str
    user_id: Optional[str] = None
    
    # Plan overview
    total_steps: int
    estimated_total_time: str
    estimated_total_cost: float
    success_probability: float = Field(ge=0.0, le=1.0)
    
    # Steps categorized
    critical_steps: List[ActionStep] = Field(default_factory=list)
    high_priority_steps: List[ActionStep] = Field(default_factory=list) 
    medium_priority_steps: List[ActionStep] = Field(default_factory=list)
    optional_steps: List[ActionStep] = Field(default_factory=list)
    
    # Timeline
    suggested_timeline: str
    key_milestones: List[Dict[str, str]] = Field(default_factory=list)
    
    # Preparation phase
    preparation_checklist: List[str] = Field(default_factory=list)
    
    # Risk assessment
    potential_challenges: List[str] = Field(default_factory=list)
    mitigation_strategies: List[str] = Field(default_factory=list)
    
    # Success factors
    success_tips: List[str] = Field(default_factory=list)
    
    # Follow-up actions
    post_application_steps: List[ActionStep] = Field(default_factory=list)
    
    # Metadata
    created_date: str
    last_updated: str
    plan_version: str = "1.0"


class ActionPlannerAgent(BaseAgent):
    """Agent responsible for creating detailed action plans for scheme applications"""
    
    def __init__(self):
        super().__init__(
            agent_id="action_planner",
            name="Action Planner Agent",
            description="Creates comprehensive, step-by-step action plans for government scheme applications",
            capabilities=[
                "generate_action_steps",
                "resolve_step_priority", 
                "merge_common_steps",
                "estimate_effort",
                "create_timeline",
                "identify_dependencies"
            ]
        )
        
        # Step templates for common document types
        self.document_step_templates = {
            "aadhaar_card": {
                "title": "Obtain Aadhaar Card",
                "description": "Get or update your Aadhaar card",
                "category": "document",
                "estimated_time": "1-2 weeks",
                "online_resources": ["https://uidai.gov.in"],
                "instructions": [
                    "Visit nearest Aadhaar enrollment center",
                    "Carry required documents (birth certificate, address proof)",
                    "Complete biometric enrollment",
                    "Collect acknowledgment receipt",
                    "Download Aadhaar after 90 days"
                ]
            },
            "income_certificate": {
                "title": "Obtain Income Certificate", 
                "description": "Get official income certificate from competent authority",
                "category": "document",
                "estimated_time": "1-2 weeks",
                "instructions": [
                    "Visit Tehsildar/SDM office",
                    "Submit application with required documents",
                    "Pay prescribed fees",
                    "Collect certificate after verification"
                ]
            }
        }
        
        # Common application processes
        self.application_templates = {
            "online_portal": {
                "title": "Submit Online Application",
                "instructions": [
                    "Register on official portal",
                    "Fill application form carefully",
                    "Upload required documents",
                    "Pay application fees if any",
                    "Submit and save application number"
                ]
            },
            "offline_submission": {
                "title": "Submit Physical Application",
                "instructions": [
                    "Download and fill application form",
                    "Attach required document copies",
                    "Visit designated office during working hours",
                    "Submit form and collect receipt"
                ]
            }
        }
    
    def get_system_prompt(self) -> str:
        """Get system prompt for action planning"""
        return f"""You are the {self.name}, an expert AI agent specialized in creating detailed, actionable plans for Indian government scheme applications.

Your core responsibilities:
1. Break down the application process into clear, manageable steps
2. Prioritize steps based on criticality and dependencies
3. Provide realistic time and cost estimates
4. Create parallel tracks where possible to reduce total time
5. Include detailed instructions and helpful resources
6. Anticipate common challenges and provide solutions
7. Ensure compliance with official procedures

Key Planning Principles:
- Make plans actionable and specific
- Consider user's current situation and constraints
- Provide both online and offline alternatives
- Include verification and follow-up steps
- Account for processing delays and waiting times
- Offer tips to avoid common mistakes
- Provide fallback options for each critical step

Step Categories:
- CRITICAL: Must be completed for eligibility
- HIGH: Important for smooth processing  
- MEDIUM: Helpful but not essential
- OPTIONAL: Additional benefits or conveniences

Timeline Considerations:
- Document preparation: 1-4 weeks
- Application submission: 1-2 days  
- Processing time: 2-8 weeks (varies by scheme)
- Verification: 1-3 weeks
- Approval/Disbursement: 1-4 weeks

You should create comprehensive yet practical plans that empower users to successfully navigate the application process."""
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process action planning request"""
        try:
            scheme_details = request.get("scheme_details", {})
            eligibility_assessment = request.get("eligibility_assessment", {})
            user_profile = request.get("user_profile", {})
            planning_options = request.get("options", {})
            
            if not scheme_details:
                return {
                    "success": False,
                    "error": "Scheme details are required for action planning",
                    "action_plan": None
                }
            
            logger.info(f"Creating action plan for scheme: {scheme_details.get('name', 'Unknown')}")
            
            # Step 1: Analyze current situation and requirements
            situation_analysis = await self._analyze_current_situation(
                user_profile, scheme_details, eligibility_assessment
            )
            
            # Step 2: Generate document preparation steps
            document_steps = await self._generate_document_steps(
                scheme_details, user_profile, eligibility_assessment
            )
            
            # Step 3: Generate application process steps  
            application_steps = await self._generate_application_steps(
                scheme_details, situation_analysis
            )
            
            # Step 4: Generate verification and follow-up steps
            followup_steps = await self._generate_followup_steps(
                scheme_details, situation_analysis
            )
            
            # Step 5: Create comprehensive plan with LLM enhancement
            enhanced_plan = await self._create_comprehensive_plan(
                scheme_details, document_steps, application_steps, followup_steps, situation_analysis
            )
            
            return {
                "success": True,
                "action_plan": enhanced_plan.dict(),
                "summary": self._generate_plan_summary(enhanced_plan)
            }
            
        except Exception as e:
            logger.error(f"Error in action planning: {e}")
            return {
                "success": False,
                "error": str(e),
                "action_plan": None
            }
    
    async def _analyze_current_situation(self, profile: Dict[str, Any], scheme: Dict[str, Any], assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current situation to inform planning"""
        
        # User readiness factors
        available_docs = profile.get("available_documents", [])
        missing_docs = assessment.get("missing_documents", [])
        eligibility_status = assessment.get("overall_status", "unknown")
        
        # Scheme complexity factors
        required_docs = scheme.get("documents_required", [])
        application_process = scheme.get("application_process", "unknown")
        
        # Calculate readiness score
        doc_readiness = len(available_docs) / max(len(required_docs), 1) if required_docs else 1.0
        overall_readiness = doc_readiness * 0.7 + (1.0 if eligibility_status == "eligible" else 0.3) * 0.3
        
        return {
            "user_readiness_score": overall_readiness,
            "missing_documents_count": len(missing_docs),
            "critical_missing_docs": missing_docs,
            "available_documents_count": len(available_docs),
            "eligibility_status": eligibility_status,
            "scheme_complexity": len(required_docs),
            "application_method": application_process,
            "estimated_preparation_weeks": max(1, len(missing_docs) // 2),
            "user_location_type": profile.get("rural_urban", "unknown")
        }
    
    async def _generate_document_steps(self, scheme: Dict[str, Any], profile: Dict[str, Any], assessment: Dict[str, Any]) -> List[ActionStep]:
        """Generate steps for document preparation"""
        steps = []
        step_counter = 1
        
        required_docs = scheme.get("documents_required", [])
        available_docs = profile.get("available_documents", [])
        missing_docs = [doc for doc in required_docs if doc not in available_docs]
        
        # Create steps for missing documents
        for doc in missing_docs:
            template = self.document_step_templates.get(doc, {})
            
            step = ActionStep(
                step_id=f"doc_{step_counter:02d}",
                title=template.get("title", f"Obtain {doc.replace('_', ' ').title()}"),
                description=template.get("description", f"Obtain required document: {doc.replace('_', ' ').title()}"),
                category="document",
                priority=self._determine_document_priority(doc),
                estimated_time=template.get("estimated_time", "1-2 weeks"),
                estimated_cost=self._estimate_document_cost(doc),
                detailed_instructions=template.get("instructions", [f"Visit concerned office to obtain {doc.replace('_', ' ')}"]),
                online_resources=template.get("online_resources", []),
                offline_locations=self._get_offline_locations_for_doc(doc, profile),
                helpful_tips=self._get_document_tips(doc),
                common_mistakes=self._get_common_mistakes(doc),
                suggested_start_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            steps.append(step)
            step_counter += 1
        
        # Add document verification step if there are any documents to prepare
        if missing_docs:
            verify_step = ActionStep(
                step_id=f"doc_{step_counter:02d}",
                title="Verify All Documents",
                description="Ensure all documents are complete and valid",
                category="verification",
                priority=ActionPriority.HIGH,
                estimated_time="1-2 hours",
                detailed_instructions=[
                    "Check all documents for clarity and completeness",
                    "Make photocopies of all documents", 
                    "Get photocopies attested if required",
                    "Organize documents in application sequence"
                ],
                depends_on=[f"doc_{i:02d}" for i in range(1, step_counter)]
            )
            steps.append(verify_step)
        
        return steps
    
    async def _generate_application_steps(self, scheme: Dict[str, Any], situation: Dict[str, Any]) -> List[ActionStep]:
        """Generate application submission steps"""
        steps = []
        application_method = scheme.get("application_process", "unknown")
        
        # Step 1: Prepare application
        prep_step = ActionStep(
            step_id="app_01",
            title="Prepare Application Form",
            description="Complete the official application form accurately",
            category="application",
            priority=ActionPriority.CRITICAL,
            estimated_time="1-2 hours",
            detailed_instructions=[
                "Download official application form from government website",
                "Read instructions carefully before filling",
                "Fill form in clear handwriting or type if online",
                "Ensure all mandatory fields are completed",
                "Double-check all information for accuracy"
            ],
            online_resources=[scheme.get("official_website", "")],
            helpful_tips=[
                "Use block letters for handwritten forms",
                "Keep a copy of filled form for records",
                "Have someone review before submission"
            ]
        )
        steps.append(prep_step)
        
        # Step 2: Submit application
        if "online" in application_method.lower():
            submit_step = ActionStep(
                step_id="app_02",
                title="Submit Online Application",
                description="Submit application through official online portal",
                category="application",
                priority=ActionPriority.CRITICAL,
                estimated_time="30-60 minutes",
                detailed_instructions=[
                    "Create account on official portal if required",
                    "Upload scanned copies of all documents (PDF format, <2MB each)",
                    "Fill online form carefully",
                    "Review all information before final submission",
                    "Pay fees online if applicable",
                    "Save/print application acknowledgment receipt"
                ],
                depends_on=["app_01"],
                helpful_tips=[
                    "Use good quality scanner for documents",
                    "Submit during business hours for immediate confirmation",
                    "Keep application number safe"
                ],
                common_mistakes=[
                    "Uploading unclear document scans",
                    "Not saving acknowledgment receipt",
                    "Submitting with incomplete information"
                ]
            )
        else:
            submit_step = ActionStep(
                step_id="app_02", 
                title="Submit Physical Application",
                description="Submit application at designated government office",
                category="application",
                priority=ActionPriority.CRITICAL,
                estimated_time="2-4 hours",
                detailed_instructions=[
                    "Visit designated office during working hours",
                    "Take all original documents and photocopies",
                    "Submit application form with attachments",
                    "Pay fees if applicable and collect receipt",
                    "Collect acknowledgment receipt with application number"
                ],
                depends_on=["app_01"],
                offline_locations=self._get_submission_locations(scheme),
                helpful_tips=[
                    "Visit early in the day to avoid queues",
                    "Carry extra photocopies",
                    "Dress appropriately for government office"
                ]
            )
        
        steps.append(submit_step)
        
        return steps
    
    async def _generate_followup_steps(self, scheme: Dict[str, Any], situation: Dict[str, Any]) -> List[ActionStep]:
        """Generate verification and follow-up steps"""
        steps = []
        
        # Track application status
        track_step = ActionStep(
            step_id="follow_01",
            title="Track Application Status",
            description="Monitor application processing status regularly",
            category="follow_up",
            priority=ActionPriority.MEDIUM,
            estimated_time="5 minutes daily",
            detailed_instructions=[
                "Check application status online using application number",
                "Note any status updates or additional requirements",
                "Respond promptly to any queries from officials",
                "Keep application number and receipts handy"
            ],
            suggested_start_date=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            online_resources=[scheme.get("official_website", "")],
            helpful_tips=[
                "Check status every 2-3 days",
                "Set reminders to follow up",
                "Maintain communication log"
            ]
        )
        steps.append(track_step)
        
        # Attend verification if required
        verification_step = ActionStep(
            step_id="follow_02",
            title="Attend Verification Process",
            description="Participate in document/field verification if called",
            category="verification",
            priority=ActionPriority.HIGH,
            estimated_time="2-4 hours",
            estimated_cost=50.0,  # Travel costs
            detailed_instructions=[
                "Respond to verification notice promptly",
                "Carry all original documents",
                "Be available at specified date and time",
                "Answer questions honestly and clearly",
                "Collect verification completion receipt"
            ],
            status=ActionStatus.OPTIONAL,  # Only if called
            helpful_tips=[
                "Inform office if you need to reschedule",
                "Carry identity proof additionally",
                "Be polite and cooperative with officials"
            ]
        )
        steps.append(verification_step)
        
        # Receive benefits
        receive_step = ActionStep(
            step_id="follow_03", 
            title="Receive Scheme Benefits",
            description="Collect approved benefits or set up recurring payments",
            category="completion",
            priority=ActionPriority.HIGH,
            estimated_time="1-2 hours",
            detailed_instructions=[
                "Check for approval notification",
                "Update bank account details if required",
                "Collect benefit distribution card if applicable",
                "Understand ongoing compliance requirements"
            ],
            helpful_tips=[
                "Ensure bank account is active and operational",
                "Keep approval letter safe for future reference",
                "Understand renewal requirements if any"
            ]
        )
        steps.append(receive_step)
        
        return steps
    
    async def _create_comprehensive_plan(self, scheme: Dict[str, Any], doc_steps: List[ActionStep], app_steps: List[ActionStep], follow_steps: List[ActionStep], situation: Dict[str, Any]) -> ActionPlan:
        """Create comprehensive action plan with LLM enhancement"""
        
        all_steps = doc_steps + app_steps + follow_steps
        
        # Categorize steps by priority
        critical_steps = [s for s in all_steps if s.priority == ActionPriority.CRITICAL]
        high_steps = [s for s in all_steps if s.priority == ActionPriority.HIGH]
        medium_steps = [s for s in all_steps if s.priority == ActionPriority.MEDIUM]
        optional_steps = [s for s in all_steps if s.priority == ActionPriority.LOW or s.status == ActionStatus.OPTIONAL]
        
        # Calculate estimates
        total_time_weeks = situation.get("estimated_preparation_weeks", 2) + 4  # +4 for processing
        total_cost = sum(step.estimated_cost for step in all_steps)
        success_prob = min(0.9, situation.get("user_readiness_score", 0.5) + 0.3)
        
        # Generate enhanced plan using LLM
        enhancement_prompt = self._create_plan_enhancement_prompt(scheme, all_steps, situation)
        
        llm_response = await self.generate_llm_response(
            prompt=enhancement_prompt,
            structured=True,
            temperature=0.4
        )
        
        # Extract LLM enhancements
        if llm_response["success"] and llm_response.get("is_structured"):
            enhancements = llm_response["structured_data"]
        else:
            enhancements = self._create_default_enhancements(scheme, situation)
        
        # Create final plan
        plan = ActionPlan(
            plan_id=f"plan_{scheme['scheme_id']}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            scheme_id=scheme["scheme_id"],
            scheme_name=scheme["name"],
            
            total_steps=len(all_steps),
            estimated_total_time=f"{total_time_weeks} weeks",
            estimated_total_cost=total_cost,
            success_probability=success_prob,
            
            critical_steps=critical_steps,
            high_priority_steps=high_steps,
            medium_priority_steps=medium_steps,
            optional_steps=optional_steps,
            
            suggested_timeline=enhancements.get("timeline", f"{total_time_weeks} weeks total"),
            key_milestones=enhancements.get("milestones", []),
            
            preparation_checklist=enhancements.get("preparation_checklist", []),
            potential_challenges=enhancements.get("challenges", []),
            mitigation_strategies=enhancements.get("mitigation", []),
            success_tips=enhancements.get("success_tips", []),
            
            post_application_steps=follow_steps,
            
            created_date=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
        return plan
    
    def _determine_document_priority(self, document: str) -> ActionPriority:
        """Determine priority level for a document"""
        high_priority_docs = ["aadhaar_card", "voter_id", "income_certificate", "caste_certificate"]
        medium_priority_docs = ["bank_account", "domicile_certificate", "ration_card"]
        
        if document in high_priority_docs:
            return ActionPriority.CRITICAL
        elif document in medium_priority_docs:
            return ActionPriority.HIGH
        else:
            return ActionPriority.MEDIUM
    
    def _estimate_document_cost(self, document: str) -> float:
        """Estimate cost for obtaining a document"""
        costs = {
            "aadhaar_card": 0.0,  # Free
            "voter_id": 0.0,      # Free
            "income_certificate": 50.0,
            "caste_certificate": 100.0,
            "domicile_certificate": 50.0,
            "bank_account": 0.0,  # Usually free
            "ration_card": 30.0
        }
        return costs.get(document, 25.0)  # Default cost
    
    def _get_offline_locations_for_doc(self, document: str, profile: Dict[str, Any]) -> List[str]:
        """Get offline locations for document procurement"""
        locations = {
            "aadhaar_card": ["Post Office", "Bank branches", "CSC centers"],
            "income_certificate": ["Tehsildar Office", "SDM Office", "District Collectorate"],
            "caste_certificate": ["Tehsildar Office", "SDM Office"],
            "voter_id": ["Election Office", "Collector Office"],
            "bank_account": ["Nearest bank branch", "Post office"]
        }
        return locations.get(document, ["District Collectorate", "Local government office"])
    
    def _get_document_tips(self, document: str) -> List[str]:
        """Get helpful tips for document procurement"""
        tips = {
            "aadhaar_card": [
                "Enrollment is free, don't pay touts",
                "Carry multiple address proofs",
                "Update mobile number for OTP"
            ],
            "income_certificate": [
                "Apply early as it takes time",
                "Get employer certificate for salaried persons",
                "Keep income tax returns ready"
            ],
            "caste_certificate": [
                "Original caste certificate of parent required",
                "Ensure proper attestation",
                "Check validity period"
            ]
        }
        return tips.get(document, ["Carry all required documents", "Apply in person", "Keep photocopies"])
    
    def _get_common_mistakes(self, document: str) -> List[str]:
        """Get common mistakes to avoid"""
        mistakes = {
            "aadhaar_card": [
                "Not updating address after moving",
                "Providing wrong mobile number",
                "Not keeping enrollment ID safe"
            ],
            "income_certificate": [
                "Applying too close to deadline", 
                "Inconsistent income declarations",
                "Missing employer signature"
            ]
        }
        return mistakes.get(document, ["Incomplete application", "Missing signatures", "Unclear photocopies"])
    
    def _get_submission_locations(self, scheme: Dict[str, Any]) -> List[str]:
        """Get locations for scheme application submission"""
        return [
            "District Collectorate",
            "Tehsildar Office", 
            "Block Development Office",
            "Panchayat Office (for rural areas)"
        ]
    
    def _create_plan_enhancement_prompt(self, scheme: Dict[str, Any], steps: List[ActionStep], situation: Dict[str, Any]) -> str:
        """Create prompt for LLM plan enhancement"""
        return f"""Enhance this action plan for the government scheme application:

SCHEME: {scheme["name"]}
TOTAL STEPS: {len(steps)}
USER READINESS: {situation.get("user_readiness_score", 0.5):.2f}
LOCATION TYPE: {situation.get("user_location_type", "unknown")}

Please provide enhancements in the following areas:

1. TIMELINE: Realistic timeline with phases
2. MILESTONES: Key checkpoints and deadlines  
3. PREPARATION_CHECKLIST: Things to prepare before starting
4. CHALLENGES: Potential obstacles user might face
5. MITIGATION: Strategies to overcome challenges
6. SUCCESS_TIPS: Expert tips for successful application

Consider:
- User's location (rural/urban access differences)
- Seasonal factors that might affect processing
- Alternative approaches if primary method fails
- Efficiency improvements to reduce total time

Provide practical, actionable advice that helps users succeed."""
    
    def _create_default_enhancements(self, scheme: Dict[str, Any], situation: Dict[str, Any]) -> Dict[str, Any]:
        """Create default enhancements if LLM fails"""
        return {
            "timeline": "4-6 weeks total (2 weeks prep, 4 weeks processing)",
            "milestones": [
                {"week": "1", "milestone": "Gather all documents"},
                {"week": "2", "milestone": "Submit application"},
                {"week": "4", "milestone": "Verification complete"},
                {"week": "6", "milestone": "Receive benefits"}
            ],
            "preparation_checklist": [
                "Gather all identity documents",
                "Obtain income/caste certificates", 
                "Open bank account if needed",
                "Research application process"
            ],
            "challenges": [
                "Document delays",
                "Office visit requirements",
                "Verification delays"
            ],
            "mitigation": [
                "Start document collection early",
                "Keep multiple copies ready",
                "Follow up regularly"
            ],
            "success_tips": [
                "Be patient with government processes",
                "Keep all receipts and acknowledgments",
                "Follow official guidelines strictly"
            ]
        }
    
    def _generate_plan_summary(self, plan: ActionPlan) -> str:
        """Generate human-readable plan summary"""
        summary = f"Action Plan for {plan.scheme_name}\n\n"
        summary += f"📊 Plan Overview:\n"
        summary += f"• Total Steps: {plan.total_steps}\n"
        summary += f"• Estimated Time: {plan.estimated_total_time}\n"
        summary += f"• Estimated Cost: ₹{plan.estimated_total_cost:,.0f}\n"
        summary += f"• Success Probability: {plan.success_probability*100:.0f}%\n\n"
        
        summary += f"🔥 Critical Steps ({len(plan.critical_steps)}):\n"
        for step in plan.critical_steps[:3]:  # Show top 3
            summary += f"• {step.title}\n"
        
        if len(plan.critical_steps) > 3:
            summary += f"• ... and {len(plan.critical_steps) - 3} more\n"
        
        summary += f"\n⏱ Key Milestones:\n"
        for milestone in plan.key_milestones[:3]:
            summary += f"• Week {milestone.get('week')}: {milestone.get('milestone')}\n"
        
        summary += f"\n💡 Top Success Tips:\n"
        for tip in plan.success_tips[:2]:
            summary += f"• {tip}\n"
        
        return summary