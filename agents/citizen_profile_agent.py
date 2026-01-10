"""
Citizen Profile Agent
Extracts structured citizen data (Student/Farmer) using Gemini
"""
import json
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from google.genai import types

from agents.base_agent import BaseAgent

# Define the system prompt based on user requirements
SYSTEM_PROMPT = """
You are a highly efficient "Citizen Data Extraction Agent." Your sole purpose is to listen to user descriptions and extract key demographic and socioeconomic variables into a structured JSON format.

### Common Fields (Extract for everyone):
- name: (String)
- user_type: (Strictly 'student' or 'farmer')
- age: (Integer)
- gender: (Male/Female/Other)
- state: (e.g., Gujarat)
- district: (e.g., Gandhinagar)
- income_range: (e.g., 0-2.5L)
- category: (SC, ST, OBC, General)
- minority: (Boolean)
- disability: (Boolean)

### Student Specific Fields (Only if user_type is 'student'):
- education_level: (String, e.g., '10th', 'Diploma', 'Undergraduate')
- course_name: (String)
- stream: (String, e.g., 'Science', 'Arts')
- institution_name: (String)
- institution_type: (String, e.g., 'Government', 'Private')
- year_of_study: (Integer)
- previous_year_marks_percent: (Float)
- is_hosteller: (Boolean)

### Farmer Specific Fields (Only if user_type is 'farmer'):
- owns_land: (Boolean)
- land_area_acres: (Float)
- main_crops: (String, comma-separated)
- irrigation_source: (String)
- has_farmer_id: (Boolean)
- has_livestock: (Boolean)

### Rules:
1. First, identify the 'user_type'.
2. If a value is missing for the identified type, set it to null.
3. Do NOT extract student fields for farmers, and vice versa.
4. Output ONLY valid JSON.
"""

