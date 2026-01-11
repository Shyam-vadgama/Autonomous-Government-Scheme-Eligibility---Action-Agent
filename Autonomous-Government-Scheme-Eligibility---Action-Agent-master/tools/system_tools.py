"""
Global System Tools
Shared tools and utilities used across all agents in the system
"""
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field
from loguru import logger
import os


class DecisionLog(BaseModel):
    """Individual decision log entry"""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_id: str
    user_id: Optional[str] = None
    decision_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reasoning: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    execution_time_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class UserState(BaseModel):
    """User state information"""
    user_id: str
    profile: Dict[str, Any] = Field(default_factory=dict)
    active_plans: List[str] = Field(default_factory=list)
    completed_plans: List[str] = Field(default_factory=list)
    last_activity: datetime = Field(default_factory=datetime.now)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    progress_history: List[Dict[str, Any]] = Field(default_factory=list)


class AgentDecisionLogger:
    """Logs all agent decisions for transparency and debugging"""
    
    def __init__(self, db_path: str = "./data/decisions.db"):
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure decision log database exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_logs (
                    log_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    user_id TEXT,
                    decision_type TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    execution_time_ms REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            conn.commit()
    
    def log_decision(self, decision: DecisionLog) -> bool:
        """Log a decision to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO decision_logs (
                        log_id, timestamp, agent_id, user_id, decision_type,
                        input_data, output_data, reasoning, confidence_score,
                        execution_time_ms, success, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    decision.log_id,
                    decision.timestamp.isoformat(),
                    decision.agent_id,
                    decision.user_id,
                    decision.decision_type,
                    json.dumps(decision.input_data),
                    json.dumps(decision.output_data),
                    decision.reasoning,
                    decision.confidence_score,
                    decision.execution_time_ms,
                    decision.success,
                    decision.error_message
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error logging decision: {e}")
            return False
    
    def get_decisions_by_user(self, user_id: str, limit: int = 100) -> List[DecisionLog]:
        """Get recent decisions for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM decision_logs 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                decisions = []
                for row in cursor.fetchall():
                    decision = DecisionLog(
                        log_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        agent_id=row[2],
                        user_id=row[3],
                        decision_type=row[4],
                        input_data=json.loads(row[5]),
                        output_data=json.loads(row[6]),
                        reasoning=row[7],
                        confidence_score=row[8],
                        execution_time_ms=row[9],
                        success=bool(row[10]),
                        error_message=row[11]
                    )
                    decisions.append(decision)
                
                return decisions
        except Exception as e:
            logger.error(f"Error retrieving decisions: {e}")
            return []
    
    def get_agent_performance_stats(self, agent_id: str, days: int = 30) -> Dict[str, Any]:
        """Get performance statistics for an agent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Calculate date threshold
                from_date = (datetime.now() - datetime.timedelta(days=days)).isoformat()
                
                # Get basic stats
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_decisions,
                        AVG(confidence_score) as avg_confidence,
                        AVG(execution_time_ms) as avg_execution_time,
                        COUNT(CASE WHEN success = 1 THEN 1 END) as successful_decisions
                    FROM decision_logs 
                    WHERE agent_id = ? AND timestamp > ?
                """, (agent_id, from_date))
                
                row = cursor.fetchone()
                if row:
                    total = row[0]
                    return {
                        "agent_id": agent_id,
                        "total_decisions": total,
                        "avg_confidence_score": row[1] or 0.0,
                        "avg_execution_time_ms": row[2] or 0.0,
                        "success_rate": (row[3] / total) if total > 0 else 0.0,
                        "analysis_period_days": days
                    }
                else:
                    return {"agent_id": agent_id, "total_decisions": 0}
                    
        except Exception as e:
            logger.error(f"Error getting agent stats: {e}")
            return {"error": str(e)}


