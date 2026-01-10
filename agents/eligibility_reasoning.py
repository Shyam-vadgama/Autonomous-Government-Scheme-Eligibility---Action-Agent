"""
Eligibility Reasoning Agent
Evaluates rules and determines eligibility with detailed explanations
"""
import json
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger

from agents.base_agent import BaseAgent


class EligibilityStatus(str, Enum):
    """Eligibility status enumeration"""
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    CONDITIONALLY_ELIGIBLE = "conditionally_eligible"
    INSUFFICIENT_DATA = "insufficient_data"


class EligibilityRule(BaseModel):
    """Individual eligibility rule evaluation"""
    rule_id: str
    rule_name: str
    description: str
    required_value: Any
    actual_value: Any
    status: EligibilityStatus
    reasoning: str
    weight: float = 1.0


class DocumentRequirement(BaseModel):
    """Document requirement analysis"""
    document_type: str
    required: bool = True
    available: bool = False
    alternatives: List[str] = Field(default_factory=list)
    urgency: str = "medium"  # low, medium, high
    description: str = ""


class EligibilityAssessment(BaseModel):
    """Complete eligibility assessment for a scheme"""
    scheme_id: str
    scheme_name: str
    overall_status: EligibilityStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    # Detailed rule evaluation
    passed_rules: List[EligibilityRule] = Field(default_factory=list)
    failed_rules: List[EligibilityRule] = Field(default_factory=list)
    conditional_rules: List[EligibilityRule] = Field(default_factory=list)
    
    # Document analysis
    required_documents: List[DocumentRequirement] = Field(default_factory=list)
    missing_documents: List[str] = Field(default_factory=list)
    available_documents: List[str] = Field(default_factory=list)
    
    # Action items
    immediate_actions: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    
    # Explanations
    eligibility_reasoning: str = ""
    rejection_reasoning: str = ""
    improvement_suggestions: List[str] = Field(default_factory=list)
    
    # Metadata
    assessment_date: str
    data_completeness: float = Field(ge=0.0, le=1.0)


