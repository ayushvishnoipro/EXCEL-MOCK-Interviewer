import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import os
import datetime
import random
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
api_key = None

try:
    # Try to get API key from Streamlit secrets first (for cloud deployment)
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    try:
        # Fallback to environment variable (for local development)
        api_key = os.getenv("GEMINI_API_KEY")
    except:
        pass

if not api_key or api_key == "your_gemini_api_key_here":
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
    st.stop()

genai.configure(api_key=api_key)

# System prompts and configurations
INTERVIEWER_PERSONA = """
You are an expert Excel interviewer conducting a professional skills assessment. 
You are thorough, encouraging, and provide constructive feedback. 
Your responses must always be in valid JSON format as specified.
"""

QUESTION_GENERATION_PROMPT = """
You are an Excel interview question generator. 
Produce a JSON array of exactly 6 distinct interview questions about advanced Excel skills, 
ordered from easiest to hardest (difficulty levels 1-6).

Focus on these Excel areas:
- Formulas and functions (VLOOKUP, INDEX/MATCH, nested IF statements)
- Pivot tables and data analysis
- Data validation and conditional formatting
- Error handling and troubleshooting
- Advanced features (Power Query, macros basics)
- Real-world scenarios and problem-solving

Each question should have:
- id: integer from 1 to 6
- question_text: detailed question description
- model_answer: comprehensive expected answer
- difficulty: integer from 1 to 6

Return ONLY the JSON array, no additional text.
"""

EVALUATION_PROMPT_TEMPLATE = """
{persona}

Evaluate this Excel interview answer and respond with ONLY a valid JSON object, no additional text.

Question: {question}
User Answer: {answer}
Model Answer: {model_answer}

Respond with exactly this JSON format:
{{
    "score": 3,
    "feedback": "detailed feedback on the answer quality",
    "tip": "helpful tip for improvement or reinforcement",
    "strengths": "what the user did well",
    "areas_for_improvement": "specific areas to work on"
}}

Requirements:
- score: integer from 0 to 5 (0=completely wrong, 5=excellent)
- All text fields must be strings, not arrays
- Be encouraging but honest
- Consider partial credit for incomplete but correct approaches
- Return ONLY the JSON object, no markdown formatting, no additional text
"""

SUMMARY_PROMPT_TEMPLATE = """
{persona}

Generate a comprehensive interview summary based on these Q&A pairs and scores:

{qa_pairs}

Provide a JSON response with:
{{
    "overall_score": (average score rounded to 1 decimal),
    "performance_level": "Beginner/Intermediate/Advanced/Expert",
    "strengths": ["list of key strengths demonstrated"],
    "improvement_areas": ["specific areas needing development"],
    "recommendations": ["actionable next steps for skill development"],
    "summary": "overall performance narrative"
}}
"""

def call_gemini(prompt: str, max_retries: int = 2) -> str:
    """Call Gemini API with retry logic and error handling."""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(prompt)
            if response.text:
                # Clean the response text
                response_text = response.text.strip()
                
                # Remove any markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()
                elif response_text.startswith("```"):
                    response_text = response_text.replace("```", "").strip()
                
                return response_text
            else:
                raise Exception("Empty response from Gemini")
        except Exception as e:
            if attempt == max_retries:
                if "quota" in str(e).lower() or "limit" in str(e).lower():
                    st.error("API quota exceeded. Please try again later or check your Gemini API limits.")
                else:
                    st.error(f"Failed to get response from Gemini after {max_retries + 1} attempts: {str(e)}")
                return None
            time.sleep(2)  # Slightly longer delay before retry
    return None

def generate_questions(n: int = 6) -> list:
    """Generate interview questions using Gemini API."""
    st.info("🤖 Generating fresh interview questions using AI...")
    
    response = call_gemini(QUESTION_GENERATION_PROMPT)
    if not response:
        return None
    
    try:
        questions = json.loads(response)
        if len(questions) == n:
            return questions
        else:
            st.warning(f"Generated {len(questions)} questions instead of {n}. Using what we have.")
            return questions[:n] if len(questions) > n else questions
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse generated questions: {e}")
        return None

def load_or_generate_questions() -> list:
    """Load questions from file or generate new ones."""
    question_bank_path = "question_bank.json"
    
    if os.path.exists(question_bank_path):
        try:
            with open(question_bank_path, 'r') as f:
                questions = json.load(f)
            st.success(f"✅ Loaded {len(questions)} questions from question bank")
            return questions
        except Exception as e:
            st.warning(f"Failed to load question bank: {e}. Generating new questions...")
    
    questions = generate_questions(6)
    return questions

