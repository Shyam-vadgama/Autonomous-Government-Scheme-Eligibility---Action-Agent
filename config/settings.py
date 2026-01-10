"""
System Settings and Configuration
Central configuration management for the Government Scheme Agent system
"""
import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field


class AgentSettings(BaseSettings):
    """Main application settings"""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Gemini AI Configuration
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", env="GEMINI_MODEL")
    gemini_temperature: float = Field(default=0.7, env="GEMINI_TEMPERATURE")
    gemini_max_tokens: int = Field(default=8192, env="GEMINI_MAX_TOKENS")
    gemini_timeout: int = Field(default=30, env="GEMINI_TIMEOUT")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Agent System Configuration
    max_agent_retries: int = Field(default=3, env="MAX_AGENT_RETRIES")
    agent_timeout: int = Field(default=60, env="AGENT_TIMEOUT")
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    
    # Database Configuration
    database_path: str = Field(default="data/agent_system.db", env="DATABASE_PATH")
    
    # Application Paths
    schemes_db_path: str = Field(default="data/schemes_db.py", env="SCHEMES_DB_PATH")
    logs_directory: str = Field(default="logs", env="LOGS_DIRECTORY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class SecuritySettings(BaseSettings):
    """Security and privacy settings"""
    
    # API Security
    enable_cors: bool = Field(default=True, env="ENABLE_CORS")
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")
    
    # Data Privacy
    anonymize_logs: bool = Field(default=False, env="ANONYMIZE_LOGS")
    data_retention_days: int = Field(default=30, env="DATA_RETENTION_DAYS")
    
    # Rate Limiting
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    requests_per_minute: int = Field(default=60, env="REQUESTS_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AgentConfig(BaseSettings):
    """Individual agent configuration"""
    
    # Profile Analyzer Agent
    profile_analyzer_enabled: bool = Field(default=True, env="PROFILE_ANALYZER_ENABLED")
    profile_confidence_threshold: float = Field(default=0.7, env="PROFILE_CONFIDENCE_THRESHOLD")
    
    # Scheme Discovery Agent
    scheme_discovery_enabled: bool = Field(default=True, env="SCHEME_DISCOVERY_ENABLED")
    max_schemes_to_discover: int = Field(default=10, env="MAX_SCHEMES_TO_DISCOVER")
    relevance_threshold: float = Field(default=0.5, env="RELEVANCE_THRESHOLD")
    
    # Eligibility Reasoning Agent
    eligibility_reasoning_enabled: bool = Field(default=True, env="ELIGIBILITY_REASONING_ENABLED")
    eligibility_confidence_threshold: float = Field(default=0.8, env="ELIGIBILITY_CONFIDENCE_THRESHOLD")
    
    # Action Planner Agent
    action_planner_enabled: bool = Field(default=True, env="ACTION_PLANNER_ENABLED")
    max_action_steps: int = Field(default=20, env="MAX_ACTION_STEPS")
    
    # Follow-up Agent
    follow_up_enabled: bool = Field(default=True, env="FOLLOW_UP_ENABLED")
    follow_up_interval_days: int = Field(default=7, env="FOLLOW_UP_INTERVAL_DAYS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instances
agent_settings = AgentSettings()
security_settings = SecuritySettings()
agent_config = AgentConfig()


def get_settings() -> AgentSettings:
    """Get main application settings"""
    return agent_settings


def get_security_settings() -> SecuritySettings:
    """Get security settings"""
    return security_settings


def get_agent_config() -> AgentConfig:
    """Get agent configuration"""
    return agent_config


def validate_configuration() -> Dict[str, Any]:
    """Validate the current configuration"""
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check required settings
    if not agent_settings.gemini_api_key:
        validation_results["errors"].append("GEMINI_API_KEY is required")
        validation_results["valid"] = False
    
    # Check API configuration
    if agent_settings.api_port < 1024 or agent_settings.api_port > 65535:
        validation_results["warnings"].append("API port should be between 1024-65535")
    
    # Check agent configuration
    if agent_config.profile_confidence_threshold > 1.0 or agent_config.profile_confidence_threshold < 0.0:
        validation_results["errors"].append("Profile confidence threshold must be between 0.0-1.0")
        validation_results["valid"] = False
    
    if agent_config.relevance_threshold > 1.0 or agent_config.relevance_threshold < 0.0:
        validation_results["errors"].append("Relevance threshold must be between 0.0-1.0")
        validation_results["valid"] = False
    
    # Check paths
    import os
    if not os.path.exists(os.path.dirname(agent_settings.database_path)):
        validation_results["warnings"].append(f"Database directory does not exist: {os.path.dirname(agent_settings.database_path)}")
    
    if not os.path.exists(agent_settings.logs_directory):
        validation_results["warnings"].append(f"Logs directory does not exist: {agent_settings.logs_directory}")
    
    return validation_results


def get_configuration_summary() -> Dict[str, Any]:
    """Get a summary of current configuration"""
    return {
        "api": {
            "host": agent_settings.api_host,
            "port": agent_settings.api_port,
            "debug": agent_settings.debug
        },
        "gemini": {
            "model": agent_settings.gemini_model,
            "temperature": agent_settings.gemini_temperature,
            "max_tokens": agent_settings.gemini_max_tokens,
            "api_key_configured": bool(agent_settings.gemini_api_key)
        },
        "agents": {
            "profile_analyzer": agent_config.profile_analyzer_enabled,
            "scheme_discovery": agent_config.scheme_discovery_enabled,
            "eligibility_reasoning": agent_config.eligibility_reasoning_enabled,
            "action_planner": agent_config.action_planner_enabled,
            "follow_up": agent_config.follow_up_enabled
        },
        "security": {
            "cors_enabled": security_settings.enable_cors,
            "rate_limiting": security_settings.enable_rate_limiting,
            "requests_per_minute": security_settings.requests_per_minute
        },
        "system": {
            "log_level": agent_settings.log_level,
            "max_retries": agent_settings.max_agent_retries,
            "timeout": agent_settings.agent_timeout,
            "database_path": agent_settings.database_path
        }
    }


# Environment configuration helper
def setup_environment():
    """Setup environment and create necessary directories"""
    import os
    
    # Create logs directory
    if not os.path.exists(agent_settings.logs_directory):
        os.makedirs(agent_settings.logs_directory)
    
    # Create database directory
    db_dir = os.path.dirname(agent_settings.database_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Set up logging
    from loguru import logger
    
    # Remove default logger
    logger.remove()
    
    # Add console logging
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=agent_settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file logging if specified
    if agent_settings.log_file:
        logger.add(
            agent_settings.log_file,
            level=agent_settings.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )


if __name__ == "__main__":
    # Test configuration
    print("🔧 Testing configuration...")
    
    setup_environment()
    validation = validate_configuration()
    
    if validation["valid"]:
        print("✅ Configuration is valid")
        print(f"📊 Configuration summary: {get_configuration_summary()}")
    else:
        print("❌ Configuration errors found:")
        for error in validation["errors"]:
            print(f"   - {error}")
    
    if validation["warnings"]:
        print("⚠️ Configuration warnings:")
        for warning in validation["warnings"]:
            print(f"   - {warning}")