class EligibilityReasoningAgent(BaseAgent):
    """Agent responsible for detailed eligibility evaluation and reasoning"""
    
    def __init__(self):
        super().__init__(
            agent_id="eligibility_reasoning",
            name="Eligibility Reasoning Agent",
            description="Evaluates scheme eligibility with detailed rule-based reasoning and explanations",
            capabilities=[
                "evaluate_eligibility_rules",
                "generate_rejection_reason",
                "detect_conditional_eligibility", 
                "map_required_documents",
                "provide_improvement_suggestions"
            ]
        )
        
        # Rule weights for different types of criteria
        self.rule_weights = {
            "mandatory": 1.0,
            "important": 0.8,
            "moderate": 0.6,
            "minor": 0.4
        }
        
        # Document priority levels
        self.document_priorities = {
            "identity": "high",
            "income": "high", 
            "caste": "medium",
            "residence": "medium",
            "education": "low",
            "miscellaneous": "low"
        }
    
    def get_system_prompt(self) -> str:
        """Get system prompt for eligibility reasoning"""
        return f"""You are the {self.name}, an expert AI agent that performs detailed eligibility analysis for Indian government schemes.

Your core responsibilities:
1. Evaluate each eligibility rule systematically with clear reasoning
2. Determine overall eligibility status with confidence scoring
3. Identify missing documents and suggest alternatives
4. Provide actionable recommendations for improvement
5. Generate human-readable explanations for all decisions
6. Handle edge cases and conditional eligibility scenarios

Evaluation Framework:
- ELIGIBLE: All mandatory criteria met, high confidence
- CONDITIONALLY_ELIGIBLE: Most criteria met, some conditions to fulfill
- NOT_ELIGIBLE: Fails mandatory criteria, clear rejection reasons
- INSUFFICIENT_DATA: Cannot determine due to missing information

Key Principles:
- Be thorough and systematic in rule evaluation
- Provide clear, actionable reasoning for every decision
- Consider alternative pathways for conditional eligibility
- Prioritize user education and empowerment
- Maintain accuracy while being helpful and encouraging
- Always explain what users can do to improve their eligibility

Document Analysis:
- Identify critical vs. optional documents
- Suggest alternatives where available
- Prioritize by urgency and importance
- Consider digital/online alternatives

You must provide structured, comprehensive analysis that helps users understand their situation and next steps."""
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process eligibility reasoning request"""
        try:
            user_profile = request.get("user_profile", {})
            scheme_details = request.get("scheme_details", {})
            assessment_options = request.get("options", {})
            
            if not user_profile or not scheme_details:
                return {
                    "success": False,
                    "error": "Both user profile and scheme details are required",
                    "assessment": None
                }
            
            logger.info(f"Evaluating eligibility for scheme: {scheme_details.get('name', 'Unknown')}")
            
            # Step 1: Evaluate individual rules
            rule_evaluations = await self._evaluate_eligibility_rules(user_profile, scheme_details)
            
            # Step 2: Analyze document requirements
            document_analysis = await self._analyze_document_requirements(user_profile, scheme_details)
            
            # Step 3: Determine overall eligibility
            overall_status = self._determine_overall_eligibility(rule_evaluations, document_analysis)
            
            # Step 4: Generate detailed reasoning with LLM
            detailed_reasoning = await self._generate_detailed_reasoning(
                user_profile, scheme_details, rule_evaluations, document_analysis, overall_status
            )
            
            # Step 5: Create comprehensive assessment
            assessment = self._create_comprehensive_assessment(
                scheme_details, rule_evaluations, document_analysis, overall_status, detailed_reasoning
            )
            
            return {
                "success": True,
                "assessment": assessment.dict(),
                "summary": self._generate_assessment_summary(assessment)
            }
            
        except Exception as e:
            logger.error(f"Error in eligibility reasoning: {e}")
            return {
                "success": False,
                "error": str(e),
                "assessment": None
            }
    
    async def _evaluate_eligibility_rules(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> Dict[str, List[EligibilityRule]]:
        """Evaluate individual eligibility rules"""
        criteria = scheme.get("eligibility_criteria", {})
        
        passed_rules = []
        failed_rules = []
        conditional_rules = []
        
        # Age requirements
        if "age" in criteria:
            age_rule = self._evaluate_age_rule(profile, criteria["age"])
            if age_rule.status == EligibilityStatus.ELIGIBLE:
                passed_rules.append(age_rule)
            elif age_rule.status == EligibilityStatus.CONDITIONALLY_ELIGIBLE:
                conditional_rules.append(age_rule)
            else:
                failed_rules.append(age_rule)
        
        # Income requirements
        if "annual_income" in criteria or "income_category" in criteria:
            income_rule = self._evaluate_income_rule(profile, criteria)
            if income_rule.status == EligibilityStatus.ELIGIBLE:
                passed_rules.append(income_rule)
            elif income_rule.status == EligibilityStatus.CONDITIONALLY_ELIGIBLE:
                conditional_rules.append(income_rule)
            else:
                failed_rules.append(income_rule)
        
        # Gender requirements
        if "gender" in criteria:
            gender_rule = self._evaluate_gender_rule(profile, criteria["gender"])
            if gender_rule.status == EligibilityStatus.ELIGIBLE:
                passed_rules.append(gender_rule)
            else:
                failed_rules.append(gender_rule)
        
        # Caste category requirements
        if "caste_category" in criteria:
            caste_rule = self._evaluate_caste_rule(profile, criteria["caste_category"])
            if caste_rule.status == EligibilityStatus.ELIGIBLE:
                passed_rules.append(caste_rule)
            elif caste_rule.status == EligibilityStatus.CONDITIONALLY_ELIGIBLE:
                conditional_rules.append(caste_rule)
            else:
                failed_rules.append(caste_rule)
        
        # Geographic requirements
        if "rural_urban" in criteria:
            location_rule = self._evaluate_location_rule(profile, criteria["rural_urban"])
            if location_rule.status == EligibilityStatus.ELIGIBLE:
                passed_rules.append(location_rule)
            else:
                failed_rules.append(location_rule)
        
        # Special category requirements
        special_rules = self._evaluate_special_requirements(profile, criteria)
        for rule in special_rules:
            if rule.status == EligibilityStatus.ELIGIBLE:
                passed_rules.append(rule)
            elif rule.status == EligibilityStatus.CONDITIONALLY_ELIGIBLE:
                conditional_rules.append(rule)
            else:
                failed_rules.append(rule)
        
        return {
            "passed": passed_rules,
            "failed": failed_rules,
            "conditional": conditional_rules
        }
    
    def _evaluate_age_rule(self, profile: Dict[str, Any], age_criteria: Dict[str, Any]) -> EligibilityRule:
        """Evaluate age-based eligibility rule"""
        user_age = profile.get("age", 0)
        min_age = age_criteria.get("min", 0)
        max_age = age_criteria.get("max", 150)
        
        if min_age <= user_age <= max_age:
            return EligibilityRule(
                rule_id="age_requirement",
                rule_name="Age Eligibility",
                description=f"Age must be between {min_age} and {max_age}",
                required_value=f"{min_age}-{max_age}",
                actual_value=user_age,
                status=EligibilityStatus.ELIGIBLE,
                reasoning=f"User age {user_age} is within required range {min_age}-{max_age}",
                weight=1.0
            )
        else:
            return EligibilityRule(
                rule_id="age_requirement",
                rule_name="Age Eligibility", 
                description=f"Age must be between {min_age} and {max_age}",
                required_value=f"{min_age}-{max_age}",
                actual_value=user_age,
                status=EligibilityStatus.NOT_ELIGIBLE,
                reasoning=f"User age {user_age} is outside required range {min_age}-{max_age}",
                weight=1.0
            )
    
    def _evaluate_income_rule(self, profile: Dict[str, Any], criteria: Dict[str, Any]) -> EligibilityRule:
        """Evaluate income-based eligibility rule"""
        user_income = profile.get("annual_income", 0)
        user_income_cat = profile.get("income_category", "unknown")
        
        # Check income category requirement
        if "income_category" in criteria:
            required_categories = criteria["income_category"]
            if user_income_cat in required_categories:
                return EligibilityRule(
                    rule_id="income_category",
                    rule_name="Income Category",
                    description=f"Must belong to categories: {', '.join(required_categories)}",
                    required_value=required_categories,
                    actual_value=user_income_cat,
                    status=EligibilityStatus.ELIGIBLE,
                    reasoning=f"User belongs to {user_income_cat} category which is in required list",
                    weight=1.0
                )
            else:
                return EligibilityRule(
                    rule_id="income_category",
                    rule_name="Income Category",
                    description=f"Must belong to categories: {', '.join(required_categories)}",
                    required_value=required_categories,
                    actual_value=user_income_cat,
                    status=EligibilityStatus.NOT_ELIGIBLE,
                    reasoning=f"User's {user_income_cat} category is not in required categories",
                    weight=1.0
                )
        
        # Check specific income limits
        if "annual_income" in criteria:
            income_req = criteria["annual_income"]
            max_income = income_req.get("max", float('inf'))
            min_income = income_req.get("min", 0)
            
            if min_income <= user_income <= max_income:
                return EligibilityRule(
                    rule_id="income_limit",
                    rule_name="Income Limit",
                    description=f"Annual income must be between ₹{min_income:,} and ₹{max_income:,}",
                    required_value=f"₹{min_income:,} - ₹{max_income:,}",
                    actual_value=f"₹{user_income:,}",
                    status=EligibilityStatus.ELIGIBLE,
                    reasoning=f"User income ₹{user_income:,} is within required range",
                    weight=1.0
                )
            else:
                return EligibilityRule(
                    rule_id="income_limit",
                    rule_name="Income Limit",
                    description=f"Annual income must be between ₹{min_income:,} and ₹{max_income:,}",
                    required_value=f"₹{min_income:,} - ₹{max_income:,}",
                    actual_value=f"₹{user_income:,}",
                    status=EligibilityStatus.NOT_ELIGIBLE,
                    reasoning=f"User income ₹{user_income:,} is outside required range",
                    weight=1.0
                )
        
        # Default case
        return EligibilityRule(
            rule_id="income_general",
            rule_name="Income Requirements",
            description="Income criteria evaluation",
            required_value="varies",
            actual_value=f"₹{user_income:,}",
            status=EligibilityStatus.INSUFFICIENT_DATA,
            reasoning="Insufficient data for income evaluation",
            weight=0.5
        )
    
    def _evaluate_gender_rule(self, profile: Dict[str, Any], required_gender: str) -> EligibilityRule:
        """Evaluate gender-based eligibility rule"""
        user_gender = profile.get("gender", "unknown")
        
        if user_gender == required_gender:
            return EligibilityRule(
                rule_id="gender_requirement",
                rule_name="Gender Requirement",
                description=f"Scheme is for {required_gender} applicants only",
                required_value=required_gender,
                actual_value=user_gender,
                status=EligibilityStatus.ELIGIBLE,
                reasoning=f"User gender {user_gender} matches requirement",
                weight=1.0
            )
        else:
            return EligibilityRule(
                rule_id="gender_requirement",
                rule_name="Gender Requirement",
                description=f"Scheme is for {required_gender} applicants only",
                required_value=required_gender,
                actual_value=user_gender,
                status=EligibilityStatus.NOT_ELIGIBLE,
                reasoning=f"User gender {user_gender} does not match {required_gender} requirement",
                weight=1.0
            )
    
    def _evaluate_caste_rule(self, profile: Dict[str, Any], caste_requirement: str) -> EligibilityRule:
        """Evaluate caste-based eligibility rule"""
        user_caste = profile.get("caste_category", "unknown")
        
        if user_caste == caste_requirement:
            return EligibilityRule(
                rule_id="caste_requirement",
                rule_name="Caste Category",
                description=f"Scheme is for {caste_requirement.upper()} category",
                required_value=caste_requirement,
                actual_value=user_caste,
                status=EligibilityStatus.ELIGIBLE,
                reasoning=f"User belongs to {user_caste.upper()} category as required",
                weight=1.0
            )
        elif user_caste == "unknown":
            return EligibilityRule(
                rule_id="caste_requirement",
                rule_name="Caste Category",
                description=f"Scheme is for {caste_requirement.upper()} category",
                required_value=caste_requirement,
                actual_value=user_caste,
                status=EligibilityStatus.CONDITIONALLY_ELIGIBLE,
                reasoning="Caste category not specified - needs verification with certificate",
                weight=1.0
            )
        else:
            return EligibilityRule(
                rule_id="caste_requirement",
                rule_name="Caste Category",
                description=f"Scheme is for {caste_requirement.upper()} category",
                required_value=caste_requirement,
                actual_value=user_caste,
                status=EligibilityStatus.NOT_ELIGIBLE,
                reasoning=f"User's {user_caste.upper()} category does not match {caste_requirement.upper()} requirement",
                weight=1.0
            )
    
    def _evaluate_location_rule(self, profile: Dict[str, Any], location_requirement: str) -> EligibilityRule:
        """Evaluate location-based eligibility rule"""
        user_location = profile.get("rural_urban", "unknown")
        
        if user_location == location_requirement:
            return EligibilityRule(
                rule_id="location_requirement",
                rule_name="Location Type",
                description=f"Scheme is for {location_requirement} areas only",
                required_value=location_requirement,
                actual_value=user_location,
                status=EligibilityStatus.ELIGIBLE,
                reasoning=f"User is in {user_location} area as required",
                weight=1.0
            )
        else:
            return EligibilityRule(
                rule_id="location_requirement",
                rule_name="Location Type", 
                description=f"Scheme is for {location_requirement} areas only",
                required_value=location_requirement,
                actual_value=user_location,
                status=EligibilityStatus.NOT_ELIGIBLE,
                reasoning=f"User is in {user_location} area but scheme requires {location_requirement}",
                weight=1.0
            )
    
    def _evaluate_special_requirements(self, profile: Dict[str, Any], criteria: Dict[str, Any]) -> List[EligibilityRule]:
        """Evaluate special category requirements"""
        rules = []
        
        # Farmer requirement
        if criteria.get("is_farmer", False):
            user_is_farmer = profile.get("is_farmer", False)
            rules.append(EligibilityRule(
                rule_id="farmer_requirement",
                rule_name="Farmer Status",
                description="Applicant must be a farmer",
                required_value=True,
                actual_value=user_is_farmer,
                status=EligibilityStatus.ELIGIBLE if user_is_farmer else EligibilityStatus.NOT_ELIGIBLE,
                reasoning=f"User {'is' if user_is_farmer else 'is not'} a farmer",
                weight=1.0
            ))
        
        # Disability requirement
        if criteria.get("disability_status", False):
            user_has_disability = profile.get("disability_status", False)
            rules.append(EligibilityRule(
                rule_id="disability_requirement",
                rule_name="Disability Status",
                description="Scheme is for persons with disabilities",
                required_value=True,
                actual_value=user_has_disability,
                status=EligibilityStatus.ELIGIBLE if user_has_disability else EligibilityStatus.NOT_ELIGIBLE,
                reasoning=f"User {'has' if user_has_disability else 'does not have'} disability status",
                weight=1.0
            ))
        
        # Pregnancy/lactation requirement
        if criteria.get("is_pregnant_lactating", False):
            user_is_pregnant = profile.get("is_pregnant_lactating", False)
            rules.append(EligibilityRule(
                rule_id="pregnancy_requirement",
                rule_name="Pregnancy/Lactation Status",
                description="Scheme is for pregnant/lactating women",
                required_value=True,
                actual_value=user_is_pregnant,
                status=EligibilityStatus.ELIGIBLE if user_is_pregnant else EligibilityStatus.NOT_ELIGIBLE,
                reasoning=f"User {'is' if user_is_pregnant else 'is not'} pregnant/lactating",
                weight=1.0
            ))
        
        return rules
    
    async def _analyze_document_requirements(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> Dict[str, List[DocumentRequirement]]:
        """Analyze required documents vs available documents"""
        required_docs = scheme.get("documents_required", [])
        available_docs = profile.get("available_documents", [])
        
        document_requirements = []
        missing_docs = []
        available_docs_list = []
        
        for doc in required_docs:
            is_available = doc in available_docs
            
            # Determine document category and priority
            priority = self._get_document_priority(doc)
            alternatives = self._get_document_alternatives(doc)
            
            doc_req = DocumentRequirement(
                document_type=doc,
                required=True,
                available=is_available,
                alternatives=alternatives,
                urgency=priority,
                description=self._get_document_description(doc)
            )
            
            document_requirements.append(doc_req)
            
            if is_available:
                available_docs_list.append(doc)
            else:
                missing_docs.append(doc)
        
        return {
            "requirements": document_requirements,
            "missing": missing_docs,
            "available": available_docs_list
        }
    
    def _get_document_priority(self, document: str) -> str:
        """Get priority level for a document"""
        if any(keyword in document.lower() for keyword in ["aadhaar", "identity", "voter"]):
            return "high"
        elif any(keyword in document.lower() for keyword in ["income", "caste", "domicile"]):
            return "medium"
        else:
            return "low"
    
    def _get_document_alternatives(self, document: str) -> List[str]:
        """Get alternative documents for a given document type"""
        alternatives = {
            "aadhaar_card": ["voter_id", "passport", "driving_license"],
            "income_certificate": ["salary_certificate", "tax_returns", "bank_statements"],
            "caste_certificate": ["community_certificate", "tribe_certificate"],
            "bank_account": ["passbook_copy", "bank_statement", "cancelled_cheque"],
            "age_proof": ["birth_certificate", "school_certificate", "passport"]
        }
        return alternatives.get(document, [])
    
    def _get_document_description(self, document: str) -> str:
        """Get description for a document type"""
        descriptions = {
            "aadhaar_card": "12-digit unique identity document",
            "voter_id": "Electoral identity card",
            "income_certificate": "Official certificate showing annual income",
            "caste_certificate": "Government-issued caste category certificate",
            "bank_account": "Active bank account details",
            "ration_card": "Food distribution card from PDS",
            "domicile_certificate": "Proof of residence in state/district"
        }
        return descriptions.get(document, f"Required document: {document.replace('_', ' ').title()}")
    
    def _determine_overall_eligibility(self, rule_evaluations: Dict[str, List[EligibilityRule]], document_analysis: Dict[str, List]) -> EligibilityStatus:
        """Determine overall eligibility status"""
        passed_rules = rule_evaluations["passed"]
        failed_rules = rule_evaluations["failed"]
        conditional_rules = rule_evaluations["conditional"]
        
        # If any mandatory rule fails, user is not eligible
        mandatory_failures = [r for r in failed_rules if r.weight >= 1.0]
        if mandatory_failures:
            return EligibilityStatus.NOT_ELIGIBLE
        
        # If there are conditional rules or missing important documents
        if conditional_rules or len(document_analysis["missing"]) > 0:
            return EligibilityStatus.CONDITIONALLY_ELIGIBLE
        
        # If all rules pass
        if len(passed_rules) > 0 and len(failed_rules) == 0:
            return EligibilityStatus.ELIGIBLE
        
        # Default case
        return EligibilityStatus.INSUFFICIENT_DATA
    
    async def _generate_detailed_reasoning(self, profile: Dict[str, Any], scheme: Dict[str, Any], rule_evaluations: Dict, document_analysis: Dict, overall_status: EligibilityStatus) -> Dict[str, Any]:
        """Generate detailed reasoning using LLM"""
        
        reasoning_prompt = f"""Provide detailed eligibility reasoning for this government scheme application:

