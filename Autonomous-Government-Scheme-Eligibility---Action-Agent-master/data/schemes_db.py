"""
Government Schemes Database Loader
Loads scheme data from schemes.json
"""
import json
import os
from loguru import logger

def load_schemes():
    """Load schemes from schemes.json file"""
    try:
        # Look in root directory then data directory
        paths = ["schemes.json", "data/schemes.json"]
        
        for path in paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    schemes = json.load(f)
                    logger.info(f"Loaded {len(schemes)} schemes from {path}")
                    return schemes
        
        logger.warning("schemes.json not found in expected locations")
        return []
        
    except Exception as e:
        logger.error(f"Error loading schemes.json: {e}")
        return []

# Export the schemes list
GOVERNMENT_SCHEMES = load_schemes()
