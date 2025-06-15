import os
from dotenv import load_dotenv
from typing import Optional, List

load_dotenv()

class Config:
    """Configuration management for Trend Analysis MCP Server"""
    
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    
    MAX_TWEETS_PER_SEARCH = int(os.getenv("MAX_TWEETS_PER_SEARCH", "100"))
    MAX_WEB_SOURCES = int(os.getenv("MAX_WEB_SOURCES", "10"))
    DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "24h")
    CACHE_DURATION_MINUTES = int(os.getenv("CACHE_DURATION_MINUTES", "30"))
    
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    SERVER_NAME = "trend-analysis-server"
    SERVER_VERSION = "0.1.0"
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate required configuration and return list of missing items"""
        missing = []
        
        if not cls.TWITTER_BEARER_TOKEN:
            missing.append("TWITTER_BEARER_TOKEN")
            
        if not cls.FIRECRAWL_API_KEY:
            missing.append("FIRECRAWL_API_KEY")
            
        return missing
    
    @classmethod
    def is_valid(cls) -> bool:
        """Check if all required configuration is present"""
        return len(cls.validate()) == 0
    
    @classmethod
    def get_twitter_config(cls) -> dict:
        """Get Twitter API configuration dict"""
        return {
            "bearer_token": cls.TWITTER_BEARER_TOKEN,
            "consumer_key": cls.TWITTER_API_KEY,
            "consumer_secret": cls.TWITTER_API_SECRET,
            "access_token": cls.TWITTER_ACCESS_TOKEN,
            "access_token_secret": cls.TWITTER_ACCESS_TOKEN_SECRET,
        }
    
    @classmethod
    def get_timeframe_hours(cls, timeframe: Optional[str] = None) -> int:
        """Convert timeframe string to hours"""
        tf = timeframe or cls.DEFAULT_TIMEFRAME
        
        if tf.endswith('h'):
            return int(tf[:-1])
        elif tf.endswith('d'):
            return int(tf[:-1]) * 24
        elif tf.endswith('w'):
            return int(tf[:-1]) * 24 * 7
        else:
            # Default to 24 hours if format not recognized
            return 24

config = Config()

if __name__ == "__main__":
    missing = config.validate()
    if missing:
        print(f"Missing required configuration: {', '.join(missing)}")
        print("Please check your .env file")
    else:
        print("Configuration valid!")