class UserStateStore:
    """Manages persistent user state across sessions"""
    
    def __init__(self, db_path: str = "./data/user_states.db"):
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure user state database exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_states (
                    user_id TEXT PRIMARY KEY,
                    profile TEXT NOT NULL,
                    active_plans TEXT NOT NULL,
                    completed_plans TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    preferences TEXT NOT NULL,
                    progress_history TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def save_user_state(self, user_state: UserState) -> bool:
        """Save user state to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_states (
                        user_id, profile, active_plans, completed_plans,
                        last_activity, preferences, progress_history
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_state.user_id,
                    json.dumps(user_state.profile),
                    json.dumps(user_state.active_plans),
                    json.dumps(user_state.completed_plans),
                    user_state.last_activity.isoformat(),
                    json.dumps(user_state.preferences),
                    json.dumps(user_state.progress_history)
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving user state: {e}")
            return False
    
    def get_user_state(self, user_id: str) -> Optional[UserState]:
        """Get user state from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM user_states WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return UserState(
                        user_id=row[0],
                        profile=json.loads(row[1]),
                        active_plans=json.loads(row[2]),
                        completed_plans=json.loads(row[3]),
                        last_activity=datetime.fromisoformat(row[4]),
                        preferences=json.loads(row[5]),
                        progress_history=json.loads(row[6])
                    )
                else:
                    # Create new user state
                    new_state = UserState(user_id=user_id)
                    self.save_user_state(new_state)
                    return new_state
                    
        except Exception as e:
            logger.error(f"Error getting user state: {e}")
            return None
    
    def update_user_profile(self, user_id: str, profile_updates: Dict[str, Any]) -> bool:
        """Update user profile data"""
        user_state = self.get_user_state(user_id)
        if user_state:
            user_state.profile.update(profile_updates)
            user_state.last_activity = datetime.now()
            return self.save_user_state(user_state)
        return False
    
    def add_active_plan(self, user_id: str, plan_id: str) -> bool:
        """Add a new active plan for user"""
        user_state = self.get_user_state(user_id)
        if user_state and plan_id not in user_state.active_plans:
            user_state.active_plans.append(plan_id)
            user_state.last_activity = datetime.now()
            return self.save_user_state(user_state)
        return False
    
    def complete_plan(self, user_id: str, plan_id: str) -> bool:
        """Move plan from active to completed"""
        user_state = self.get_user_state(user_id)
        if user_state and plan_id in user_state.active_plans:
            user_state.active_plans.remove(plan_id)
            user_state.completed_plans.append(plan_id)
            user_state.last_activity = datetime.now()
            return self.save_user_state(user_state)
        return False


class SchemeRuleEngine:
    """Rule engine for scheme eligibility evaluation"""
    
    def __init__(self):
        self.rule_cache = {}
    
    def evaluate_rule(self, rule_name: str, user_data: Dict[str, Any], rule_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a specific eligibility rule"""
        try:
            if rule_name == "age_range":
                return self._evaluate_age_range(user_data, rule_parameters)
            elif rule_name == "income_limit":
                return self._evaluate_income_limit(user_data, rule_parameters)
            elif rule_name == "caste_category":
                return self._evaluate_caste_category(user_data, rule_parameters)
            elif rule_name == "geographic_eligibility":
                return self._evaluate_geographic_eligibility(user_data, rule_parameters)
            elif rule_name == "document_availability":
                return self._evaluate_document_availability(user_data, rule_parameters)
            else:
                return {"passed": False, "reason": f"Unknown rule: {rule_name}"}
                
        except Exception as e:
            logger.error(f"Error evaluating rule {rule_name}: {e}")
            return {"passed": False, "reason": f"Rule evaluation error: {str(e)}"}
    
    def _evaluate_age_range(self, user_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate age range eligibility"""
        user_age = user_data.get("age", 0)
        min_age = parameters.get("min_age", 0)
        max_age = parameters.get("max_age", 150)
        
        if min_age <= user_age <= max_age:
            return {
                "passed": True,
                "reason": f"Age {user_age} is within range {min_age}-{max_age}",
                "confidence": 1.0
            }
        else:
            return {
                "passed": False,
                "reason": f"Age {user_age} is outside range {min_age}-{max_age}",
                "confidence": 1.0
            }
    
    def _evaluate_income_limit(self, user_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate income limit eligibility"""
        user_income = user_data.get("annual_income", 0)
        max_income = parameters.get("max_income", float('inf'))
        min_income = parameters.get("min_income", 0)
        
        if min_income <= user_income <= max_income:
            return {
                "passed": True,
                "reason": f"Income ₹{user_income:,} is within limit ₹{min_income:,}-₹{max_income:,}",
                "confidence": 1.0
            }
        else:
            return {
                "passed": False,
                "reason": f"Income ₹{user_income:,} exceeds limit ₹{max_income:,}" if user_income > max_income 
                         else f"Income ₹{user_income:,} below minimum ₹{min_income:,}",
                "confidence": 1.0
            }
    
    def _evaluate_caste_category(self, user_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate caste category eligibility"""
        user_caste = user_data.get("caste_category", "unknown")
        required_categories = parameters.get("allowed_categories", [])
        
        if user_caste in required_categories:
            return {
                "passed": True,
                "reason": f"User caste {user_caste} is in allowed categories",
                "confidence": 1.0
            }
        elif user_caste == "unknown":
            return {
                "passed": False,
                "reason": "Caste category not specified - verification needed",
                "confidence": 0.5
            }
        else:
            return {
                "passed": False,
                "reason": f"Caste {user_caste} not in allowed categories: {required_categories}",
                "confidence": 1.0
            }
    
    def _evaluate_geographic_eligibility(self, user_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate geographic eligibility"""
        user_state = user_data.get("state", "unknown").lower()
        user_area_type = user_data.get("rural_urban", "unknown").lower()
        
        allowed_states = [s.lower() for s in parameters.get("allowed_states", [])]
        allowed_area_types = [t.lower() for t in parameters.get("allowed_area_types", [])]
        
        # Check state eligibility
        if allowed_states and user_state not in allowed_states:
            return {
                "passed": False,
                "reason": f"Scheme not available in {user_state}",
                "confidence": 1.0
            }
        
        # Check area type eligibility
        if allowed_area_types and user_area_type not in allowed_area_types:
            return {
                "passed": False,
                "reason": f"Scheme only for {'/'.join(allowed_area_types)} areas",
                "confidence": 1.0
            }
        
        return {
            "passed": True,
            "reason": "Geographic eligibility satisfied",
            "confidence": 1.0
        }
    
    def _evaluate_document_availability(self, user_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate document availability"""
        available_docs = user_data.get("available_documents", [])
        required_docs = parameters.get("required_documents", [])
        optional_docs = parameters.get("optional_documents", [])
        
        missing_required = [doc for doc in required_docs if doc not in available_docs]
        available_optional = [doc for doc in optional_docs if doc in available_docs]
        
        if not missing_required:
            return {
                "passed": True,
                "reason": "All required documents available",
                "confidence": 1.0,
                "details": {
                    "missing_required": missing_required,
                    "available_optional": available_optional
                }
            }
        else:
            return {
                "passed": False,
                "reason": f"Missing required documents: {missing_required}",
                "confidence": 0.0,
                "details": {
                    "missing_required": missing_required,
                    "available_optional": available_optional
                }
            }


class HumanReadableExplainer:
    """Converts technical decisions into human-readable explanations"""
    
    @staticmethod
    def explain_eligibility_decision(decision_data: Dict[str, Any]) -> str:
        """Create human-readable eligibility explanation"""
        overall_status = decision_data.get("overall_status", "unknown")
        passed_rules = decision_data.get("passed_rules", [])
        failed_rules = decision_data.get("failed_rules", [])
        
        if overall_status == "eligible":
            explanation = "✅ **You are eligible for this scheme!**\n\n"
            explanation += "**Why you qualify:**\n"
            for rule in passed_rules[:3]:
                explanation += f"• {rule.get('reasoning', 'Requirement met')}\n"
        
        elif overall_status == "not_eligible":
            explanation = "❌ **You are not currently eligible for this scheme.**\n\n"
            explanation += "**Reasons for ineligibility:**\n"
            for rule in failed_rules[:3]:
                explanation += f"• {rule.get('reasoning', 'Requirement not met')}\n"
        
        elif overall_status == "conditionally_eligible":
            explanation = "⚠️ **You may be eligible with some conditions.**\n\n"
            explanation += "**What you need to do:**\n"
            for rule in failed_rules[:2]:
                explanation += f"• {rule.get('reasoning', 'Additional requirement')}\n"
        
        else:
            explanation = "ℹ️ **Need more information to determine eligibility.**\n\n"
            explanation += "Please provide complete details about your situation."
        
        return explanation
    
    @staticmethod
    def explain_action_plan(plan_data: Dict[str, Any]) -> str:
        """Create human-readable action plan explanation"""
        plan_name = plan_data.get("scheme_name", "Government Scheme")
        total_steps = plan_data.get("total_steps", 0)
        estimated_time = plan_data.get("estimated_total_time", "several weeks")
        
        explanation = f"📋 **Action Plan for {plan_name}**\n\n"
        explanation += f"**Overview:** {total_steps} steps, estimated {estimated_time}\n\n"
        
        # Critical steps
        critical_steps = plan_data.get("critical_steps", [])
        if critical_steps:
            explanation += "🔴 **Critical Steps (Must Complete):**\n"
            for i, step in enumerate(critical_steps[:3], 1):
                explanation += f"{i}. {step.get('title', 'Important step')}\n"
            if len(critical_steps) > 3:
                explanation += f"... and {len(critical_steps) - 3} more critical steps\n"
            explanation += "\n"
        
        # Timeline
        timeline = plan_data.get("suggested_timeline", "")
        if timeline:
            explanation += f"⏰ **Timeline:** {timeline}\n\n"
        
        # Success tips
        success_tips = plan_data.get("success_tips", [])
        if success_tips:
            explanation += "💡 **Success Tips:**\n"
            for tip in success_tips[:2]:
                explanation += f"• {tip}\n"
        
        return explanation


class SafeFailureHandler:
    """Handles failures gracefully and provides fallback mechanisms"""
    
    @staticmethod
    def handle_agent_failure(agent_id: str, error: Exception, fallback_response: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle agent failure with graceful degradation"""
        logger.error(f"Agent {agent_id} failed: {error}")
        
        return {
            "success": False,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "fallback_response": fallback_response or {
                "message": "Agent temporarily unavailable. Please try again later.",
                "suggested_actions": [
                    "Check your input data",
                    "Try again in a few minutes",
                    "Contact support if problem persists"
                ]
            }
        }
    
    @staticmethod
    def create_minimal_response(request_type: str) -> Dict[str, Any]:
        """Create minimal response when systems fail"""
        responses = {
            "profile_analysis": {
                "profile": {
                    "name": "Unknown",
                    "eligibility_status": "needs_verification"
                },
                "message": "Please provide your information manually for processing"
            },
            "scheme_discovery": {
                "schemes": [],
                "message": "Unable to discover schemes automatically. Please contact local government office."
            },
            "eligibility_assessment": {
                "status": "manual_review_required",
                "message": "Please visit local office for eligibility verification"
            },
            "action_plan": {
                "steps": [
                    {
                        "title": "Visit Local Office",
                        "description": "Contact your local government office for assistance",
                        "priority": "high"
                    }
                ],
                "message": "Manual assistance recommended"
            }
        }
        
        return responses.get(request_type, {
            "message": "Service temporarily unavailable. Please try again later."
        })


# Global instances
_decision_logger = None
_user_state_store = None
_rule_engine = None

def get_decision_logger() -> AgentDecisionLogger:
    """Get global decision logger instance"""
    global _decision_logger
    if _decision_logger is None:
        _decision_logger = AgentDecisionLogger()
    return _decision_logger

def get_user_state_store() -> UserStateStore:
    """Get global user state store instance"""
    global _user_state_store
    if _user_state_store is None:
        _user_state_store = UserStateStore()
    return _user_state_store

def get_rule_engine() -> SchemeRuleEngine:
    """Get global rule engine instance"""
    global _rule_engine
    if _rule_engine is None:
        _rule_engine = SchemeRuleEngine()
    return _rule_engine