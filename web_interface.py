"""
FastAPI Web Interface for Government Scheme Agent
Provides REST API endpoints for the agent system
"""
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from datetime import datetime
from dotenv import load_dotenv # Import load_dotenv

from main import get_government_scheme_agent, UserRequest

load_dotenv() # Load environment variables from .env



# Pydantic models for API
class ProfileAnalysisRequest(BaseModel):
    user_input: str
    existing_profile: Dict[str, Any] = {}
    user_id: Optional[str] = "anonymous"


class SchemeApplicationRequest(BaseModel):
    user_input: str
    user_id: Optional[str] = "anonymous"
    options: Dict[str, Any] = {}


class FollowUpRequest(BaseModel):
    user_id: str
    update_message: str
    options: Dict[str, Any] = {}


# Initialize FastAPI app
app = FastAPI(
    title="Government Scheme Eligibility Agent API",
    description="AI-powered assistant for Indian government scheme applications",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent system
agent_system = None


@app.on_event("startup")
async def startup_event():
    """Initialize the agent system on startup"""
    global agent_system
    
    # Set quota conservation mode during startup
    os.environ["SKIP_AGENT_INIT_TEST"] = "true"
    
    try:
        agent_system = get_government_scheme_agent()
        success = await agent_system.initialize_system()
        
        if success:
            print("✅ Government Scheme Agent system initialized successfully")
        else:
            print("⚠️  Government Scheme Agent initialized with limited functionality")
            print("    (likely due to API quota exhaustion or connectivity issues)")
            # Keep the agent_system object even if initialization failed
            # It can still provide basic functionality
            
    except Exception as e:
        print(f"⚠️  Agent system startup encountered issues: {str(e)}")
        print("    Web interface will continue with demonstration mode")
        # Set agent_system to None to trigger demo responses
        agent_system = None


@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "service": "Government Scheme Eligibility Agent",
        "version": "1.0.0",
        "status": "operational",
        "ai_model": "Google Gemini",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "analyze_profile": "/api/v1/analyze-profile",
            "apply_scheme": "/api/v1/apply-scheme", 
            "follow_up": "/api/v1/follow-up",
            "status": "/api/v1/status",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with quota awareness"""
    try:
        if agent_system:
            status = agent_system.get_system_status()
            
            # Add quota information
            quota_info = {
                "api_provider": "Google Gemini AI",
                "tier": "Free Tier",
                "daily_limit": "20 requests",
                "reset_time": "Daily at midnight UTC"
            }
            
            # Check if agents are functional
            agent_count = len(status.get("agents", {}))
            functional_agents = sum(1 for agent_status in status.get("agents", {}).values() 
                                  if agent_status.get("status") in ["idle", "ready"])
            
            system_health = "healthy" if functional_agents == agent_count else "limited"
            
            return {
                "status": system_health,
                "system_status": status,
                "quota_info": quota_info,
                "agent_summary": {
                    "total": agent_count,
                    "functional": functional_agents,
                    "ratio": f"{functional_agents}/{agent_count}"
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "demo_mode", 
                "reason": "Agent system in demonstration mode (quota exhausted)",
                "quota_info": {
                    "api_provider": "Google Gemini AI",
                    "tier": "Free Tier",
                    "daily_limit": "20 requests",
                    "current_status": "Quota Exhausted",
                    "reset_time": "Daily at midnight UTC"
                },
                "available_features": ["Demo responses", "System information", "API documentation"],
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "reason": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/v1/analyze-profile")
async def analyze_profile(request: ProfileAnalysisRequest):
    """Analyze user profile for scheme eligibility"""
    try:
        user_request = UserRequest(
            user_id=request.user_id or f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            request_type="update_profile",
            user_input=request.user_input,
            existing_profile=request.existing_profile
        )
        
        response = await agent_system.process_user_request(user_request)
        
        return {
            "success": response.success,
            "user_profile": response.user_profile,
            "next_question": response.next_question,
            "completion_percentage": response.completion_percentage,
            "summary": response.summary,
            "processing_time_ms": response.processing_time_ms,
            "confidence_score": response.confidence_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/apply-scheme")
async def apply_for_schemes(request: SchemeApplicationRequest):
    """Find schemes and create application plan"""
    try:
        user_request = UserRequest(
            user_id=request.user_id or f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            request_type="new_application",
            user_input=request.user_input,
            options=request.options
        )
        
        response = await agent_system.process_user_request(user_request)
        
        return {
            "success": response.success,
            "user_profile": response.user_profile,
            "discovered_schemes": response.discovered_schemes,
            "eligibility_assessments": response.eligibility_assessments,
            "action_plans": response.action_plans,
            "summary": response.summary,
            "recommendations": response.recommendations,
            "next_steps": response.next_steps,
            "confidence_score": response.confidence_score,
            "processing_time_ms": response.processing_time_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/follow-up")
async def follow_up_application(request: FollowUpRequest):
    """Follow up on existing application"""
    try:
        user_request = UserRequest(
            user_id=request.user_id,
            request_type="follow_up",
            user_input=request.update_message,
            options=request.options
        )
        
        response = await agent_system.process_user_request(user_request)
        
        return {
            "success": response.success,
            "follow_up_analysis": response.follow_up_analysis,
            "summary": response.summary,
            "recommendations": response.recommendations,
            "next_steps": response.next_steps,
            "processing_time_ms": response.processing_time_ms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status")
async def get_system_status():
    """Get detailed system status"""
    try:
        if agent_system:
            status = agent_system.get_system_status()
            return status
        else:
            raise HTTPException(status_code=503, detail="Agent system not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/schemes")
async def get_available_schemes():
    """Get list of available government schemes"""
    try:
        from data.schemes_db import GOVERNMENT_SCHEMES
        return {
            "total_schemes": len(GOVERNMENT_SCHEMES),
            "schemes": [
                {
                    "scheme_id": scheme["scheme_id"],
                    "name": scheme["name"],
                    "category": scheme["category"],
                    "description": scheme["description"],
                    "target_groups": scheme.get("target_groups", []),
                    "status": scheme.get("status", "active")
                }
                for scheme in GOVERNMENT_SCHEMES
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Simple HTML interface
@app.get("/demo", response_class=HTMLResponse)
async def demo_interface():
    """Simple demo interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Government Scheme Agent Demo</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f0f2f5; color: #333; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
            .header { text-align: center; color: #1a202c; margin-bottom: 30px; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; }
            .header h1 { margin: 0; font-size: 2.5em; color: #2c5282; }
            .header p { color: #718096; margin-top: 10px; font-size: 1.1em; }
            
            .form-group { margin-bottom: 25px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #4a5568; }
            textarea, input { width: 100%; padding: 12px; border: 1px solid #cbd5e0; border-radius: 8px; font-size: 16px; box-sizing: border-box; transition: border-color 0.2s; }
            textarea:focus, input:focus { border-color: #3182ce; outline: none; box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2); }
            textarea { height: 150px; resize: vertical; line-height: 1.5; }
            
            .btn-container { display: flex; gap: 15px; margin-top: 30px; }
            button { flex: 1; background-color: #3182ce; color: white; padding: 14px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; transition: background-color 0.2s; }
            button:hover { background-color: #2b6cb0; }
            button.secondary { background-color: #718096; }
            button.secondary:hover { background-color: #4a5568; }
            
            .result { margin-top: 30px; padding: 25px; background-color: #f7fafc; border-radius: 8px; border: 1px solid #e2e8f0; display: none; }
            .result.loading { color: #d69e2e; font-weight: 600; text-align: center; display: block; }
            .result.success { border-left: 5px solid #48bb78; }
            .result.error { border-left: 5px solid #f56565; color: #c53030; }
            
            .profile-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-top: 20px; }
            .profile-section { margin-bottom: 20px; }
            .profile-section h3 { color: #2d3748; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-bottom: 10px; font-size: 1.1em; }
            .data-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
            .data-item { background: #f8fafc; padding: 10px; border-radius: 6px; }
            .data-label { font-size: 0.85em; color: #718096; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
            .data-value { font-weight: 600; color: #2d3748; word-break: break-word; }
            .tag { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600; margin-left: 10px; }
            .tag.student { background-color: #ebf8ff; color: #3182ce; }
            .tag.farmer { background-color: #f0fff4; color: #38a169; }
            
            .missing-alert { background-color: #fffaf0; border: 1px solid #fbd38d; color: #c05621; padding: 15px; border-radius: 6px; margin-top: 20px; }
            .missing-alert h4 { margin: 0 0 10px 0; font-size: 1em; }
            .missing-list { margin: 0; padding-left: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🇮🇳 Government Scheme Eligibility Agent</h1>
                <p>Advanced Citizen Data Extraction & Scheme Matching</p>
            </div>
            
            <div class="form-group">
                <label for="userInput">Describe your profile (Student or Farmer):</label>
                <textarea id="userInput" placeholder="Example: My name is Rajesh, I am a 20 year old student pursuing B.Tech in Computer Science at a private college in Pune. My father is a farmer with 3 acres of land..."></textarea>
            </div>
            
            <div class="form-group">
                <label for="userId">User ID (optional):</label>
                <input type="text" id="userId" placeholder="Enter your user ID or leave blank for anonymous">
            </div>
            
            <div class="btn-container">
                <button onclick="analyzeProfile()" class="secondary">Extract Profile Data</button>
                <button onclick="findSchemes()">Find Eligible Schemes</button>
            </div>
            
            <div id="result" class="result"></div>
        </div>

        <script>
            function formatValue(val) {
                if (val === null || val === undefined) return '<span style="color: #a0aec0; font-style: italic;">Not provided</span>';
                if (val === true) return '<span style="color: #48bb78;">Yes</span>';
                if (val === false) return '<span style="color: #e53e3e;">No</span>';
                return val;
            }

            function renderProfileSection(title, data, fields) {
                let html = `<div class="profile-section"><h3>${title}</h3><div class="data-grid">`;
                fields.forEach(field => {
                    if (data.hasOwnProperty(field)) {
                        html += `
                            <div class="data-item">
                                <div class="data-label">${field.replace(/_/g, ' ')}</div>
                                <div class="data-value">${formatValue(data[field])}</div>
                            </div>`;
                    }
                });
                html += '</div></div>';
                return html;
            }

            async function analyzeProfile(isUpdate = false) {
                let userInput;
                const resultDiv = document.getElementById('result');
                const userId = document.getElementById('userId').value || 'demo_user';

                if (isUpdate) {
                    userInput = document.getElementById('replyInput').value;
                    if (!userInput.trim()) {
                        alert('Please enter your answer');
                        return;
                    }
                } else {
                    userInput = document.getElementById('userInput').value;
                    if (!userInput.trim()) {
                        alert('Please enter your information');
                        return;
                    }
                }
                
                resultDiv.style.display = 'block';
                if (!isUpdate) resultDiv.className = 'result loading'; // Only show loading on full refresh or handle UI nicely
                
                try {
                    // We send an empty existing_profile to force the backend to load it from the SQLite DB
                    const response = await fetch('/api/v1/analyze-profile', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_input: userInput,
                            user_id: userId,
                            existing_profile: {} 
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const profile = data.user_profile;
                        const userType = profile.user_type || 'Unknown';
                        
                        // Get completion percentage from root response or profile or calculate
                        let calculatedPercent = 0;
                        if (data.completion_percentage !== undefined && data.completion_percentage !== null) {
                            calculatedPercent = data.completion_percentage;
                        } else if (profile.completion_percentage !== undefined) {
                            calculatedPercent = profile.completion_percentage;
                        } else {
                             // Fallback
                             const missingCount = (profile.missing_fields || []).length;
                             const estimatedTotal = userType === 'student' ? 18 : 16; 
                             calculatedPercent = Math.max(0, Math.min(100, Math.round(((estimatedTotal - missingCount) / estimatedTotal) * 100)));
                        }

                        resultDiv.className = 'result success';
                        let html = `
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
                                <h2 style="margin: 0; color: #2d3748;">Extracted Profile</h2>
                                <span class="tag ${userType.toLowerCase()}">${userType.toUpperCase()}</span>
                            </div>
                            
                            <div style="background: #edf2f7; border-radius: 8px; height: 10px; width: 100%; margin-bottom: 20px; overflow: hidden;">
                                <div style="background: #48bb78; width: ${calculatedPercent}%; height: 100%; transition: width 0.5s ease;"></div>
                            </div>
                            <div style="text-align: right; font-size: 0.85em; color: #718096; margin-top: -15px; margin-bottom: 20px;">${calculatedPercent}% Complete</div>
                        `;

                        // Next Question / Chat Interface
                        let question = data.next_question;
                        if (!question && profile.missing_fields && profile.missing_fields.length > 0) {
                            question = `Please provide your ${profile.missing_fields.slice(0,3).join(', ').replace(/_/g, ' ')} to complete your profile.`;
                        } else if (!question) {
                             question = "Profile looks good! You can now search for schemes.";
                        }

                        html += `
                            <div style="background: #ebf8ff; border: 1px solid #bee3f8; padding: 15px; border-radius: 8px; margin-bottom: 25px; display: flex; align-items: start;">
                                <div style="font-size: 1.5em; margin-right: 15px;">🤖</div>
                                <div>
                                    <div style="font-weight: 600; color: #2c5282; margin-bottom: 5px;">Agent</div>
                                    <div style="color: #2b6cb0;">${question}</div>
                                </div>
                            </div>
                        `;
                        
                        // Reply Box
                        if (calculatedPercent < 100) {
                             html += `
                                <div style="display: flex; gap: 10px; margin-bottom: 30px;">
                                    <input type="text" id="replyInput" placeholder="Type your answer here..." style="flex: 1; padding: 12px; border: 1px solid #cbd5e0; border-radius: 8px;">
                                    <button onclick="analyzeProfile(true)" style="flex: 0 0 auto; padding: 12px 20px;">Reply</button>
                                </div>
                             `;
                        }

                        // Common Fields
                        const commonFields = ["name", "age", "gender", "state", "district", "income_range", "category", "minority", "disability"];
                        html += renderProfileSection("Personal Details", profile, commonFields);
                        
                        // Type Specific Fields
                        if (userType === 'student') {
                            const studentFields = ["education_level", "course_name", "stream", "institution_name", "institution_type", "year_of_study", "previous_year_marks_percent", "is_hosteller"];
                            html += renderProfileSection("Student Details", profile, studentFields);
                        } else if (userType === 'farmer') {
                            const farmerFields = ["owns_land", "land_area_acres", "main_crops", "irrigation_source", "has_farmer_id", "has_livestock"];
                            html += renderProfileSection("Farmer Details", profile, farmerFields);
                        }
                        
                        resultDiv.innerHTML = html;
                        
                        // Scroll to top of result if update
                        if(isUpdate) resultDiv.scrollIntoView({ behavior: 'smooth' });
                        
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = data.summary || 'An unknown error occurred during profile analysis. Please check your connection or API key.';
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = `Network Error: Could not connect to the server. Is it running? Details: ${error.message}`;
                }
            }
            
            async function findSchemes() {
                const userInput = document.getElementById('userInput').value;
                const userId = document.getElementById('userId').value || 'demo_user';
                const resultDiv = document.getElementById('result');
                
                if (!userInput.trim()) {
                    alert('Please enter your information');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.className = 'result loading';
                resultDiv.textContent = 'Analyzing schemes based on your profile...';
                
                try {
                    const response = await fetch('/api/v1/apply-scheme', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_input: userInput,
                            user_id: userId,
                            options: { max_schemes: 5 }
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.className = 'result success';
                        
                        // Reuse the profile display logic if possible, or just show schemes
                        let html = `
                            <h2 style="color: #2d3748;">Scheme Analysis Results</h2>
                            <div class="profile-card" style="background: #f0fff4; border: 1px solid #c6f6d5;">
                                <h3 style="color: #276749;">Summary</h3>
                                <p>${data.summary}</p>
                            </div>
                        `;
                        
                        if (data.discovered_schemes && data.discovered_schemes.length > 0) {
                            html += `<h3 style="margin-top: 30px;">Top Eligible Schemes</h3>`;
                            data.discovered_schemes.forEach((scheme, index) => {
                                html += `
                                    <div class="profile-card">
                                        <div style="display: flex; justify-content: space-between;">
                                            <h4 style="margin: 0; color: #2b6cb0;">${index + 1}. ${scheme.name}</h4>
                                            <span style="background: #ebf8ff; color: #2c5282; padding: 2px 8px; border-radius: 4px; font-size: 0.9em;">${(scheme.relevance_score * 100).toFixed(0)}% Match</span>
                                        </div>
                                        <p style="color: #718096; margin: 10px 0;">${scheme.description}</p>
                                        <div style="font-size: 0.9em; color: #4a5568;">
                                            <strong>Category:</strong> ${scheme.category}
                                        </div>
                                    </div>
                                `;
                            });
                        }
                        
                        if (data.recommendations && data.recommendations.length > 0) {
                            html += `<h3 style="margin-top: 30px;">Recommendations</h3><ul>`;
                            data.recommendations.forEach(rec => {
                                html += `<li>${rec}</li>`;
                            });
                            html += `</ul>`;
                        }
                        
                        resultDiv.innerHTML = html;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.textContent = data.summary || 'An unknown error occurred during scheme analysis. Please check the profile extraction first.';
                    }
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.textContent = `Network Error: Could not connect to the server. Is it running? Details: ${error.message}`;
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content


if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    workers = int(os.getenv("WORKERS", "1"))
    
    # Run the server
    uvicorn.run(
        "web_interface:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,  # Set to True for development
        log_level="info"
    )