"""
Question Management Service for Excel Mock Interviewer
"""
import json
import os
from typing import List, Dict, Optional
from ..config.settings import Config


class QuestionService:
    """Service for managing interview questions"""
    
    def __init__(self, gemini_service=None):
        """
        Initialize question service
        
        Args:
            gemini_service: Instance of GeminiService for generating questions
        """
        self.gemini_service = gemini_service
        self.question_bank_path = Config.QUESTION_BANK_PATH
    
    def load_from_bank(self) -> Optional[List[Dict]]:
        """
        Load questions from question bank file
        
        Returns:
            List of questions or None if file doesn't exist or error
        """
        if os.path.exists(self.question_bank_path):
            try:
                with open(self.question_bank_path, 'r') as f:
                    questions = json.load(f)
                return questions
            except Exception as e:
                print(f"Failed to load question bank: {e}")
                return None
        return None
    
    def save_to_bank(self, questions: List[Dict]) -> bool:
        """
        Save questions to question bank file
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.question_bank_path), exist_ok=True)
            
            with open(self.question_bank_path, 'w') as f:
                json.dump(questions, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save question bank: {e}")
            return False
    
    def get_questions(self, force_generate: bool = True) -> Optional[List[Dict]]:
        """
        Get interview questions - generate fresh questions for each interview
        
        Args:
            force_generate: If True, generate new questions instead of loading from bank
            
        Returns:
            List of questions or None if failed
        """
        # Always generate fresh questions by default for unique interviews
        if force_generate and self.gemini_service:
            questions = self.gemini_service.generate_questions(Config.TOTAL_QUESTIONS)
            if questions:
                return questions
        
        # Fallback to question bank only if generation fails
        questions = self.load_from_bank()
        if questions:
            return questions
        
        # Last resort: use hardcoded fallback questions
        return self.get_fallback_questions()
    
    def validate_questions(self, questions: List[Dict]) -> bool:
        """
        Validate question format
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(questions, list):
            return False
        
        required_fields = ['id', 'question_text', 'model_answer']
        
        for question in questions:
            if not isinstance(question, dict):
                return False
            
            for field in required_fields:
                if field not in question:
                    return False
                
            # Validate ID is integer
            try:
                int(question['id'])
            except (ValueError, TypeError):
                return False
        
        return True
    
    def get_fallback_questions(self) -> List[Dict]:
        """
        Get hardcoded fallback questions if all else fails
        
        Returns:
            List of basic fallback questions
        """
        return [
            {
                "id": 1,
                "question_text": "Explain the difference between VLOOKUP and INDEX/MATCH functions. When would you use one over the other?",
                "model_answer": "VLOOKUP searches in the first column and returns from specified column. INDEX/MATCH is more flexible - can look left, better performance, dynamic columns. Use VLOOKUP for simple right lookups, INDEX/MATCH for complex scenarios.",
                "difficulty": 1
            },
            {
                "id": 2,
                "question_text": "How would you create a pivot table to analyze sales data by region and month?",
                "model_answer": "Select data > Insert Pivot Table. Drag Date to Rows (group by month), Region to Columns, Sales to Values. Add slicers for filtering. Format as currency and add conditional formatting.",
                "difficulty": 2
            },
            {
                "id": 3,
                "question_text": "What are common Excel errors and how do you handle them?",
                "model_answer": "Common errors: #N/A (IFERROR, IFNA), #VALUE! (data type validation), #REF! (INDIRECT), #DIV/0! (IF checks). Use error handling functions and data validation.",
                "difficulty": 3
            },
            {
                "id": 4,
                "question_text": "Describe how to set up data validation with dependent dropdowns.",
                "model_answer": "Create named ranges or tables for lists. Use INDIRECT function for dependent lists. Set data validation to List with formula. Use conditional formatting for visual feedback.",
                "difficulty": 4
            },
            {
                "id": 5,
                "question_text": "How would you use Power Query to clean messy data?",
                "model_answer": "Data > Get Data to import. Remove duplicates, handle nulls, fix data types. Use transformations like split columns, merge queries, append data. Create reproducible refresh process.",
                "difficulty": 5
            },
            {
                "id": 6,
                "question_text": "Design an automated reporting system with Excel and VBA.",
                "model_answer": "Use Power Query for data refresh, dynamic ranges, PivotTables. VBA for automation: Workbook_Open events, scheduled refresh, email automation with Outlook integration. Include error handling.",
                "difficulty": 6
            }
        ]
    
    def generate_fresh_questions(self) -> Optional[List[Dict]]:
        """
        Generate completely fresh questions using AI
        
        Returns:
            List of newly generated questions or None if failed
        """
        if self.gemini_service:
            return self.gemini_service.generate_questions(Config.TOTAL_QUESTIONS)
        return None
    
    def get_random_questions_from_bank(self) -> Optional[List[Dict]]:
        """
        Get randomized questions from the question bank
        
        Returns:
            List of shuffled questions from bank or None if failed
        """
        questions = self.load_from_bank()
        if questions and len(questions) >= Config.TOTAL_QUESTIONS:
            import random
            # Shuffle and return requested number of questions
            random.shuffle(questions)
            return questions[:Config.TOTAL_QUESTIONS]
        return questions
