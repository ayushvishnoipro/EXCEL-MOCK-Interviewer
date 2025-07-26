"""
Configuration settings for Excel Mock Interviewer
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Configuration
    @staticmethod
    def get_gemini_api_key():
        """Get Gemini API key from secrets or environment"""
        api_key = None
        
        try:
            # Try Streamlit secrets first (for cloud deployment)
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            try:
                # Fallback to environment variable (for local development)
                api_key = os.getenv("GEMINI_API_KEY")
            except:
                pass
        
        return api_key
    
    # Model Configuration
    GEMINI_MODEL = "gemini-2.0-flash-exp"
    MAX_RETRIES = 2
    RETRY_DELAY = 2
    
    # Interview Configuration
    TOTAL_QUESTIONS = 6
    SCORE_RANGE = (0, 5)
    
    # File Paths
    QUESTION_BANK_PATH = "data/question_bank.json"
    TRANSCRIPT_PREFIX = "excel_interview_transcript"
    
    # UI Configuration
    PAGE_TITLE = "Excel Mock Interviewer"
    PAGE_ICON = "📊"
    LAYOUT = "wide"
    
    # Performance Levels
    PERFORMANCE_LEVELS = {
        (0, 1.5): "Beginner",
        (1.5, 2.5): "Novice", 
        (2.5, 3.5): "Intermediate",
        (3.5, 4.5): "Advanced",
        (4.5, 5): "Expert"
    }
    
    @staticmethod
    def get_performance_level(score: float) -> str:
        """Get performance level based on average score"""
        for (min_score, max_score), level in Config.PERFORMANCE_LEVELS.items():
            if min_score <= score < max_score:
                return level
        return "Expert"  # For perfect score of 5.0
