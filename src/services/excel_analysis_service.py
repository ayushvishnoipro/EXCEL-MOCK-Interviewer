"""
Excel File Analysis Service for generating data-driven questions
"""
import pandas as pd
import os
import streamlit as st
from typing import List, Dict, Optional, Tuple
import json
from ..config.settings import Config


class ExcelAnalysisService:
    """Service for analyzing Excel files and generating data-driven questions"""
    
    def __init__(self, gemini_service=None):
        """
        Initialize Excel analysis service
        
        Args:
            gemini_service: Instance of GeminiService for generating questions
        """
        self.gemini_service = gemini_service
        self.excel_files_path = "data"
        self.supported_extensions = ['.xlsx', '.xls', '.csv']
    
    def get_available_excel_files(self) -> List[str]:
        """
        Get list of available Excel files in the data directory
        
        Returns:
            List of Excel file names
        """
        if not os.path.exists(self.excel_files_path):
            return []
        
        excel_files = []
        for file in os.listdir(self.excel_files_path):
            if any(file.lower().endswith(ext) for ext in self.supported_extensions):
                excel_files.append(file)
        
        return excel_files
    
    def load_excel_file(self, filename: str, sheet_name: str = None) -> Optional[pd.DataFrame]:
        """
        Load an Excel file into a pandas DataFrame
        
        Args:
            filename: Name of the Excel file
            sheet_name: Name of the sheet to load (None for first sheet)
            
        Returns:
            DataFrame or None if failed
        """
        file_path = os.path.join(self.excel_files_path, filename)
        
        try:
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            return df
        except Exception as e:
            st.error(f"Failed to load Excel file {filename}: {str(e)}")
            return None
    
    def get_excel_file_info(self, filename: str) -> Optional[Dict]:
        """
        Get basic information about an Excel file
        
        Args:
            filename: Name of the Excel file
            
        Returns:
            Dictionary with file information
        """
        file_path = os.path.join(self.excel_files_path, filename)
        
        try:
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
                info = {
                    'filename': filename,
                    'sheets': ['CSV Data'],
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'data_types': df.dtypes.to_dict(),
                    'sample_data': df.head(5).to_dict('records')
                }
            else:
                # Get sheet names
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                
                # Load first sheet for analysis
                df = pd.read_excel(file_path, sheet_name=sheet_names[0])
                
                info = {
                    'filename': filename,
                    'sheets': sheet_names,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'data_types': df.dtypes.to_dict(),
                    'sample_data': df.head(5).to_dict('records')
                }
            
            return info
        except Exception as e:
            st.error(f"Failed to analyze Excel file {filename}: {str(e)}")
            return None
    
    def generate_data_driven_questions(self, file_info: Dict, num_questions: int = 3) -> Optional[List[Dict]]:
        """
        Generate questions based on Excel file data
        
        Args:
            file_info: Information about the Excel file
            num_questions: Number of questions to generate
            
        Returns:
            List of data-driven questions
        """
        if not self.gemini_service:
            return None
        
        # Prepare data context for AI
        data_context = {
            'filename': file_info['filename'],
            'columns': file_info['column_names'],
            'data_types': {k: str(v) for k, v in file_info['data_types'].items()},
            'sample_rows': file_info['sample_data'][:3],  # First 3 rows as examples
            'total_rows': file_info['rows']
        }
        
        prompt = f"""
        Generate {num_questions} Excel formula/query questions based on this real dataset:
        
        File: {data_context['filename']}
        Columns: {', '.join(data_context['columns'])}
        Sample Data: {json.dumps(data_context['sample_rows'], indent=2)}
        Total Rows: {data_context['total_rows']}
        
        Create practical questions that require writing Excel formulas to analyze this specific data.
        Focus on common business scenarios like:
        - Filtering and summarizing data
        - Conditional calculations
        - Data analysis and reporting
        - Lookups and data retrieval
        
        Return exactly this JSON format:
        [
          {{
            "id": 1,
            "question_text": "Based on the {data_context['filename']} data shown above, write an Excel formula to calculate [specific business requirement]",
            "model_answer": "Specific Excel formula with explanation",
            "difficulty": 3,
            "data_snippet": "Brief description of which data to focus on",
            "expected_formula": "=EXACT_FORMULA_HERE"
          }}
        ]
        
        Make questions specific to the actual data structure and realistic business scenarios.
        """
        
        response = self.gemini_service._call_gemini(prompt)
        if not response:
            return None
        
        try:
            questions = self.gemini_service._parse_json_with_fallback(response)
            return questions
        except Exception as e:
            st.error(f"Failed to generate data-driven questions: {str(e)}")
            return None
    
    def create_data_snippet_display(self, file_info: Dict, max_rows: int = 5) -> Tuple[pd.DataFrame, str]:
        """
        Create a data snippet for display in questions
        
        Args:
            file_info: Information about the Excel file
            max_rows: Maximum number of rows to display
            
        Returns:
            Tuple of (DataFrame snippet, description)
        """
        sample_data = file_info['sample_data'][:max_rows]
        df_snippet = pd.DataFrame(sample_data)
        
        description = f"""
        **Data from {file_info['filename']}:**
        - Total rows: {file_info['rows']}
        - Columns: {', '.join(file_info['column_names'])}
        - Showing first {len(sample_data)} rows:
        """
        
        return df_snippet, description
    
    def validate_excel_formula(self, formula: str, context: Dict) -> Dict:
        """
        Basic validation of Excel formula format
        
        Args:
            formula: Formula string to validate
            context: Context information about the data
            
        Returns:
            Validation result dictionary
        """
        validation = {
            'is_valid': False,
            'issues': [],
            'suggestions': []
        }
        
        formula = formula.strip()
        
        # Basic format checks
        if not formula.startswith('='):
            validation['issues'].append("Formula should start with '='")
            validation['suggestions'].append("Add '=' at the beginning")
        
        # Check for common Excel functions
        excel_functions = ['SUM', 'AVERAGE', 'COUNT', 'COUNTIF', 'SUMIF', 'VLOOKUP', 'INDEX', 'MATCH', 'IF']
        has_function = any(func in formula.upper() for func in excel_functions)
        
        if not has_function:
            validation['suggestions'].append("Consider using Excel functions like SUMIF, COUNTIF, or VLOOKUP")
        
        # Check for proper syntax elements
        if '(' in formula and ')' not in formula:
            validation['issues'].append("Missing closing parenthesis")
        
        if ')' in formula and '(' not in formula:
            validation['issues'].append("Missing opening parenthesis")
        
        # If no major issues, consider it valid
        if len(validation['issues']) == 0:
            validation['is_valid'] = True
        
        return validation