SCHEME: {scheme["name"]}
DESCRIPTION: {scheme["description"]}

USER PROFILE SUMMARY:
- Age: {profile.get('age', 'Unknown')}
- Gender: {profile.get('gender', 'Unknown')}
- Income Category: {profile.get('income_category', 'Unknown')}
- Annual Income: ₹{profile.get('annual_income', 0):,}
- Caste Category: {profile.get('caste_category', 'Unknown')}
- Location: {profile.get('rural_urban', 'Unknown')}
- Occupation: {profile.get('occupation', 'Unknown')}

RULE EVALUATIONS:
Passed Rules: {len(rule_evaluations['passed'])}
Failed Rules: {len(rule_evaluations['failed'])}
Conditional Rules: {len(rule_evaluations['conditional'])}

DOCUMENT STATUS:
Missing Documents: {document_analysis['missing']}
Available Documents: {document_analysis['available']}

PRELIMINARY STATUS: {overall_status.value}

Please provide:
1. ELIGIBILITY_EXPLANATION: Clear explanation of why user is/isn't eligible
2. KEY_STRENGTHS: What aspects of their profile support eligibility
3. MAIN_CONCERNS: What aspects might prevent or delay eligibility
4. IMMEDIATE_ACTIONS: What user should do immediately
5. IMPROVEMENT_SUGGESTIONS: How user can improve their eligibility
6. CONFIDENCE_SCORE: Your confidence in this assessment (0.0-1.0)

