"""
UI components for the Excel Mock Interviewer
"""
import streamlit as st
import datetime
from typing import Dict, List
from ..utils.session_manager import SessionManager
from ..utils.file_manager import FileManager, ScoreCalculator
from ..config.settings import Config


class InterviewUI:
    """Main UI components for the interview application"""
    
    @staticmethod
    def setup_page():
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title=Config.PAGE_TITLE,
            page_icon=Config.PAGE_ICON,
            layout=Config.LAYOUT
        )
    
    @staticmethod
    def show_header():
        """Display application header"""
        st.title(f"{Config.PAGE_ICON} {Config.PAGE_TITLE}")
        st.markdown("""
        Welcome to the **Excel Mock Interviewer**! This AI-powered tool will conduct a comprehensive 
        Excel skills assessment with 6 progressively challenging questions.
        
        **What to expect:**
        - 6 dynamically generated questions covering advanced Excel topics
        - Immediate AI feedback on each answer
        - Detailed performance analysis with personalized recommendations
        - Complete interview transcript download
        """)
    
    @staticmethod
    def show_intro():
        """Display introduction screen with question generation options"""
        st.markdown("---")
        st.markdown("### 🚀 Ready to begin?")
        st.markdown("""
        The interview will cover:
        - Advanced formulas and functions
        - Pivot tables and data analysis
        - Data validation and error handling
        - Real-world Excel scenarios
        """)
        
        st.markdown("### 📝 Question Generation Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fresh_questions = st.button(
                "🤖 Generate Fresh Questions", 
                type="primary",
                help="AI will create brand new questions for this interview"
            )
        
        with col2:
            bank_questions = st.button(
                "📚 Use Question Bank", 
                help="Use pre-defined questions (faster start)"
            )
        
        return fresh_questions, bank_questions
    
    @staticmethod
    def show_progress():
        """Display interview progress"""
        questions = SessionManager.get('questions', [])
        current_idx = SessionManager.get('current_question_index', 0)
        
        if questions:
            progress = current_idx / len(questions)
            st.progress(progress)
            st.markdown(f"**Progress:** Question {current_idx + 1} of {len(questions)}")
    
    @staticmethod
    def display_question(question: Dict):
        """
        Display a question and handle user input
        
        Args:
            question: Question dictionary
        """
        st.markdown(f"### Question {question['id']}/{Config.TOTAL_QUESTIONS}")
        st.markdown(f"**Difficulty Level:** {question.get('difficulty', question['id'])}/{Config.TOTAL_QUESTIONS}")
        st.markdown("---")
        st.markdown(question['question_text'])
        
        # User answer input
        answer_key = f"answer_{question['id']}"
        user_answer = st.text_area(
            "Your Answer:", 
            key=answer_key,
            height=150,
            placeholder="Please provide your detailed answer here..."
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            submit_clicked = st.button("Submit Answer", key=f"submit_{question['id']}")
        
        with col2:
            skip_clicked = st.button("Skip Question", key=f"skip_{question['id']}")
        
        return user_answer, submit_clicked, skip_clicked
    
    @staticmethod
    def show_evaluation(evaluation: Dict):
        """
        Display evaluation results
        
        Args:
            evaluation: Evaluation dictionary
        """
        st.success(f"✅ Answer evaluated! Score: {evaluation['score']}/5")
        
        with st.expander("📋 Detailed Feedback", expanded=True):
            st.markdown(f"**Score:** {evaluation['score']}/5")
            st.markdown(f"**Feedback:** {evaluation['feedback']}")
            st.markdown(f"**Strengths:** {evaluation['strengths']}")
            st.markdown(f"**Areas for Improvement:** {evaluation['areas_for_improvement']}")
            st.markdown(f"**Tip:** {evaluation['tip']}")
    
    @staticmethod
    def show_continue_button():
        """Show continue to next question button"""
        return st.button("Continue to Next Question")
    
    @staticmethod
    def show_sidebar_history():
        """Show previous answers in sidebar"""
        transcript = SessionManager.get('transcript', [])
        
        if transcript:
            with st.sidebar:
                st.markdown("### 📝 Previous Answers")
                for entry in transcript:
                    with st.expander(f"Q{entry['question_id']} (Score: {entry['score']}/5)"):
                        st.markdown(f"**Q:** {entry['question'][:100]}...")
                        if entry['user_answer'] != '[SKIPPED]':
                            st.markdown(f"**A:** {entry['user_answer'][:100]}...")
                        else:
                            st.markdown("**A:** [Question was skipped]")
    
    @staticmethod
    def show_error_message(message: str):
        """Display error message"""
        st.error(f"⚠️ {message}")
    
    @staticmethod
    def show_api_key_error():
        """Display API key configuration error"""
        st.error("""
        🔑 **API Key Required**
        
        Please configure your GEMINI_API_KEY:
        
        **For local development:**
        1. Edit the `.env` file
        2. Replace `your_gemini_api_key_here` with your actual Gemini API key
        
        **For Streamlit Cloud:**
        1. Add `GEMINI_API_KEY` in your app's Secrets management
        
        **Get your free API key:**
        - Visit: https://makersuite.google.com/app/apikey
        """)


class SummaryUI:
    """UI components for interview summary"""
    
    @staticmethod
    def show_completion_header():
        """Display interview completion header"""
        st.markdown("# 🎯 Interview Complete!")
        st.markdown("---")
    
    @staticmethod
    def show_performance_metrics(summary: Dict, transcript: List[Dict]):
        """
        Display performance metrics
        
        Args:
            summary: Interview summary
            transcript: Interview transcript
        """
        metrics = ScoreCalculator.get_performance_metrics(transcript)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Score", f"{metrics['average_score']}/5")
        with col2:
            st.metric("Performance Level", summary.get('performance_level', metrics['performance_level']))
        with col3:
            st.metric("Questions Completed", f"{metrics['questions_attempted']}/{Config.TOTAL_QUESTIONS}")
    
    @staticmethod
    def show_detailed_summary(summary: Dict):
        """
        Display detailed summary
        
        Args:
            summary: Interview summary dictionary
        """
        # Detailed summary
        st.markdown("## 📊 Performance Analysis")
        st.markdown(summary.get('summary', 'Performance summary not available'))
        
        # Strengths
        if summary.get('strengths'):
            st.markdown("### ✅ Your Strengths")
            for strength in summary['strengths']:
                st.markdown(f"• {strength}")
        
        # Improvement areas
        if summary.get('improvement_areas'):
            st.markdown("### 📈 Areas for Improvement")
            for area in summary['improvement_areas']:
                st.markdown(f"• {area}")
        
        # Recommendations
        if summary.get('recommendations'):
            st.markdown("### 💡 Recommendations")
            for rec in summary['recommendations']:
                st.markdown(f"• {rec}")
    
    @staticmethod
    def show_transcript_options(transcript: List[Dict], summary: Dict):
        """
        Show transcript download options
        
        Args:
            transcript: Interview transcript
            summary: Interview summary
        """
        st.markdown("---")
        if st.button("💾 Save Interview Transcript"):
            filename = FileManager.save_transcript_to_csv(transcript, summary)
            st.success(f"✅ Transcript saved as: {filename}")
            
            # Offer download
            try:
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="📥 Download Transcript",
                        data=f.read(),
                        file_name=filename,
                        mime="text/csv"
                    )
            except FileNotFoundError:
                st.error("Failed to prepare download file")
    
    @staticmethod
    def show_restart_option():
        """Show restart interview option"""
        return st.button("🔄 Start New Interview")
