"""
Gemini AI Service for Excel Mock Interviewer
"""
import time
import json
import streamlit as st
import google.generativeai as genai
from typing import Optional, List, Dict
from ..config.settings import Config
from ..config.prompts import PromptTemplates


class GeminiService:
    """Service for interacting with Google's Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini service with API key"""
        self.api_key = Config.get_gemini_api_key()
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise ValueError("Invalid or missing Gemini API key")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def _clean_json_response(self, response_text: str) -> str:
        """
        Clean and sanitize JSON response text
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Cleaned JSON string
        """
        import re
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Remove any text before the first '[' or '{'
        json_start = min(
            response_text.find('[') if response_text.find('[') != -1 else len(response_text),
            response_text.find('{') if response_text.find('{') != -1 else len(response_text)
        )
        if json_start > 0:
            response_text = response_text[json_start:]
        
        # Remove any text after the last ']' or '}'
        json_end = max(response_text.rfind(']'), response_text.rfind('}'))
        if json_end != -1:
            response_text = response_text[:json_end + 1]
        
        # Remove or replace problematic control characters
        response_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', ' ', response_text)
        
        # Fix quote issues in JSON strings
        # This is a more sophisticated approach to handle nested quotes
        lines = response_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Look for JSON string values (text between quotes after colons)
            if '": "' in line or "':" in line:
                # Find string values and escape quotes within them
                parts = line.split('": "')
                if len(parts) > 1:
                    # Process each string value
                    for i in range(1, len(parts)):
                        # Find the end of the string value
                        end_quote = parts[i].rfind('"')
                        if end_quote > 0:
                            string_content = parts[i][:end_quote]
                            rest_of_line = parts[i][end_quote:]
                            
                            # Escape quotes within the string content
                            string_content = string_content.replace('"', '\\"')
                            parts[i] = string_content + rest_of_line
                    
                    line = '": "'.join(parts)
            
            cleaned_lines.append(line)
        
        response_text = '\n'.join(cleaned_lines)
        
        # Additional cleaning
        response_text = response_text.replace('\n', ' ').replace('\r', ' ')
        response_text = re.sub(r'\s+', ' ', response_text)  # Multiple spaces to single space
        
        return response_text.strip()
    
    def _call_gemini(self, prompt: str, max_retries: int = None) -> Optional[str]:
        """
        Make a call to Gemini API with retry logic
        
        Args:
            prompt: The prompt to send to Gemini
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response text or None if failed
        """
        if max_retries is None:
            max_retries = Config.MAX_RETRIES
        
        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(prompt)
                if response.text:
                    # Clean the response text
                    cleaned_text = self._clean_json_response(response.text)
                    return cleaned_text
                else:
                    raise Exception("Empty response from Gemini")
                    
            except Exception as e:
                if attempt == max_retries:
                    if "quota" in str(e).lower() or "limit" in str(e).lower():
                        st.error("API quota exceeded. Please try again later or check your Gemini API limits.")
                    else:
                        st.error(f"Failed to get response from Gemini after {max_retries + 1} attempts: {str(e)}")
                    return None
                time.sleep(Config.RETRY_DELAY)
        
        return None
    
    def _parse_json_with_fallback(self, response_text: str) -> Optional[List[Dict]]:
        """
        Parse JSON with multiple fallback strategies
        
        Args:
            response_text: JSON string to parse
            
        Returns:
            Parsed JSON or None if all strategies fail
        """
        # Strategy 1: Try direct JSON parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Try with quote escaping
        try:
            # Simple quote escaping for common cases
            import re
            
            # Find all string values in JSON and escape quotes within them
            def escape_quotes_in_strings(match):
                full_match = match.group(0)
                key_part = match.group(1)  # The key part
                value_part = match.group(2)  # The value part
                
                # Escape quotes in the value part only
                escaped_value = value_part.replace('"', '\\"')
                return f'{key_part}"{escaped_value}"'
            
            # Pattern to match "key": "value with possible quotes"
            pattern = r'("(?:question_text|model_answer)":\s*")([^"]*(?:"[^"]*")*[^"]*?)("(?:\s*[,\}]))'
            
            fixed_text = re.sub(pattern, escape_quotes_in_strings, response_text)
            return json.loads(fixed_text)
        except (json.JSONDecodeError, Exception):
            pass
        
        # Strategy 3: Manual parsing as last resort
        try:
            return self._manual_json_parse(response_text)
        except Exception:
            return None
    
    def _manual_json_parse(self, response_text: str) -> Optional[List[Dict]]:
        """
        Manual JSON parsing for malformed JSON responses
        
        Args:
            response_text: Malformed JSON string
            
        Returns:
            List of parsed question dictionaries
        """
        import re
        
        questions = []
        
        # Extract each question object manually
        # Look for patterns like { "id": 1, "question_text": "...", "model_answer": "...", "difficulty": 1 }
        
        # Split by question objects
        question_pattern = r'\{\s*"id":\s*(\d+).*?\}'
        matches = re.finditer(question_pattern, response_text, re.DOTALL)
        
        for match in matches:
            question_text = match.group(0)
            
            # Extract individual fields
            id_match = re.search(r'"id":\s*(\d+)', question_text)
            question_match = re.search(r'"question_text":\s*"(.*?)"(?=\s*,\s*"model_answer")', question_text, re.DOTALL)
            answer_match = re.search(r'"model_answer":\s*"(.*?)"(?=\s*,\s*"difficulty")', question_text, re.DOTALL)
            difficulty_match = re.search(r'"difficulty":\s*(\d+)', question_text)
            
            if id_match and question_match and answer_match and difficulty_match:
                question = {
                    "id": int(id_match.group(1)),
                    "question_text": question_match.group(1).replace('\\"', '"'),
                    "model_answer": answer_match.group(1).replace('\\"', '"'),
                    "difficulty": int(difficulty_match.group(1))
                }
                questions.append(question)
        
        return questions if questions else None

    def generate_questions(self, n: int = 6) -> Optional[List[Dict]]:
        """
        Generate interview questions using Gemini API
        
        Args:
            n: Number of questions to generate
            
        Returns:
            List of question dictionaries or None if failed
        """
        st.info("🤖 Generating fresh interview questions using AI...")
        
        response = self._call_gemini(PromptTemplates.QUESTION_GENERATION_PROMPT)
        if not response:
            return None
        
        # Try parsing with fallback strategies
        questions = self._parse_json_with_fallback(response)
        
        if questions:
            # Validate the response structure
            if not isinstance(questions, list):
                st.error("Invalid response format: Expected a list of questions")
                return None
                
            if len(questions) == n:
                st.success(f"✅ Generated {len(questions)} unique questions successfully!")
                return questions
            else:
                st.warning(f"Generated {len(questions)} questions instead of {n}. Using what we have.")
                return questions[:n] if len(questions) > n else questions
        else:
            st.error("Failed to parse generated questions with all strategies")
            
            # Show debug information
            response_preview = response[:500] + "..." if len(response) > 500 else response
            with st.expander("🔍 Debug Information (Click to expand)"):
                st.code(response_preview, language="text")
                st.write(f"Response length: {len(response)} characters")
            
            return None
    
    def evaluate_answer(self, question: Dict, user_answer: str) -> Optional[Dict]:
        """
        Evaluate a user's answer using Gemini API
        
        Args:
            question: Question dictionary with question_text and model_answer
            user_answer: User's answer text
            
        Returns:
            Evaluation dictionary or None if failed
        """
        evaluation_prompt = PromptTemplates.EVALUATION_PROMPT_TEMPLATE.format(
            persona=PromptTemplates.INTERVIEWER_PERSONA,
            question=question['question_text'],
            answer=user_answer,
            model_answer=question['model_answer']
        )
        
        response = self._call_gemini(evaluation_prompt)
        if not response:
            return None
        
        # Try parsing with fallback strategies
        evaluation = self._parse_evaluation_with_fallback(response)
        
        if evaluation:
            # Validate and sanitize required fields
            required_fields = ['score', 'feedback', 'tip', 'strengths', 'areas_for_improvement']
            for field in required_fields:
                if field not in evaluation:
                    evaluation[field] = f"Information not provided for {field}"
            
            # Ensure score is an integer between 0-5
            try:
                evaluation['score'] = max(0, min(5, int(evaluation['score'])))
            except:
                evaluation['score'] = 3  # Default to middle score
            
            return evaluation
        else:
            st.error(f"Failed to parse evaluation response. Raw response: {response[:200]}...")
            return None
    
    def _parse_evaluation_with_fallback(self, response_text: str) -> Optional[Dict]:
        """
        Parse evaluation JSON with multiple fallback strategies
        
        Args:
            response_text: JSON string to parse
            
        Returns:
            Parsed evaluation dict or None if all strategies fail
        """
        # Strategy 1: Try direct JSON parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Try to complete incomplete JSON
        try:
            # If JSON is cut off, try to fix it
            fixed_response = self._fix_incomplete_json(response_text)
            if fixed_response:
                return json.loads(fixed_response)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Manual parsing for evaluation
        try:
            return self._manual_evaluation_parse(response_text)
        except Exception:
            return None
    
    def _fix_incomplete_json(self, response_text: str) -> Optional[str]:
        """
        Try to fix incomplete JSON responses
        
        Args:
            response_text: Incomplete JSON string
            
        Returns:
            Fixed JSON string or None
        """
        import re
        
        # Clean the response first
        response_text = self._clean_json_response(response_text)
        
        # If it starts with { but doesn't end with }, try to complete it
        if response_text.startswith('{') and not response_text.endswith('}'):
            # Count open and closed braces
            open_braces = response_text.count('{')
            close_braces = response_text.count('}')
            
            if open_braces > close_braces:
                # Add missing closing braces
                response_text += '}' * (open_braces - close_braces)
        
        # If it ends with incomplete string, try to close it
        if response_text.endswith('"') == False and '"' in response_text:
            # Find the last complete field and try to close it
            last_quote = response_text.rfind('"')
            if last_quote > 0:
                # Check if we're in the middle of a value
                after_quote = response_text[last_quote + 1:]
                if ':' not in after_quote and '}' not in after_quote:
                    # We're probably in an incomplete string value
                    response_text += '"}'
        
        return response_text
    
    def _manual_evaluation_parse(self, response_text: str) -> Optional[Dict]:
        """
        Manual parsing for evaluation responses
        
        Args:
            response_text: Response text to parse
            
        Returns:
            Evaluation dictionary
        """
        import re
        
        evaluation = {}
        
        # Extract score
        score_match = re.search(r'"score":\s*(\d+)', response_text)
        if score_match:
            evaluation['score'] = int(score_match.group(1))
        else:
            evaluation['score'] = 3  # Default score
        
        # Extract feedback
        feedback_match = re.search(r'"feedback":\s*"([^"]*(?:\\"[^"]*)*)', response_text)
        if feedback_match:
            evaluation['feedback'] = feedback_match.group(1).replace('\\"', '"')
        else:
            evaluation['feedback'] = "Good attempt! Your answer shows understanding of the concept."
        
        # Extract tip
        tip_match = re.search(r'"tip":\s*"([^"]*(?:\\"[^"]*)*)', response_text)
        if tip_match:
            evaluation['tip'] = tip_match.group(1).replace('\\"', '"')
        else:
            evaluation['tip'] = "Continue practicing to improve your Excel skills."
        
        # Extract strengths
        strengths_match = re.search(r'"strengths":\s*"([^"]*(?:\\"[^"]*)*)', response_text)
        if strengths_match:
            evaluation['strengths'] = strengths_match.group(1).replace('\\"', '"')
        else:
            evaluation['strengths'] = "Shows knowledge of Excel functions"
        
        # Extract areas for improvement
        improvement_match = re.search(r'"areas_for_improvement":\s*"([^"]*(?:\\"[^"]*)*)', response_text)
        if improvement_match:
            evaluation['areas_for_improvement'] = improvement_match.group(1).replace('\\"', '"')
        else:
            evaluation['areas_for_improvement'] = "Practice providing more complete answers with examples"
        
        return evaluation
    
    def generate_summary(self, transcript: List[Dict]) -> Optional[Dict]:
        """
        Generate interview summary using Gemini API
        
        Args:
            transcript: List of Q&A entries
            
        Returns:
            Summary dictionary or None if failed
        """
        # Prepare Q&A pairs for summary
        qa_pairs = []
        for entry in transcript:
            qa_pair = f"""
Question {entry['question_id']}: {entry['question']}
Answer: {entry['user_answer']}
Score: {entry['score']}/5
"""
            qa_pairs.append(qa_pair)
        
        summary_prompt = PromptTemplates.SUMMARY_PROMPT_TEMPLATE.format(
            persona=PromptTemplates.INTERVIEWER_PERSONA,
            qa_pairs='\n'.join(qa_pairs)
        )
        
        response = self._call_gemini(summary_prompt)
        if not response:
            return None
        
        try:
            summary = json.loads(response)
            return summary
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse summary response: {e}")
            return None
