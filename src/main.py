"""
Main application controller for Excel Mock Interviewer
"""
import streamlit as st
import datetime
from typing import Dict

from .services.gemini_service import GeminiService
from .services.question_service import QuestionService
from .ui.components import InterviewUI, SummaryUI
from .utils.session_manager import SessionManager
from .utils.file_manager import FileManager
from .config.settings import Config


class ExcelInterviewApp:
    """Main application controller"""
    
    def __init__(self):
        """Initialize the application"""
        self.setup_services()
        SessionManager.initialize()
    
    def setup_services(self):
        """Initialize services"""
        try:
            # Initialize Gemini service
            if 'gemini_service' not in st.session_state or st.session_state.gemini_service is None:
                st.session_state.gemini_service = GeminiService()
            
            # Initialize question service
            if 'question_service' not in st.session_state or st.session_state.question_service is None:
                st.session_state.question_service = QuestionService(st.session_state.gemini_service)
                
        except ValueError as e:
            InterviewUI.show_api_key_error()
            st.stop()
        except Exception as e:
            st.error(f"Failed to initialize services: {e}")
            st.stop()
    
    def start_interview(self, use_fresh_questions: bool = True):
        """
        Start a new interview
        
        Args:
            use_fresh_questions: If True, generate fresh questions; if False, use question bank
        """
        if use_fresh_questions:
            st.info("🤖 Generating fresh questions for your unique interview experience...")
            questions = st.session_state.question_service.generate_fresh_questions()
        else:
            st.info("📚 Loading questions from question bank...")
            questions = st.session_state.question_service.get_random_questions_from_bank()
            if not questions:
                # Fallback to fresh generation if bank is empty
                st.warning("Question bank unavailable. Generating fresh questions...")
                questions = st.session_state.question_service.generate_fresh_questions()
        
        if questions:
            if st.session_state.question_service.validate_questions(questions):
                SessionManager.set('questions', questions)
                SessionManager.set('interview_started', True)
                st.success(f"✅ {len(questions)} questions ready! Let's begin your interview.")
                st.rerun()
            else:
                InterviewUI.show_error_message("Invalid question format. Using fallback questions.")
                fallback_questions = st.session_state.question_service.get_fallback_questions()
                SessionManager.set('questions', fallback_questions)
                SessionManager.set('interview_started', True)
                st.rerun()
        else:
            InterviewUI.show_error_message("Failed to load questions. Please try again.")
    
    def handle_answer_submission(self, question: Dict, user_answer: str):
        """Handle user answer submission"""
        if not user_answer.strip():
            st.warning("Please provide an answer before submitting.")
            return
        
        with st.spinner("🤖 Evaluating your answer..."):
            evaluation = st.session_state.gemini_service.evaluate_answer(question, user_answer)
            
            if evaluation:
                # Show evaluation
                InterviewUI.show_evaluation(evaluation)
                
                # Save to transcript
                transcript_entry = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'question_id': question['id'],
                    'question': question['question_text'],
                    'user_answer': user_answer,
                    'model_answer': question['model_answer'],
                    'score': evaluation['score'],
                    'feedback': evaluation['feedback'],
                    'tip': evaluation['tip'],
                    'strengths': evaluation['strengths'],
                    'areas_for_improvement': evaluation['areas_for_improvement']
                }
                
                SessionManager.add_to_transcript(transcript_entry)
                SessionManager.increment_question_index()
                
                if SessionManager.is_interview_complete():
                    SessionManager.set('interview_completed', True)
                    st.rerun()
                else:
                    if InterviewUI.show_continue_button():
                        st.rerun()
            else:
                # Use intelligent fallback evaluation based on the answer
                self.handle_smart_fallback_evaluation(question, user_answer)
    
    def handle_smart_fallback_evaluation(self, question: Dict, user_answer: str):
        """Handle evaluation with smart fallback when AI service fails"""
        st.info("Using intelligent fallback evaluation...")
        
        # Provide a more intelligent fallback based on answer content
        answer_lower = user_answer.lower().strip()
        
        # Basic scoring logic based on answer content
        score = 3  # Default middle score
        feedback = "Your answer demonstrates understanding of the concept."
        tip = "Consider providing more specific details and examples."
        strengths = "Shows knowledge of Excel concepts"
        areas_for_improvement = "Include more detailed explanations"
        
        # Simple keyword-based evaluation for common Excel functions
        if any(keyword in answer_lower for keyword in ['sumif', 'countif', 'vlookup', 'index', 'match']):
            score = max(score, 4)
            feedback = "Good use of Excel functions in your answer."
            strengths = "Correctly identified relevant Excel functions"
        
        if any(keyword in answer_lower for keyword in ['formula', 'function', '=', 'range']):
            score = max(score, 3)
            strengths = "Shows understanding of Excel formula concepts"
        
        # Check if answer is too brief
        if len(answer_lower) < 20:
            score = min(score, 2)
            areas_for_improvement = "Provide more detailed explanations"
            tip = "Try to explain the steps or reasoning behind your answer"
        
        fallback_evaluation = {
            'score': score,
            'feedback': feedback,
            'tip': tip,
            'strengths': strengths,
            'areas_for_improvement': areas_for_improvement
        }
        
        InterviewUI.show_evaluation(fallback_evaluation)
        
        # Save fallback to transcript
        transcript_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'question_id': question['id'],
            'question': question['question_text'],
            'user_answer': user_answer,
            'model_answer': question['model_answer'],
            'score': fallback_evaluation['score'],
            'feedback': fallback_evaluation['feedback'],
            'tip': fallback_evaluation['tip'],
            'strengths': fallback_evaluation['strengths'],
            'areas_for_improvement': fallback_evaluation['areas_for_improvement']
        }
        
        SessionManager.add_to_transcript(transcript_entry)
        SessionManager.increment_question_index()
        
        if SessionManager.is_interview_complete():
            SessionManager.set('interview_completed', True)
            st.rerun()
        else:
            if InterviewUI.show_continue_button():
                st.rerun()
    
    def handle_fallback_evaluation(self, question: Dict, user_answer: str):
        """Handle evaluation when AI service fails"""
        st.info("Using fallback evaluation...")
        
        fallback_evaluation = {
            'score': 3,
            'feedback': 'Your answer has been received. Due to a technical issue, we cannot provide detailed feedback at this time.',
            'tip': 'Please review Excel best practices and continue with the next question.',
            'strengths': 'Answer provided',
            'areas_for_improvement': 'Review the topic area'
        }
        
        InterviewUI.show_evaluation(fallback_evaluation)
        
        # Save fallback to transcript
        transcript_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'question_id': question['id'],
            'question': question['question_text'],
            'user_answer': user_answer,
            'model_answer': question['model_answer'],
            'score': fallback_evaluation['score'],
            'feedback': fallback_evaluation['feedback'],
            'tip': fallback_evaluation['tip'],
            'strengths': fallback_evaluation['strengths'],
            'areas_for_improvement': fallback_evaluation['areas_for_improvement']
        }
        
        SessionManager.add_to_transcript(transcript_entry)
        SessionManager.increment_question_index()
        
        if SessionManager.is_interview_complete():
            SessionManager.set('interview_completed', True)
            st.rerun()
        else:
            if InterviewUI.show_continue_button():
                st.rerun()
    
    def handle_skip_question(self, question: Dict):
        """Handle question skip"""
        transcript_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'question_id': question['id'],
            'question': question['question_text'],
            'user_answer': '[SKIPPED]',
            'model_answer': question['model_answer'],
            'score': 0,
            'feedback': 'Question was skipped',
            'tip': 'Consider reviewing this topic area',
            'strengths': 'N/A',
            'areas_for_improvement': 'Review this Excel concept'
        }
        
        SessionManager.add_to_transcript(transcript_entry)
        SessionManager.increment_question_index()
        
        if SessionManager.is_interview_complete():
            SessionManager.set('interview_completed', True)
        
        st.rerun()
    
    def generate_summary(self):
        """Generate and return interview summary"""
        if SessionManager.get('summary'):
            return SessionManager.get('summary')
        
        transcript = SessionManager.get('transcript', [])
        if not transcript:
            return None
        
        with st.spinner("🤖 Generating your performance summary..."):
            summary = st.session_state.gemini_service.generate_summary(transcript)
            if summary:
                SessionManager.set('summary', summary)
                return summary
            else:
                # Fallback summary
                from .utils.file_manager import ScoreCalculator
                metrics = ScoreCalculator.get_performance_metrics(transcript)
                
                fallback_summary = {
                    'overall_score': metrics['average_score'],
                    'performance_level': metrics['performance_level'],
                    'strengths': ['Completed the interview', 'Demonstrated Excel knowledge'],
                    'improvement_areas': ['Continue learning Excel concepts'],
                    'recommendations': ['Practice with real-world Excel scenarios', 'Review advanced Excel features'],
                    'summary': f'You completed {metrics["questions_attempted"]} questions with an average score of {metrics["average_score"]}/5.'
                }
                
                SessionManager.set('summary', fallback_summary)
                return fallback_summary
    
    def run(self):
        """Main application entry point"""
        # Setup page
        InterviewUI.setup_page()
        
        # Show header
        InterviewUI.show_header()
        
        # Main application flow
        if not SessionManager.get('interview_started'):
            # Show intro screen with question generation options
            fresh_questions, bank_questions = InterviewUI.show_intro()
            
            if fresh_questions:
                self.start_interview(use_fresh_questions=True)
            elif bank_questions:
                self.start_interview(use_fresh_questions=False)
        
        elif SessionManager.get('interview_completed'):
            # Show summary
            self.show_summary()
        
        else:
            # Show current question
            self.show_current_question()
        
        # Show sidebar history
        InterviewUI.show_sidebar_history()
    
    def show_current_question(self):
        """Display current question and handle interactions"""
        current_question = SessionManager.get_current_question()
        
        if current_question:
            # Show progress
            InterviewUI.show_progress()
            
            # Display question and get user input
            user_answer, submit_clicked, skip_clicked = InterviewUI.display_question(current_question)
            
            # Handle button clicks
            if submit_clicked:
                self.handle_answer_submission(current_question, user_answer)
            elif skip_clicked:
                self.handle_skip_question(current_question)
        else:
            InterviewUI.show_error_message("No questions available")
    
    def show_summary(self):
        """Display interview summary"""
        summary = self.generate_summary()
        transcript = SessionManager.get('transcript', [])
        
        if summary:
            # Show completion header
            SummaryUI.show_completion_header()
            
            # Show performance metrics
            SummaryUI.show_performance_metrics(summary, transcript)
            
            # Show detailed summary
            SummaryUI.show_detailed_summary(summary)
            
            # Show transcript options
            SummaryUI.show_transcript_options(transcript, summary)
            
            # Show restart option
            if SummaryUI.show_restart_option():
                SessionManager.reset()
                st.rerun()
        else:
            InterviewUI.show_error_message("Failed to generate summary")


def main():
    """Application entry point"""
    app = ExcelInterviewApp()
    app.run()


if __name__ == "__main__":
    main()