Be encouraging and helpful while being accurate about requirements."""
        
        llm_response = await self.generate_llm_response(
            prompt=reasoning_prompt,
            structured=True,
            temperature=0.5
        )
        
        if llm_response["success"] and llm_response.get("is_structured"):
            return llm_response["structured_data"]
        else:
            # Fallback reasoning
            return {
                "eligibility_explanation": f"Assessment status: {overall_status.value}",
                "key_strengths": ["Profile analysis completed"],
                "main_concerns": ["Detailed analysis needed"],
                "immediate_actions": ["Gather required documents"],
                "improvement_suggestions": ["Complete missing profile information"],
                "confidence_score": 0.5
            }
    
    def _create_comprehensive_assessment(self, scheme: Dict[str, Any], rule_evaluations: Dict, document_analysis: Dict, overall_status: EligibilityStatus, reasoning: Dict[str, Any]) -> EligibilityAssessment:
        """Create comprehensive eligibility assessment"""
        
        return EligibilityAssessment(
            scheme_id=scheme["scheme_id"],
            scheme_name=scheme["name"],
            overall_status=overall_status,
            confidence_score=reasoning.get("confidence_score", 0.5),
            
            passed_rules=rule_evaluations["passed"],
            failed_rules=rule_evaluations["failed"],
            conditional_rules=rule_evaluations["conditional"],
            
            required_documents=document_analysis["requirements"],
            missing_documents=document_analysis["missing"],
            available_documents=document_analysis["available"],
            
            immediate_actions=reasoning.get("immediate_actions", []),
            recommended_actions=reasoning.get("improvement_suggestions", []),
            
            eligibility_reasoning=reasoning.get("eligibility_explanation", ""),
            rejection_reasoning=reasoning.get("main_concerns", ""),
            improvement_suggestions=reasoning.get("improvement_suggestions", []),
            
            assessment_date=datetime.now().date().isoformat(),
            data_completeness=self._calculate_data_completeness(rule_evaluations)
        )
    
    def _calculate_data_completeness(self, rule_evaluations: Dict) -> float:
        """Calculate data completeness score"""
        total_rules = sum(len(rules) for rules in rule_evaluations.values())
        insufficient_data_rules = len([r for r in rule_evaluations.get("conditional", []) if r.status == EligibilityStatus.INSUFFICIENT_DATA])
        
        if total_rules == 0:
            return 0.5
        
        completeness = (total_rules - insufficient_data_rules) / total_rules
        return round(completeness, 2)
    
    def _generate_assessment_summary(self, assessment: EligibilityAssessment) -> str:
        """Generate human-readable assessment summary"""
        status_messages = {
            EligibilityStatus.ELIGIBLE: "✓ You are eligible for this scheme!",
            EligibilityStatus.CONDITIONALLY_ELIGIBLE: "⚠ You may be eligible with some conditions",
            EligibilityStatus.NOT_ELIGIBLE: "✗ You are not currently eligible for this scheme",
            EligibilityStatus.INSUFFICIENT_DATA: "? Need more information to determine eligibility"
        }
        
        summary = f"Eligibility Assessment for {assessment.scheme_name}\n\n"
        summary += f"Status: {status_messages[assessment.overall_status]}\n"
        summary += f"Confidence: {assessment.confidence_score*100:.0f}%\n\n"
        
        if assessment.passed_rules:
            summary += f"✓ Passed {len(assessment.passed_rules)} eligibility criteria\n"
        
        if assessment.failed_rules:
            summary += f"✗ Failed {len(assessment.failed_rules)} requirements\n"
        
        if assessment.missing_documents:
            summary += f"📄 Missing {len(assessment.missing_documents)} documents\n"
        
        if assessment.immediate_actions:
            summary += f"\nNext Steps:\n"
            for action in assessment.immediate_actions[:3]:
                summary += f"• {action}\n"
        
        return summary