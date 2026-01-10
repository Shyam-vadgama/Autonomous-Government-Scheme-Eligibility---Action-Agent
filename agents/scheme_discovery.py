"""
Scheme Discovery Agent
Finds potentially applicable government schemes based on user profile
"""
import json
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field
from loguru import logger

from agents.base_agent import BaseAgent
from data.schemes_db import GOVERNMENT_SCHEMES


class SchemeMatch(BaseModel):
    """Represents a matched scheme with relevance score"""
    scheme_id: str
    name: str
    category: str
    description: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    matching_criteria: List[str] = Field(default_factory=list)
    potential_benefits: Dict[str, Any] = Field(default_factory=dict)
    confidence_level: str = "medium"  # low, medium, high
    
    
class SchemeDiscoveryResult(BaseModel):
    """Result of scheme discovery process"""
    total_schemes_found: int
    highly_relevant: List[SchemeMatch] = Field(default_factory=list)  # score >= 0.7
    moderately_relevant: List[SchemeMatch] = Field(default_factory=list)  # 0.4 <= score < 0.7
    low_relevance: List[SchemeMatch] = Field(default_factory=list)  # score < 0.4
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)


class SchemeDiscoveryAgent(BaseAgent):
    """Agent responsible for discovering relevant government schemes"""
    
    def __init__(self):
        super().__init__(
            agent_id="scheme_discovery",
            name="Scheme Discovery Agent", 
            description="Discovers relevant government schemes based on user profile analysis",
            capabilities=[
                "query_scheme_db",
                "score_scheme_relevance", 
                "exclude_irrelevant_schemes",
                "categorize_by_relevance",
                "semantic_scheme_matching"
            ]
        )
        
        self.schemes_database = self._load_schemes_from_json()
        
        self.category_weights = {
            "exact_match": 1.0,
            "high_priority": 0.8,
            "moderate_priority": 0.6,
            "low_priority": 0.3,
            "demographic_match": 0.7,
            "geographic_match": 0.5
        }

    def _load_schemes_from_json(self) -> List[Dict[str, Any]]:
        """Load schemes from schemes.json or fallback to static DB"""
        try:
            import os
            json_path = "schemes.json"
            if os.path.exists(json_path):
                with open(json_path, "r", encoding='utf-8') as f:
                    raw_schemes = json.load(f)
                
                logger.info(f"Loaded {len(raw_schemes)} schemes from {json_path}")
                
                # Convert to internal format
                processed = []
                for i, s in enumerate(raw_schemes):
                    processed.append({
                        "scheme_id": f"json_{i}",
                        "name": s.get("title", "Unknown Scheme"),
                        "category": s.get("target_audience", "General"),
                        "description": s.get("snippet", ""),
                        "benefits": {"description": s.get("snippet", "")},
                        "eligibility_criteria": {
                            "text_description": s.get("eligibility", "")
                        },
                        "target_groups": [s.get("target_audience", "").lower()],
                        # Preserve original text fields for string searching
                        "target_audience": s.get("target_audience", ""),
                        "eligibility": s.get("eligibility", ""),
                        "source_url": s.get("link", ""),
                        "apply_link": s.get("apply_link", "")
                    })
                return processed
        except Exception as e:
            logger.error(f"Failed to load schemes.json: {e}")
        
        # Fallback
        logger.info("Using fallback GOVERNMENT_SCHEMES database")
        from data.schemes_db import GOVERNMENT_SCHEMES
        return GOVERNMENT_SCHEMES
    
    def get_system_prompt(self) -> str:
        """Get system prompt for scheme discovery"""
        return f"""You are the {self.name}, an expert AI agent specialized in discovering relevant Indian government schemes based on user profiles.

Your responsibilities:
1. Analyze user profiles to identify applicable scheme categories
2. Match user characteristics with scheme eligibility criteria
3. Score scheme relevance based on multiple factors
4. Prioritize schemes by potential impact and accessibility
5. Provide reasoning for scheme recommendations

Key Matching Factors:
- Economic status (BPL/APL/income levels)
- Social category (SC/ST/OBC/General)
- Geographic location (state, rural/urban)
- Demographic factors (age, gender, family composition)
- Occupation and employment status
- Education level
- Special circumstances (disability, pregnancy, etc.)

Scoring Guidelines:
- Exact eligibility match: 0.8-1.0
- Partial match with high relevance: 0.6-0.8
- Moderate relevance: 0.4-0.6
- Low relevance: 0.2-0.4
- No relevance: 0.0-0.2

You should provide detailed reasoning for each scheme match and exclude clearly irrelevant schemes."""
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process scheme discovery request"""
        try:
            user_profile = request.get("user_profile", {})
            discovery_options = request.get("options", {})
            
            logger.info(f"Processing scheme discovery for user profile...")
            
            if not user_profile:
                return {
                    "success": False,
                    "error": "User profile is required for scheme discovery",
                    "results": None
                }
            
            # Step 1: Filter schemes by basic eligibility
            eligible_schemes = await self._filter_eligible_schemes(user_profile)
            
            # Step 2: Score relevance for each eligible scheme
            scored_schemes = await self._score_scheme_relevance(user_profile, eligible_schemes)
            
            # Step 3: Get LLM-enhanced analysis for top schemes
            enhanced_schemes = await self._enhance_with_llm_analysis(user_profile, scored_schemes)
            
            # Step 4: Categorize results by relevance
            categorized_results = self._categorize_by_relevance(enhanced_schemes)
            
            discovery_result = SchemeDiscoveryResult(
                total_schemes_found=len(enhanced_schemes),
                highly_relevant=categorized_results["high"],
                moderately_relevant=categorized_results["medium"], 
                low_relevance=categorized_results["low"],
                processing_metadata={
                    "schemes_analyzed": len(self.schemes_database),
                    "eligible_after_filter": len(eligible_schemes),
                    "final_scored": len(enhanced_schemes),
                    "processing_time": "calculated_later"
                }
            )
            
            return {
                "success": True,
                "results": discovery_result.dict(),
                "summary": self._generate_discovery_summary(discovery_result)
            }
            
        except Exception as e:
            logger.error(f"Error in scheme discovery: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": None
            }
    
    async def _filter_eligible_schemes(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter schemes by basic eligibility criteria"""
        eligible_schemes = []
        
        # User Type Enforcement (Student vs Farmer)
        user_type = user_profile.get("user_type", "").lower()
        
        for scheme in self.schemes_database:
            # Category-based filtering logic
            if user_type == "student":
                # If student, exclude explicit farmer schemes
                # Include student schemes and general schemes
                if self._is_farmer_scheme(scheme) and not self._is_student_scheme(scheme):
                    continue
                
            elif user_type == "farmer":
                # If farmer, exclude explicit student schemes
                if self._is_student_scheme(scheme) and not self._is_farmer_scheme(scheme):
                    continue
            
            if self._check_basic_eligibility(user_profile, scheme):
                eligible_schemes.append(scheme)
        
        logger.info(f"Found {len(eligible_schemes)} potentially eligible schemes")
        return eligible_schemes

    def _is_student_scheme(self, scheme: Dict[str, Any]) -> bool:
        """Check if scheme is targeted at students"""
        keywords = ["student", "education", "internship", "youth", "scholarship", "university", "college", "degree", "school"]
        text = (scheme.get("target_audience", "") + " " + scheme.get("eligibility", "") + " " + scheme.get("title", "") + " " + scheme.get("name", "")).lower()
        return any(k in text for k in keywords)

    def _is_farmer_scheme(self, scheme: Dict[str, Any]) -> bool:
        """Check if scheme is targeted at farmers"""
        keywords = ["farmer", "agriculture", "crop", "land", "rural", "kisan", "harvest", "tractor", "seed", "fertilizer"]
        text = (scheme.get("target_audience", "") + " " + scheme.get("eligibility", "") + " " + scheme.get("title", "") + " " + scheme.get("name", "")).lower()
        return any(k in text for k in keywords)
    
    def _check_basic_eligibility(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> bool:
        """Check if user meets basic eligibility for a scheme"""
        criteria = scheme.get("eligibility_criteria", {})
        
        # If criteria is just text (from JSON), we rely on relevance scoring and earlier filtering
        if "text_description" in criteria and len(criteria) == 1:
            return True

        # Check mandatory exclusions first
        exclusions = criteria.get("exclusions", [])
        if "government_employees" in exclusions and profile.get("employment_status") == "government":
            return False
        if "income_tax_payers" in exclusions and profile.get("annual_income", 0) > 500000:
            return False
        
        # Check positive criteria
        
        # Age requirements
        if "age" in criteria:
            user_age = profile.get("age", 0)
            age_req = criteria["age"]
            if isinstance(age_req, dict):
                if "min" in age_req and user_age < age_req["min"]:
                    return False
                if "max" in age_req and user_age > age_req["max"]:
                    return False
        
        # Gender requirements
        if "gender" in criteria:
            if criteria["gender"] != profile.get("gender"):
                return False
        
        # Income category requirements
        if "income_category" in criteria:
            user_income_cat = profile.get("income_category")
            if user_income_cat not in criteria["income_category"]:
                return False
        
        # Income limits
        if "annual_income" in criteria:
            income_req = criteria["annual_income"]
            user_income = profile.get("annual_income", 0)
            if isinstance(income_req, dict):
                if "max" in income_req and user_income > income_req["max"]:
                    return False
                if "min" in income_req and user_income < income_req["min"]:
                    return False
        
        # Rural/Urban requirements
        if "rural_urban" in criteria:
            if criteria["rural_urban"] != profile.get("rural_urban"):
                return False
        
        # Special requirements
        if criteria.get("is_farmer", False) and not profile.get("is_farmer", False):
            return False
        if criteria.get("disability_status", False) and not profile.get("disability_status", False):
            return False
        if criteria.get("is_pregnant_lactating", False) and not profile.get("is_pregnant_lactating", False):
            return False
        
        return True
    
    async def _score_scheme_relevance(self, profile: Dict[str, Any], schemes: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], float]]:
        """Score relevance of each scheme for the user"""
        scored_schemes = []
        
        for scheme in schemes:
            score = self._calculate_relevance_score(profile, scheme)
            scored_schemes.append((scheme, score))
        
        # Sort by relevance score (highest first)
        scored_schemes.sort(key=lambda x: x[1], reverse=True)
        return scored_schemes
    
    def _calculate_relevance_score(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> float:
        """Calculate relevance score for a scheme"""
        score = 0.0
        max_score = 0.0
        
        criteria = scheme.get("eligibility_criteria", {})
        
        # Handle schemes from JSON (simple text criteria)
        if "text_description" in criteria and len(criteria) == 1:
            # Fallback to simple keyword scoring
            max_score = 1.0
            score = 0.5 # Base score
            
            # Boost if category/audience matches user type
            user_type = profile.get("user_type", "").lower()
            scheme_target = scheme.get("target_audience", "").lower()
            
            if user_type == "student" and "student" in scheme_target:
                score += 0.3
            if user_type == "farmer" and ("farmer" in scheme_target or "agri" in scheme_target or "rural" in scheme_target):
                score += 0.3
            
            return min(1.0, score)

        # ... rest of the original scoring logic ...
        # Income category match (high weight)
        max_score += 0.25
        if "income_category" in criteria:
            user_income_cat = profile.get("income_category")
            if user_income_cat in criteria["income_category"]:
                if user_income_cat == "bpl":
                    score += 0.25  # BPL gets full points
                elif user_income_cat == "aay":
                    score += 0.25  # AAY gets full points
                else:
                    score += 0.15  # APL gets partial points
        
        # Social category match (medium weight)
        max_score += 0.2
        target_groups = scheme.get("target_groups", [])
        user_caste = profile.get("caste_category", "")
        if user_caste in ["sc", "st", "obc"] and any(cat in target_groups for cat in ["sc_students", "st_welfare"]):
            score += 0.2
        elif "general" in target_groups:
            score += 0.1
        
        # Demographics match (medium weight)
        max_score += 0.2
        user_age = profile.get("age", 0)
        user_gender = profile.get("gender", "")
        
        # Age-specific schemes
        if user_age >= 60 and "senior_citizens" in target_groups:
            score += 0.2
        elif 18 <= user_age <= 35 and "youth" in target_groups:
            score += 0.15
        elif user_age < 18 and "children" in target_groups:
            score += 0.15
        
        # Gender-specific schemes
        if user_gender == "female" and any("women" in tg or "maternal" in tg for tg in target_groups):
            score += 0.1
        
        # Occupation match (medium weight)  
        max_score += 0.15
        user_occupation = profile.get("occupation", "").lower()
        scheme_category = scheme.get("category", "").lower()
        
        if "farmer" in user_occupation and "agriculture" in scheme_category:
            score += 0.15
        elif profile.get("is_farmer", False) and "agriculture" in scheme_category:
            score += 0.15
        elif "employment" in scheme_category and profile.get("employment_status") == "unemployed":
            score += 0.12
        
        # Special circumstances (high weight)
        max_score += 0.2
        if profile.get("disability_status") and "disability" in scheme_category:
            score += 0.2
        if profile.get("is_pregnant_lactating") and "maternal" in scheme_category:
            score += 0.2
        if profile.get("is_woman_head") and "women" in target_groups:
            score += 0.15
        
        # Normalize score
        if max_score > 0:
            normalized_score = min(1.0, score / max_score)
        else:
            normalized_score = 0.5  # Default moderate score
        
        return round(normalized_score, 3)
    
    async def _enhance_with_llm_analysis(self, profile: Dict[str, Any], scored_schemes: List[Tuple[Dict[str, Any], float]]) -> List[SchemeMatch]:
        """Enhance top schemes with LLM analysis"""
        enhanced_schemes = []
        
        # Take top 10 schemes for LLM analysis
        top_schemes = scored_schemes[:10]
        
        for scheme, base_score in top_schemes:
            try:
                # Create analysis prompt
                analysis_prompt = self._create_scheme_analysis_prompt(profile, scheme, base_score)
                
                # Get LLM analysis
                llm_response = await self.generate_llm_response(
                    prompt=analysis_prompt,
                    structured=True,
                    temperature=0.4
                )
                
                if llm_response["success"] and llm_response.get("is_structured"):
                    llm_data = llm_response["structured_data"]
                    
                    # Create enhanced scheme match
                    scheme_match = SchemeMatch(
                        scheme_id=scheme["scheme_id"],
                        name=scheme["name"],
                        category=scheme["category"],
                        description=scheme["description"],
                        relevance_score=llm_data.get("adjusted_relevance_score", base_score),
                        matching_criteria=llm_data.get("matching_criteria", []),
                        potential_benefits=llm_data.get("potential_benefits", scheme.get("benefits", {})),
                        confidence_level=llm_data.get("confidence_level", "medium")
                    )
                    
                    enhanced_schemes.append(scheme_match)
                else:
                    # Fallback: create basic scheme match
                    scheme_match = SchemeMatch(
                        scheme_id=scheme["scheme_id"],
                        name=scheme["name"],
                        category=scheme["category"],
                        description=scheme["description"],
                        relevance_score=base_score,
                        matching_criteria=self._extract_basic_criteria(profile, scheme),
                        potential_benefits=scheme.get("benefits", {}),
                        confidence_level="medium"
                    )
                    enhanced_schemes.append(scheme_match)
                    
            except Exception as e:
                logger.warning(f"Error enhancing scheme {scheme.get('name')}: {e}")
                # Create basic scheme match as fallback
                scheme_match = SchemeMatch(
                    scheme_id=scheme["scheme_id"],
                    name=scheme["name"],
                    category=scheme["category"],
                    description=scheme["description"],
                    relevance_score=base_score,
                    matching_criteria=["basic_eligibility"],
                    potential_benefits=scheme.get("benefits", {}),
                    confidence_level="low"
                )
                enhanced_schemes.append(scheme_match)
        
        # Add remaining schemes without LLM enhancement
        for scheme, base_score in scored_schemes[10:]:
            scheme_match = SchemeMatch(
                scheme_id=scheme["scheme_id"],
                name=scheme["name"], 
                category=scheme["category"],
                description=scheme["description"],
                relevance_score=base_score,
                matching_criteria=["basic_filter"],
                potential_benefits=scheme.get("benefits", {}),
                confidence_level="low"
            )
            enhanced_schemes.append(scheme_match)
        
        return enhanced_schemes
    
    def _create_scheme_analysis_prompt(self, profile: Dict[str, Any], scheme: Dict[str, Any], base_score: float) -> str:
        """Create prompt for LLM scheme analysis"""
        return f"""Analyze the relevance of this government scheme for the given user profile:

USER PROFILE:
{json.dumps(profile, indent=2)}

SCHEME DETAILS:
Name: {scheme["name"]}
Category: {scheme["category"]}
Description: {scheme["description"]}
Benefits: {json.dumps(scheme.get("benefits", {}), indent=2)}
Eligibility: {json.dumps(scheme.get("eligibility_criteria", {}), indent=2)}
Target Groups: {scheme.get("target_groups", [])}

CURRENT RELEVANCE SCORE: {base_score}

Please analyze and provide:

1. ADJUSTED_RELEVANCE_SCORE (0.0-1.0): Refine the relevance score considering:
   - User's specific circumstances
   - Scheme's potential impact on user's life
   - Accessibility and ease of application
   - Priority level for this user

2. MATCHING_CRITERIA: List specific criteria that the user matches

3. POTENTIAL_BENEFITS: Quantify specific benefits for this user

4. CONFIDENCE_LEVEL: Your confidence in this match (low/medium/high)

5. REASONING: Detailed explanation of your analysis

Respond in JSON format with these fields."""
    
    def _extract_basic_criteria(self, profile: Dict[str, Any], scheme: Dict[str, Any]) -> List[str]:
        """Extract basic matching criteria for fallback"""
        criteria = []
        
        # Income category
        scheme_income_cats = scheme.get("eligibility_criteria", {}).get("income_category", [])
        if profile.get("income_category") in scheme_income_cats:
            criteria.append(f"income_category_{profile.get('income_category')}")
        
        # Age
        if "age" in scheme.get("eligibility_criteria", {}):
            criteria.append("age_eligible")
        
        # Gender
        if scheme.get("eligibility_criteria", {}).get("gender") == profile.get("gender"):
            criteria.append(f"gender_{profile.get('gender')}")
        
        # Special categories
        if profile.get("is_farmer") and scheme.get("eligibility_criteria", {}).get("is_farmer"):
            criteria.append("farmer_category")
        
        if profile.get("disability_status") and "disability" in scheme.get("category", ""):
            criteria.append("disability_status")
        
        return criteria or ["basic_eligibility"]
    
    def _categorize_by_relevance(self, schemes: List[SchemeMatch]) -> Dict[str, List[SchemeMatch]]:
        """Categorize schemes by relevance score"""
        high_relevance = [s for s in schemes if s.relevance_score >= 0.7]
        medium_relevance = [s for s in schemes if 0.4 <= s.relevance_score < 0.7]
        low_relevance = [s for s in schemes if s.relevance_score < 0.4]
        
        return {
            "high": high_relevance,
            "medium": medium_relevance, 
            "low": low_relevance
        }
    
    def _generate_discovery_summary(self, result: SchemeDiscoveryResult) -> str:
        """Generate a summary of discovery results"""
        high_count = len(result.highly_relevant)
        medium_count = len(result.moderately_relevant)
        low_count = len(result.low_relevance)
        
        summary = f"Scheme Discovery Summary:\n"
        summary += f"- Found {result.total_schemes_found} relevant schemes\n"
        summary += f"- Highly relevant: {high_count} schemes\n"
        summary += f"- Moderately relevant: {medium_count} schemes\n"
        summary += f"- Low relevance: {low_count} schemes\n"
        
        if high_count > 0:
            top_scheme = result.highly_relevant[0]
            summary += f"\nTop recommendation: {top_scheme.name} (Score: {top_scheme.relevance_score})"
        
        return summary