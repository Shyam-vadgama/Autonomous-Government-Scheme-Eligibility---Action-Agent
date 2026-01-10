"""
Profile Analyzer Agent
Converts raw user input into structured data for government scheme eligibility analysis
"""
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from loguru import logger

from agents.base_agent import BaseAgent


class UserProfile(BaseModel):
    """Structured user profile model"""
    # Personal Information
    name: str
    age: int
    gender: str  # 'male', 'female', 'other'
    marital_status: str  # 'single', 'married', 'divorced', 'widowed'
    
    # Geographic Information
    state: str
    district: str
    village_city: Optional[str] = None
    pin_code: Optional[str] = None
    rural_urban: str  # 'rural', 'urban', 'semi_urban'
    
    # Economic Information
    annual_income: float
    income_category: str  # 'bpl', 'apl', 'aay'  # Below/Above Poverty Line, Antyodaya Anna Yojana
    occupation: str
    employment_status: str  # 'employed', 'unemployed', 'self_employed', 'retired'
    
    # Social Information
    caste_category: str  # 'general', 'obc', 'sc', 'st'
    minority_status: Optional[str] = None  # 'muslim', 'christian', 'sikh', etc.
    disability_status: bool = False
    disability_type: Optional[str] = None
    
    # Educational Information
    education_level: str  # 'illiterate', 'primary', 'secondary', 'graduate', 'postgraduate'
    
    # Family Information
    family_size: int
    dependents: int
    children_count: int
    elderly_dependents: int
    
    # Documents Available
    available_documents: List[str] = Field(default_factory=list)
    
    # Special Categories
    is_farmer: bool = False
    is_woman_head: bool = False
    is_senior_citizen: bool = False
    is_pregnant_lactating: bool = False
    
    # Additional metadata
    profile_completed: bool = True
    missing_fields: List[str] = Field(default_factory=list)
    confidence_score: float = 1.0


class ProfileAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing and structuring user profile data"""
    
    def __init__(self):
        super().__init__(
            agent_id="profile_analyzer",
            name="Profile Analyzer Agent",
            description="Converts raw user input into structured profile data for scheme eligibility analysis",
            capabilities=[
                "normalize_profile_data",
                "detect_missing_fields", 
                "logical_inference",
                "data_validation",
                "profile_completion_scoring"
            ]
        )
        
        # Define income categories and thresholds
        self.income_thresholds = {
            "bpl": 12000,  # Below Poverty Line (annual)
            "apl": 200000,  # Above Poverty Line threshold
            "aay": 8000,   # Antyodaya Anna Yojana (extremely poor)
        }
        
        # Define common documents
        self.common_documents = [
            "aadhaar_card", "voter_id", "pan_card", "ration_card", 
            "income_certificate", "caste_certificate", "domicile_certificate",
            "bank_account", "passport", "driving_license"
        ]
    
    def get_system_prompt(self) -> str:
        """Get system prompt for profile analysis"""
        return f"""You are the {self.name}, a specialized AI agent responsible for analyzing user profile data for government scheme eligibility.

Your primary responsibilities:
1. Extract and structure personal, geographic, economic, and social information from user input
2. Infer missing information using logical reasoning when possible
3. Identify missing critical fields that need user clarification
4. Normalize and validate data according to Indian government standards
5. Categorize users according to government scheme eligibility criteria

Key Guidelines:
- Use standard Indian government categories (BPL/APL, SC/ST/OBC/General, etc.)
- Infer reasonable defaults when information is incomplete but don't assume sensitive data
- Always maintain data accuracy and flag uncertainties
- Consider regional variations in scheme availability
- Respect privacy and handle sensitive information appropriately

Income Categories:
- BPL (Below Poverty Line): Annual income < ₹12,000
- AAY (Antyodaya): Annual income < ₹8,000 (extremely poor)
- APL (Above Poverty Line): Annual income > ₹12,000