def save_transcript_to_csv(transcript: list, summary: dict):
    """Save interview transcript and summary to CSV file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"excel_interview_transcript_{timestamp}.csv"
    
    # Prepare data for CSV
    csv_data = []
    
    # Add header row
    csv_data.append({
        'timestamp': datetime.datetime.now().isoformat(),
        'section': 'INTERVIEW_START',
        'question_id': '',
        'question': 'Excel Skills Interview Session',
        'user_answer': '',
        'score': '',
        'feedback': '',
        'tip': ''
    })
    
    # Add Q&A data
    for i, entry in enumerate(transcript):
        csv_data.append({
            'timestamp': entry.get('timestamp', ''),
            'section': 'QUESTION_ANSWER',
            'question_id': entry.get('question_id', i+1),
            'question': entry.get('question', ''),
            'user_answer': entry.get('user_answer', ''),
            'score': entry.get('score', ''),
            'feedback': entry.get('feedback', ''),
            'tip': entry.get('tip', '')
        })
    
    # Add summary
    csv_data.append({
        'timestamp': datetime.datetime.now().isoformat(),
        'section': 'SUMMARY',
        'question_id': '',
        'question': 'Overall Performance Summary',
        'user_answer': summary.get('summary', ''),
        'score': summary.get('overall_score', ''),
        'feedback': f"Strengths: {', '.join(summary.get('strengths', []))}",
        'tip': f"Recommendations: {', '.join(summary.get('recommendations', []))}"
    })
    
    df = pd.DataFrame(csv_data)
    df.to_csv(filename, index=False)
    
    return filename

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'questions' not in st.session_state:
        st.session_state.questions = None
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'transcript' not in st.session_state:
        st.session_state.transcript = []
    if 'interview_completed' not in st.session_state:
        st.session_state.interview_completed = False
    if 'summary' not in st.session_state:
        st.session_state.summary = None

def display_question(question: dict):
    """Display a question and handle user input."""
    st.markdown(f"### Question {question['id']}/6")
    st.markdown(f"**Difficulty Level:** {question.get('difficulty', question['id'])}/6")
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
        if st.button("Submit Answer", key=f"submit_{question['id']}"):
            if user_answer.strip():
                evaluate_answer(question, user_answer)
            else:
                st.warning("Please provide an answer before submitting.")
    
    with col2:
        if st.button("Skip Question", key=f"skip_{question['id']}"):
            skip_question(question)

def evaluate_answer(question: dict, user_answer: str):
    """Evaluate user's answer using Gemini API."""
    with st.spinner("🤖 Evaluating your answer..."):
        evaluation_prompt = EVALUATION_PROMPT_TEMPLATE.format(
            persona=INTERVIEWER_PERSONA,
            question=question['question_text'],
            answer=user_answer,
            model_answer=question['model_answer']
        )
        
        response = call_gemini(evaluation_prompt)
        if not response:
            st.error("Failed to evaluate answer. Please try again.")
            return
        
        try:
            # Try to parse the JSON response
            evaluation = json.loads(response)
            
            # Validate required fields
            required_fields = ['score', 'feedback', 'tip', 'strengths', 'areas_for_improvement']
            for field in required_fields:
                if field not in evaluation:
                    evaluation[field] = f"Information not provided for {field}"
            
            # Ensure score is an integer between 0-5
            try:
                evaluation['score'] = max(0, min(5, int(evaluation['score'])))
            except:
                evaluation['score'] = 0
            
            # Display evaluation
            st.success(f"✅ Answer evaluated! Score: {evaluation['score']}/5")
            
            with st.expander("📋 Detailed Feedback", expanded=True):
                st.markdown(f"**Score:** {evaluation['score']}/5")
                st.markdown(f"**Feedback:** {evaluation['feedback']}")
                st.markdown(f"**Strengths:** {evaluation['strengths']}")
                st.markdown(f"**Areas for Improvement:** {evaluation['areas_for_improvement']}")
                st.markdown(f"**Tip:** {evaluation['tip']}")
            
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
            
            st.session_state.transcript.append(transcript_entry)
            
            # Move to next question
            st.session_state.current_question_index += 1
            
            if st.session_state.current_question_index >= len(st.session_state.questions):
                st.session_state.interview_completed = True
                st.rerun()
            else:
                if st.button("Continue to Next Question"):
                    st.rerun()
                
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse evaluation response. Raw response: {response[:200]}...")
            st.info("Using fallback evaluation...")
            
            # Fallback evaluation
            fallback_evaluation = {
                'score': 3,
                'feedback': 'Your answer has been received. Due to a parsing error, we cannot provide detailed feedback at this time.',
                'tip': 'Please review Excel best practices and try the next question.',
                'strengths': 'Answer provided',
                'areas_for_improvement': 'Review the topic area'
            }
            
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
            
            st.session_state.transcript.append(transcript_entry)
            st.session_state.current_question_index += 1
            
            if st.session_state.current_question_index >= len(st.session_state.questions):
                st.session_state.interview_completed = True
                st.rerun()
            else:
                if st.button("Continue to Next Question"):
                    st.rerun()