class CitizenProfileAgent(BaseAgent):
    """
    Agent responsible for extracting structured citizen profile data
    Specializes in Student and Farmer profiles
    """
    
    def __init__(self):
        super().__init__(
            agent_id="citizen_profile_extractor",
            name="Citizen Data Extraction Agent",
            description="Extracts key demographic and socioeconomic variables into a structured JSON format",
            capabilities=[
                "extract_student_data",
                "extract_farmer_data", 
                "identify_user_type"
            ]
        )
    
    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process profile extraction request"""
        try:
            user_input = request.get("user_input", "")
            existing_profile = request.get("existing_profile", {})
            
            logger.info(f"Processing citizen data extraction for: {user_input[:50]}...")
            
            # Combine existing profile context if needed
            full_input = user_input
            if existing_profile:
                full_input += f"\nContext from previous: {json.dumps(existing_profile)}"
            
            # Use the LLM to extract data
            try:
                response = self.llm_client.client.models.generate_content(
                    model=self.llm_client.config.model_name,
                    contents=full_input,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.1,
                        top_p=0.95,
                        top_k=64,
                        max_output_tokens=8192,
                        response_mime_type="application/json"
                    )
                )
                data = json.loads(response.text)
                
                # Handle case where LLM returns a list instead of a dict
                if isinstance(data, list):
                    if len(data) > 0:
                        data = data[0]
                    else:
                        data = {}
            except Exception as e:
                error_str = str(e)
                logger.error(f"Gemini API Error: {error_str}")
                
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    return {
                        "success": False,
                        "error": "AI Quota Exhausted. The free tier limit (20-1500 requests/day) has been reached. Please wait a while or switch to a different API key.",
                        "profile": existing_profile or {"name": "User (Quota Limited)"},
                        "next_question": "I'm sorry, but I've hit my daily limit for AI analysis. Please try again later today."
                    }
                
                # Fallback to basic extraction if possible, or just error
                return {
                    "success": False,
                    "error": f"AI Extraction Failed: {error_str}",
                    "profile": existing_profile,
                    "next_question": "There was an error connecting to the AI service. Please check your internet connection."
                }

            # Post-processing (similar to the user's script)
            if "missing_fields" in data:
                del data["missing_fields"]
                
            # Define base expected fields
            base_fields = [
                "name", "user_type", "age", "gender", "state", "district", 
                "income_range", "category", "minority", "disability"
            ]
            
            # Define type-specific fields
            student_fields = [
                "education_level", "course_name", "stream", "institution_name",
                "institution_type", "year_of_study", "previous_year_marks_percent", "is_hosteller"
            ]
            
            farmer_fields = [
                "owns_land", "land_area_acres", "main_crops", "irrigation_source",
                "has_farmer_id", "has_livestock"
            ]

            expected_fields = list(base_fields)

            # Determine user_type to expand expected fields
            user_type = data.get("user_type")
            
            if user_type == "student":
                expected_fields.extend(student_fields)
            elif user_type == "farmer":
                expected_fields.extend(farmer_fields)
            else:
                # If unknown type, we minimally expect the base fields + type clarification
                pass

            # Ensure all expected keys exist in data, set to None if missing
            for field in expected_fields:
                if field not in data:
                    data[field] = None

            # Identify missing fields (for UI feedback)
            missing_fields = [k for k, v in data.items() if v is None and k in expected_fields]
            
            # Calculate Completion Percentage
            total_fields = len(expected_fields)
            filled_fields = total_fields - len(missing_fields)
            completion_percentage = int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
            
            # Generate Next Question
            next_question = None
            if missing_fields:
                if not user_type:
                    next_question = "Could you please tell me if you are a Student or a Farmer?"
                else:
                    # Generate a natural question for missing fields
                    # We'll ask for top 3 missing fields to avoid overwhelming the user
                    priority_missing = missing_fields[:3]
                    question_prompt = f"""
                    You are a helpful government scheme assistant.
                    The user is a {user_type}.
                    We need the following details to complete their profile: {', '.join(priority_missing)}.
                    Draft a polite, conversational question to ask the user for this information.
                    Keep it short and encouraging.
                    """
                    try:
                        q_response = self.llm_client.client.models.generate_content(
                            model=self.llm_client.config.model_name,
                            contents=question_prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.7,
                                max_output_tokens=100
                            )
                        )
                        next_question = q_response.text.strip()
                    except Exception as e:
                        logger.warning(f"Failed to generate question: {e}")
                        next_question = f"Please provide your {', '.join(priority_missing).replace('_', ' ')}."
            else:
                next_question = "Your profile is complete! We can now find the best schemes for you."

            # Normalize for system compatibility (SchemeDiscoveryAgent)
            normalized_profile = self._normalize_for_system(data)
            
            # Merge normalized data with raw data
            # We keep the raw data structure but ensure key fields for other agents are present
            final_profile = {**normalized_profile, **data}
            
            return {
                "success": True,
                "profile": final_profile,
                "user_type": user_type,
                "missing_fields": missing_fields,
                "completion_percentage": completion_percentage,
                "next_question": next_question,
                "confidence_score": 0.9 if not missing_fields else 0.5
            }
                
        except Exception as e:
            logger.error(f"Error extracting citizen data: {e}")
            return {
                "success": False,
                "error": str(e),
                "profile": None
            }

    def _normalize_for_system(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize extracted data for compatibility with other agents"""
        normalized = {}
        
        # Normalize category -> caste_category
        category_map = {
            "sc": "sc", "scheduled caste": "sc",
            "st": "st", "scheduled tribe": "st",
            "obc": "obc", "other backward class": "obc",
            "general": "general", "gen": "general"
        }
        raw_cat = str(data.get("category", "")).lower()
        normalized["caste_category"] = category_map.get(raw_cat, "general")
        
        # Normalize income
        # income_range is e.g. "0-2.5L"
        # We need annual_income (float) and income_category (bpl/apl)
        income_range = str(data.get("income_range", ""))
        annual_income = 100000.0 # Default
        
        try:
            # Simple heuristic parsing
            if "0-2.5" in income_range or "2.5" in income_range:
                annual_income = 125000.0
            elif "2.5-5" in income_range:
                annual_income = 375000.0
            elif "bpl" in income_range.lower():
                annual_income = 20000.0
            
            # If user didn't specify, we might default or try to parse numbers
            nums = re.findall(r"(\d+\.?\d*)", income_range)
            if nums:
                # Assuming Lakhs if small numbers
                val = float(nums[0])
                if val < 100: 
                    annual_income = val * 100000
                else:
                    annual_income = val
        except:
            pass
            
        normalized["annual_income"] = annual_income
        
        # Income category logic (same as ProfileAnalyzer)
        if annual_income <= 12000:
            normalized["income_category"] = "bpl" # Very low
        elif annual_income <= 8000:
             normalized["income_category"] = "aay"
        elif annual_income <= 200000:
            normalized["income_category"] = "bpl" # Using higher threshold for BPL mapping effectively for schemes often
        else:
            normalized["income_category"] = "apl"
            
        # Is Farmer
        normalized["is_farmer"] = (data.get("user_type") == "farmer")
        
        # Disability
        normalized["disability_status"] = bool(data.get("disability"))
        
        # Gender
        normalized["gender"] = str(data.get("gender", "male")).lower() # Default male if missing
        
        # Age
        try:
            normalized["age"] = int(data.get("age", 30))
        except:
            normalized["age"] = 30
            
        # Occupation
        if data.get("user_type") == "farmer":
            normalized["occupation"] = "Farmer"
            normalized["employment_status"] = "self_employed"
        elif data.get("user_type") == "student":
            normalized["occupation"] = "Student"
            normalized["employment_status"] = "student"
        else:
            normalized["occupation"] = "Unknown"
            normalized["employment_status"] = "unemployed"
            
        return normalized