You must respond in a structured JSON format that can be parsed and validated."""
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process profile analysis request"""
        try:
            user_input = request.get("user_input", "")
            existing_profile = request.get("existing_profile", {})
            
            logger.info(f"Processing profile analysis for input: {user_input[:100]}...")
            
            # Generate structured analysis
            analysis_prompt = self._create_analysis_prompt(user_input, existing_profile)
            
            # Define the response schema for structured output
            profile_schema = {
                "name": "string",
                "age": "integer", 
                "occupation": "string",
                "annual_income": "integer",
                "state": "string",
                "category": "string", 
                "documents": "array",
                "family_size": "integer",
                "confidence_score": "number",
                "missing_fields": "array"
            }
            
            llm_response = await self.generate_llm_response(
                prompt=analysis_prompt,
                structured=True,
                response_schema=profile_schema,
                temperature=0.3  # Lower temperature for more consistent data extraction
            )
            
            if not llm_response.get("success"):
                return {
                    "success": False,
                    "error": f"LLM analysis failed: {llm_response.get('error')}",
                    "profile": None
                }
            
            # Parse the response - it should be in the response field
            response_data = llm_response.get("response") or llm_response
            
            # If response_data is a dict with profile fields, use it directly
            if isinstance(response_data, dict) and "name" in response_data:
                profile_data = response_data
            elif isinstance(response_data, str):
                # Try to parse as JSON
                try:
                    import json
                    profile_data = json.loads(response_data)
                except:
                    # Fallback: try to extract data from unstructured response
                    fallback_profile = await self._fallback_extraction(response_data)
                    return {
                        "success": True,
                        "profile": fallback_profile.dict(),
                        "confidence_score": fallback_profile.confidence_score,
                        "missing_fields": fallback_profile.missing_fields,
                        "warning": "Used fallback extraction method"
                    }
            else:
                # Use response data as is
                profile_data = response_data
            
            # Validate and enhance the profile
            validated_profile = await self._validate_and_enhance_profile(profile_data)
            
            return {
                "success": True,
                "profile": validated_profile.dict(),
                "confidence_score": validated_profile.confidence_score,
                "missing_fields": validated_profile.missing_fields
            }
                
        except Exception as e:
            logger.error(f"Error processing profile request: {e}")
            return {
                "success": False,
                "error": str(e),
                "profile": None
            }
    
    def _create_analysis_prompt(self, user_input: str, existing_profile: Dict[str, Any]) -> str:
        """Create prompt for profile analysis"""
        return f"""Analyze the following user information and extract a structured profile for government scheme eligibility:

USER INPUT:
{user_input}

EXISTING PROFILE DATA:
{json.dumps(existing_profile, indent=2) if existing_profile else "None"}

Your task is to extract and structure the following information:

1. PERSONAL INFORMATION:
   - Name, age, gender, marital status

2. GEOGRAPHIC INFORMATION:
   - State, district, village/city, pin code, rural/urban classification

3. ECONOMIC INFORMATION:
   - Annual income, occupation, employment status
   - Income category (BPL/APL/AAY based on income thresholds)

4. SOCIAL INFORMATION:
   - Caste category (General/OBC/SC/ST)
   - Minority status, disability information

5. EDUCATIONAL INFORMATION:
   - Education level achieved

6. FAMILY INFORMATION:
   - Family size, dependents, children count

7. SPECIAL CATEGORIES:
   - Is farmer, woman head of family, senior citizen, pregnant/lactating

8. AVAILABLE DOCUMENTS:
   - List any mentioned identity/income/caste documents

INSTRUCTIONS:
- Use logical inference to fill gaps where reasonable
- Mark fields as missing if no reasonable inference is possible
- Calculate income category based on annual income
- Assign confidence scores (0.0-1.0) based on data completeness
- Use standard government terminology

Respond with a JSON object containing all extracted data and metadata."""
    
    async def _validate_and_enhance_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """Validate and enhance the extracted profile data"""
        try:
            # Extract profile fields with defaults
            profile_fields = {}
            
            # Personal Information
            profile_fields["name"] = profile_data.get("name", "").strip()
            profile_fields["age"] = int(profile_data.get("age", 0))
            profile_fields["gender"] = self._normalize_gender(profile_data.get("gender", ""))
            profile_fields["marital_status"] = self._normalize_marital_status(profile_data.get("marital_status", ""))
            
            # Geographic Information
            profile_fields["state"] = profile_data.get("state", "").strip()
            profile_fields["district"] = profile_data.get("district", "").strip()
            profile_fields["village_city"] = profile_data.get("village_city")
            profile_fields["pin_code"] = profile_data.get("pin_code")
            profile_fields["rural_urban"] = self._normalize_area_type(profile_data.get("rural_urban", ""))
            
            # Economic Information
            profile_fields["annual_income"] = float(profile_data.get("annual_income", 0))
            profile_fields["income_category"] = self._determine_income_category(profile_fields["annual_income"])
            profile_fields["occupation"] = profile_data.get("occupation", "").strip()
            profile_fields["employment_status"] = self._normalize_employment_status(profile_data.get("employment_status", ""))
            
            # Social Information
            profile_fields["caste_category"] = self._normalize_caste_category(profile_data.get("caste_category", ""))
            profile_fields["minority_status"] = profile_data.get("minority_status")
            profile_fields["disability_status"] = bool(profile_data.get("disability_status", False))
            profile_fields["disability_type"] = profile_data.get("disability_type")
            
            # Educational Information
            profile_fields["education_level"] = self._normalize_education_level(profile_data.get("education_level", ""))
            
            # Family Information
            profile_fields["family_size"] = int(profile_data.get("family_size", 1))
            profile_fields["dependents"] = int(profile_data.get("dependents", 0))
            profile_fields["children_count"] = int(profile_data.get("children_count", 0))
            profile_fields["elderly_dependents"] = int(profile_data.get("elderly_dependents", 0))
            
            # Documents
            profile_fields["available_documents"] = profile_data.get("available_documents", [])
            
            # Special Categories
            profile_fields["is_farmer"] = bool(profile_data.get("is_farmer", False))
            profile_fields["is_woman_head"] = bool(profile_data.get("is_woman_head", False))
            profile_fields["is_senior_citizen"] = profile_fields["age"] >= 60
            profile_fields["is_pregnant_lactating"] = bool(profile_data.get("is_pregnant_lactating", False))
            
            # Calculate missing fields and confidence
            missing_fields = self._identify_missing_fields(profile_fields)
            confidence_score = self._calculate_confidence_score(profile_fields, missing_fields)
            
            profile_fields["missing_fields"] = missing_fields
            profile_fields["confidence_score"] = confidence_score
            profile_fields["profile_completed"] = len(missing_fields) == 0
            
            return UserProfile(**profile_fields)
            
        except Exception as e:
            logger.error(f"Error validating profile data: {e}")
            # Return minimal profile with error indication
            return UserProfile(
                name="Unknown",
                age=0,
                gender="unknown",
                marital_status="unknown",
                state="Unknown",
                district="Unknown",
                rural_urban="unknown",
                annual_income=0.0,
                income_category="unknown",
                occupation="Unknown",
                employment_status="unknown",
                caste_category="unknown",
                education_level="unknown",
                family_size=1,
                dependents=0,
                children_count=0,
                elderly_dependents=0,
                confidence_score=0.0,
                missing_fields=["all_fields"],
                profile_completed=False
            )
    
    async def _fallback_extraction(self, raw_response: str) -> UserProfile:
        """Fallback method to extract profile from unstructured response"""
        # Basic extraction using regex and keywords
        # This is a simplified fallback - in production, this would be more sophisticated
        
        profile_data = {}
        
        # Try to extract basic information using simple patterns
        age_match = re.search(r'age[:\s]+(\d+)', raw_response.lower())
        if age_match:
            profile_data["age"] = int(age_match.group(1))
        
        income_match = re.search(r'income[:\s]+(\d+)', raw_response.lower())
        if income_match:
            profile_data["annual_income"] = float(income_match.group(1))
        
        # Default values for required fields
        return UserProfile(
            name="Unknown",
            age=profile_data.get("age", 0),
            gender="unknown",
            marital_status="unknown", 
            state="Unknown",
            district="Unknown",
            rural_urban="unknown",
            annual_income=profile_data.get("annual_income", 0.0),
            income_category="unknown",
            occupation="Unknown",
            employment_status="unknown",
            caste_category="unknown",
            education_level="unknown",
            family_size=1,
            dependents=0,
            children_count=0,
            elderly_dependents=0,
            confidence_score=0.2,  # Low confidence for fallback
            missing_fields=["most_fields"],
            profile_completed=False
        )
    
    def _normalize_gender(self, gender: str) -> str:
        """Normalize gender values"""
        gender = gender.lower().strip()
        if gender in ["m", "male", "man"]:
            return "male"
        elif gender in ["f", "female", "woman"]:
            return "female"
        elif gender in ["o", "other", "transgender", "trans"]:
            return "other"
        return "unknown"
    
    def _normalize_marital_status(self, status: str) -> str:
        """Normalize marital status"""
        status = status.lower().strip()
        if status in ["single", "unmarried"]:
            return "single"
        elif status in ["married"]:
            return "married"
        elif status in ["divorced"]:
            return "divorced"
        elif status in ["widowed", "widow"]:
            return "widowed"
        return "unknown"
    
    def _normalize_area_type(self, area_type: str) -> str:
        """Normalize rural/urban classification"""
        area_type = area_type.lower().strip()
        if area_type in ["rural", "village"]:
            return "rural"
        elif area_type in ["urban", "city"]:
            return "urban"
        elif area_type in ["semi_urban", "town"]:
            return "semi_urban"
        return "unknown"
    
    def _determine_income_category(self, annual_income: float) -> str:
        """Determine income category based on thresholds"""
        if annual_income <= self.income_thresholds["aay"]:
            return "aay"
        elif annual_income <= self.income_thresholds["bpl"]:
            return "bpl"
        elif annual_income <= self.income_thresholds["apl"]:
            return "apl"
        else:
            return "above_apl"
    
    def _normalize_employment_status(self, status: str) -> str:
        """Normalize employment status"""
        status = status.lower().strip()
        if status in ["employed", "working", "job"]:
            return "employed"
        elif status in ["unemployed", "jobless"]:
            return "unemployed"
        elif status in ["self_employed", "business", "self-employed"]:
            return "self_employed"
        elif status in ["retired"]:
            return "retired"
        return "unknown"
    
    def _normalize_caste_category(self, category: str) -> str:
        """Normalize caste category"""
        category = category.lower().strip()
        if category in ["general", "gen"]:
            return "general"
        elif category in ["obc", "other backward class"]:
            return "obc"
        elif category in ["sc", "scheduled caste"]:
            return "sc"
        elif category in ["st", "scheduled tribe"]:
            return "st"
        return "unknown"
    
    def _normalize_education_level(self, level: str) -> str:
        """Normalize education level"""
        level = level.lower().strip()
        if level in ["illiterate", "no education"]:
            return "illiterate"
        elif level in ["primary", "1-5", "elementary"]:
            return "primary"
        elif level in ["secondary", "high school", "6-12"]:
            return "secondary"
        elif level in ["graduate", "bachelor", "degree"]:
            return "graduate"
        elif level in ["postgraduate", "master", "phd"]:
            return "postgraduate"
        return "unknown"
    
    def _identify_missing_fields(self, profile_fields: Dict[str, Any]) -> List[str]:
        """Identify missing or incomplete profile fields"""
        missing = []
        
        required_fields = {
            "name": str,
            "age": int,
            "state": str,
            "district": str,
            "annual_income": float,
            "occupation": str
        }
        
        for field, field_type in required_fields.items():
            value = profile_fields.get(field)
            if not value or (field_type == str and value.strip() == "") or (field_type in [int, float] and value <= 0):
                missing.append(field)
        
        return missing
    
    def _calculate_confidence_score(self, profile_fields: Dict[str, Any], missing_fields: List[str]) -> float:
        """Calculate confidence score based on completeness"""
        total_important_fields = 20  # Approximate number of important fields
        missing_count = len(missing_fields)
        
        # Base score from completeness
        completeness_score = max(0, (total_important_fields - missing_count) / total_important_fields)
        
        # Adjust for data quality
        quality_adjustments = 0
        
        # Check for unknown/default values
        unknown_values = [
            profile_fields.get("gender") == "unknown",
            profile_fields.get("caste_category") == "unknown",
            profile_fields.get("education_level") == "unknown",
            profile_fields.get("employment_status") == "unknown"
        ]
        
        quality_adjustments = sum(unknown_values) * 0.05  # Reduce by 5% per unknown value
        
        final_score = max(0.0, completeness_score - quality_adjustments)
        return round(final_score, 2)