def skip_question(question: dict):
    """Skip current question and move to next."""
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
    
    st.session_state.transcript.append(transcript_entry)
    st.session_state.current_question_index += 1
    
    if st.session_state.current_question_index >= len(st.session_state.questions):
        st.session_state.interview_completed = True
    
    st.rerun()

def generate_summary():
    """Generate interview summary using Gemini API."""
    if st.session_state.summary:
        return st.session_state.summary
    
    with st.spinner("🤖 Generating your performance summary..."):
        # Prepare Q&A pairs for summary
        qa_pairs = []
        for entry in st.session_state.transcript:
            qa_pair = f"""
Question {entry['question_id']}: {entry['question']}
Answer: {entry['user_answer']}
Score: {entry['score']}/5
"""
            qa_pairs.append(qa_pair)
        
        summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(
            persona=INTERVIEWER_PERSONA,
            qa_pairs='\n'.join(qa_pairs)
        )
        
        response = call_gemini(summary_prompt)
        if not response:
            st.error("Failed to generate summary.")
            return None
        
        try:
            summary = json.loads(response)
            st.session_state.summary = summary
            return summary
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse summary response: {e}")
            return None

def display_summary():
    """Display interview summary and save transcript."""
    summary = generate_summary()
    if not summary:
        return
    
    st.markdown("# 🎯 Interview Complete!")
    st.markdown("---")
    
    # Overall performance
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{summary['overall_score']}/5")
    with col2:
        st.metric("Performance Level", summary['performance_level'])
    with col3:
        total_questions = len(st.session_state.transcript)
        st.metric("Questions Completed", f"{total_questions}/6")
    
    # Detailed summary
    st.markdown("## 📊 Performance Analysis")
    st.markdown(summary['summary'])
    
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
    
    # Save transcript
    st.markdown("---")
    if st.button("💾 Save Interview Transcript"):
        filename = save_transcript_to_csv(st.session_state.transcript, summary)
        st.success(f"✅ Transcript saved as: {filename}")
        
        # Offer download
        with open(filename, 'rb') as f:
            st.download_button(
                label="📥 Download Transcript",
                data=f.read(),
                file_name=filename,
                mime="text/csv"
            )
    
    # Restart option
    if st.button("🔄 Start New Interview"):
        # Reset session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Excel Mock Interviewer",
        page_icon="📊",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Header
    st.title("📊 Excel Mock Interviewer")
    st.markdown("""
    Welcome to the **Excel Mock Interviewer**! This AI-powered tool will conduct a comprehensive 
    Excel skills assessment with 6 progressively challenging questions.
    
    **What to expect:**
    - 6 dynamically generated questions covering advanced Excel topics
    - Immediate AI feedback on each answer
    - Detailed performance analysis with personalized recommendations
    - Complete interview transcript download
    """)
    
    # Interview flow
    if not st.session_state.interview_started:
        st.markdown("---")
        st.markdown("### 🚀 Ready to begin?")
        st.markdown("""
        The interview will cover:
        - Advanced formulas and functions
        - Pivot tables and data analysis
        - Data validation and error handling
        - Real-world Excel scenarios
        """)
        
        if st.button("🎯 Start Interview", type="primary"):
            questions = load_or_generate_questions()
            if questions:
                st.session_state.questions = questions
                st.session_state.interview_started = True
                st.rerun()
            else:
                st.error("Failed to load questions. Please try again.")
    
    elif st.session_state.interview_completed:
        display_summary()
    
    elif st.session_state.questions:
        # Display current question
        current_idx = st.session_state.current_question_index
        if current_idx < len(st.session_state.questions):
            current_question = st.session_state.questions[current_idx]
            
            # Progress indicator
            progress = (current_idx) / len(st.session_state.questions)
            st.progress(progress)
            st.markdown(f"**Progress:** Question {current_idx + 1} of {len(st.session_state.questions)}")
            
            display_question(current_question)
            
            # Show previous answers in sidebar
            if st.session_state.transcript:
                with st.sidebar:
                    st.markdown("### 📝 Previous Answers")
                    for entry in st.session_state.transcript:
                        with st.expander(f"Q{entry['question_id']} (Score: {entry['score']}/5)"):
                            st.markdown(f"**Q:** {entry['question'][:100]}...")
                            st.markdown(f"**A:** {entry['user_answer'][:100]}...")

if __name__ == "__main__":
    main()
