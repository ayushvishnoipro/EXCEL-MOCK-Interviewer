"""
Session state management utilities
"""
import streamlit as st
from typing import Any, Dict, List


class SessionManager:
    """Manages Streamlit session state for the interview"""
    
    @staticmethod
    def initialize():
        """Initialize all session state variables"""
        defaults = {
            'interview_started': False,
            'questions': None,
            'current_question_index': 0,
            'transcript': [],
            'interview_completed': False,
            'summary': None,
            'gemini_service': None,
            'question_service': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def reset():
        """Reset session state for new interview"""
        keys_to_reset = [
            'interview_started',
            'questions', 
            'current_question_index',
            'transcript',
            'interview_completed',
            'summary'
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                if key == 'current_question_index':
                    st.session_state[key] = 0
                elif key == 'transcript':
                    st.session_state[key] = []
                else:
                    st.session_state[key] = None if key != 'interview_started' and key != 'interview_completed' else False
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get value from session state"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        """Set value in session state"""
        st.session_state[key] = value
    
    @staticmethod
    def increment_question_index():
        """Move to next question"""
        st.session_state.current_question_index += 1
    
    @staticmethod
    def add_to_transcript(entry: Dict):
        """Add entry to interview transcript"""
        if 'transcript' not in st.session_state:
            st.session_state.transcript = []
        st.session_state.transcript.append(entry)
    
    @staticmethod
    def is_interview_complete() -> bool:
        """Check if interview is complete"""
        if not st.session_state.get('questions'):
            return False
        return st.session_state.get('current_question_index', 0) >= len(st.session_state.questions)
    
    @staticmethod
    def get_current_question() -> Dict:
        """Get current question"""
        questions = st.session_state.get('questions', [])
        index = st.session_state.get('current_question_index', 0)
        
        if 0 <= index < len(questions):
            return questions[index]
        return None
    
    @staticmethod
    def get_progress() -> float:
        """Get interview progress as percentage"""
        questions = st.session_state.get('questions', [])
        index = st.session_state.get('current_question_index', 0)
        
        if not questions:
            return 0.0
        return (index / len(questions)) * 100
