from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import logging
import uvicorn

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agentic-mapper")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Profile Data
PROFILE_DATA = {
    "name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+15550199",
    "address": "123 Tech Street, Silicon Valley, CA",
    "education": "Master of Computer Science, Stanford University",
    "experience": "10 years as Senior Full Stack Engineer",
    "skills": "Python, React, FastApi, Chrome Extensions, AI Agents",
    "linkedin": "https://linkedin.com/in/johndoe",
    "portfolio": "https://johndoe.dev",
    "category": "OBC",
    "annual_income": "80,000",
    "occupation": "Farmer",
    "state": "Gujarat",
    "district": "Kheda",
    "village": "Kheda",
    "marital_status": "Married",
    "children": "2",
    "id_proof": "Aadhaar Card, Voter ID",
}

class FormField(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    label: Optional[str] = None
    placeholder: Optional[str] = None
    type: str = "text"

class MapRequest(BaseModel):
    fields: List[FormField]

# --- Agentic Mapping Logic ---

class BaseMapper(ABC):
    @abstractmethod
    def map_field(self, field: FormField, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Returns { "value": str, "confidence": float, "reasoning": str } or None"""
        pass

class DeterministicMapper(BaseMapper):
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        # Synonyms and mapping rules
        self.rules = {
            "name": ["full name", "fullname", "candidate name", "your name", "name"],
            "first_name": ["first", "fname", "given name"],
            "last_name": ["last", "lname", "surname", "family name"],
            "email": ["email", "mail", "e-mail", "email address"],
            "phone": ["phone", "mobile", "contact", "cell", "telephone", "contact_number"],
            "address": ["address", "residence", "location", "city", "state", "street"],
            "education": ["education", "university", "college", "degree", "highest qualification", "school"],
            "experience": ["experience", "years of experience", "work history", "employment", "tenure"],
            "skills": ["skills", "technologies", "tech stack", "competencies", "expertise"],
            "linkedin": ["linkedin", "linkedin profile", "linkedin url"],
            "portfolio": ["portfolio", "website", "personal site", "url", "homepage"],
            "category": ["category", "caste", "social category", "community"],
            "annual_income": ["income", "annual income", "salary", "earnings"],
            "occupation": ["occupation", "profession", "work", "job", "farmer"],
            "state": ["state", "province", "region"],
            "district": ["district", "county"],
            "village": ["village", "town", "city"],
            "marital_status": ["marital status", "married", "single"],
            "children": ["children", "dependents", "number of children"],
            "id_proof": ["id proof", "identity", "aadhaar", "voter id"],
        }

    def map_field(self, field: FormField, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Normalize input text signature
        text_sig = f"{field.name or ''} {field.id or ''} {field.label or ''} {field.placeholder or ''}".lower()
        candidates = []

        for profile_key, keywords in self.rules.items():
            if profile_key not in profile: continue
            
            best_keyword = None
            max_score = 0.0
            
            for keyword in keywords:
                if keyword in text_sig:
                    # Confidence calculation
                    # Exact matches on name/id get 1.0
                    if keyword == field.name or keyword == field.id:
                        score = 1.0
                    # Semantic keyword match in label/placeholder
                    else:
                        score = 0.8 if len(keyword) > 4 else 0.6
                    
                    if score > max_score:
                        max_score = score
                        best_keyword = keyword
            
            if max_score > 0:
                candidates.append({
                    "key": profile_key,
                    "value": profile[profile_key],
                    "confidence": max_score,
                    "reasoning": f"Matched field attributes with '{profile_key}' (conf: {max_score}) due to synonym rule: '{best_keyword}'"
                })

        if not candidates:
            return None

        # Pick best confidence (Agentic decision)
        best = max(candidates, key=lambda x: x["confidence"])
        
        # Validation: check if value is empty or None
        if not best["value"]:
            logger.info(f"Skipped {field.name}: Profile value for '{best['key']}' is empty.")
            return None

        # Validation: check type safety
        if field.type == "email" and "@" not in str(best["value"]):
            logger.warning(f"Validation failed for {field.name}: expected email, got {best['value']}")
            return None

        # Thresholding
        if best["confidence"] >= self.threshold:
            return best
        
        logger.info(f"Skipped field {field.name}: best confidence {best['confidence']} < threshold {self.threshold}")
        return None

# Pluggable Agent
class AgenticFormFiller:
    def __init__(self, mapper: BaseMapper):
        self.mapper = mapper

    def process(self, fields: List[FormField], profile: Dict[str, Any]) -> Dict[str, Any]:
        mapping = {}
        reasoning_logs = []
        
        for field in fields:
            result = self.mapper.map_field(field, profile)
            if result:
                mapping[field.id or field.name] = result["value"]
                log_entry = f"SUCCESS: {result['reasoning']}"
                reasoning_logs.append(log_entry)
                logger.info(log_entry)
            else:
                log_entry = f"SKIP: No confident match for field '{field.name or field.id}'"
                reasoning_logs.append(log_entry)
                logger.info(log_entry)

        return {
            "filled_fields": mapping,
            "reasoning_logs": reasoning_logs
        }

# Initialize Agent with Deterministic Mapper (pluggable)
agent = AgenticFormFiller(DeterministicMapper(threshold=0.5))

@app.post("/agent/fill-form")
async def fill_form(request: MapRequest):
    return agent.process(request.fields, PROFILE_DATA)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
