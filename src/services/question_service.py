"""
Question Management Service for Excel Mock Interviewer
"""
import json
import os
import random
from typing import List, Dict, Optional
from ..config.settings import Config
from .excel_analysis_service import ExcelAnalysisService


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
        self.excel_service = ExcelAnalysisService(gemini_service) if gemini_service else None
    
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
    
    def get_mixed_questions(self, total_questions: int = 6) -> Optional[List[Dict]]:
        """
        Get a mix of conceptual and data-driven questions
        
        Args:
            total_questions: Total number of questions to generate
            
        Returns:
            Mixed list of questions or None if failed
        """
        if not self.excel_service:
            return self.get_questions(force_generate=True)
        
        # Check for available Excel files
        excel_files = self.excel_service.get_available_excel_files()
        
        if not excel_files:
            # No Excel files available, use only conceptual questions
            return self.get_questions(force_generate=True)
        
        # Split questions: 60% conceptual, 40% data-driven
        conceptual_count = max(1, int(total_questions * 0.6))
        data_driven_count = total_questions - conceptual_count
        
        mixed_questions = []
        
        # Get conceptual questions
        conceptual_questions = self.generate_fresh_questions()
        if conceptual_questions and len(conceptual_questions) >= conceptual_count:
            # Add question type marker
            for q in conceptual_questions[:conceptual_count]:
                q['question_type'] = 'conceptual'
            mixed_questions.extend(conceptual_questions[:conceptual_count])
        
        # Get data-driven questions
        data_questions = self.generate_data_driven_questions(data_driven_count, excel_files)
        if data_questions:
            mixed_questions.extend(data_questions)
        
        # If we don't have enough questions, fill with conceptual ones
        if len(mixed_questions) < total_questions:
            remaining = total_questions - len(mixed_questions)
            if conceptual_questions and len(conceptual_questions) > conceptual_count:
                for q in conceptual_questions[conceptual_count:conceptual_count + remaining]:
                    q['question_type'] = 'conceptual'
                mixed_questions.extend(conceptual_questions[conceptual_count:conceptual_count + remaining])
        
        # Assign sequential IDs and sort by difficulty
        for i, question in enumerate(mixed_questions):
            question['id'] = i + 1
        
        # Sort by difficulty while maintaining some variety
        mixed_questions.sort(key=lambda x: x.get('difficulty', x.get('id', 0)))
        
        return mixed_questions[:total_questions]
    
    def generate_data_driven_questions(self, count: int, excel_files: List[str]) -> List[Dict]:
        """
        Generate questions based on actual Excel files
        
        Args:
            count: Number of data-driven questions to generate
            excel_files: List of available Excel files
            
        Returns:
            List of data-driven questions
        """
        if not self.excel_service or not excel_files:
            return []
        
        data_questions = []
        files_to_use = excel_files[:min(len(excel_files), count)]
        
        for i, filename in enumerate(files_to_use):
            # Get file information
            file_info = self.excel_service.get_excel_file_info(filename)
            if not file_info:
                continue
            
            # Generate questions for this file
            questions = self.excel_service.generate_data_driven_questions(
                file_info, 
                num_questions=1
            )
            
            if questions:
                for q in questions:
                    q['question_type'] = 'data_driven'
                    q['source_file'] = filename
                    # Standardize file_info format for UI display
                    standardized_file_info = {
                        'filename': file_info['filename'],
                        'sheet_names': file_info.get('sheets', []),
                        'rows': file_info['rows'],
                        'columns': file_info.get('column_names', []),  # Use column_names as columns for UI
                        'column_count': file_info['columns'],  # Keep original count as column_count
                        'data_sample': file_info.get('sample_data', []),
                        'data_types': file_info.get('data_types', {}),
                        'insights': self._generate_data_insights(file_info)
                    }
                    q['file_info'] = standardized_file_info
                    q['difficulty'] = min(6, 3 + i)  # Increase difficulty for later questions
                data_questions.extend(questions)
        
        return data_questions
    
    def _generate_data_insights(self, file_info: Dict) -> list:
        """
        Generate simple insights about the Excel data for UI display.
        """
        insights = []
        try:
            if 'rows' in file_info:
                insights.append(f"Dataset contains {file_info['rows']} rows.")
            if 'column_names' in file_info and isinstance(file_info['column_names'], list):
                insights.append(f"Available columns: {len(file_info['column_names'])}")
                columns_lower = [col.lower() for col in file_info['column_names']]
                if any('date' in col for col in columns_lower):
                    insights.append("Contains date/time data.")
                if any(col in columns_lower for col in ['sales', 'revenue', 'amount', 'price']):
                    insights.append("Contains financial/sales data.")
                if any(col in columns_lower for col in ['name', 'employee', 'customer']):
                    insights.append("Contains person/entity information.")
                if any(col in columns_lower for col in ['region', 'location', 'city', 'country']):
                    insights.append("Contains geographic data.")
            if 'sample_data' in file_info and file_info['sample_data']:
                insights.append("Sample data is available for analysis.")
        except Exception:
            insights.append("Data structure available for analysis.")
        return insights
