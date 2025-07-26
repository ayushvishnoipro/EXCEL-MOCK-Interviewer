"""
File and data utilities
"""
import os
import pandas as pd
import datetime
from typing import List, Dict
from ..config.settings import Config


class FileManager:
    """Handles file operations for the interview app"""
    
    @staticmethod
    def save_transcript_to_csv(transcript: List[Dict], summary: Dict) -> str:
        """
        Save interview transcript and summary to CSV file
        
        Args:
            transcript: List of Q&A entries
            summary: Interview summary
            
        Returns:
            Filename of saved CSV
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{Config.TRANSCRIPT_PREFIX}_{timestamp}.csv"
        
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
            'tip': '',
            'strengths': '',
            'areas_for_improvement': ''
        })
        
        # Add Q&A data
        for entry in transcript:
            csv_data.append({
                'timestamp': entry.get('timestamp', ''),
                'section': 'QUESTION_ANSWER',
                'question_id': entry.get('question_id', ''),
                'question': entry.get('question', ''),
                'user_answer': entry.get('user_answer', ''),
                'score': entry.get('score', ''),
                'feedback': entry.get('feedback', ''),
                'tip': entry.get('tip', ''),
                'strengths': entry.get('strengths', ''),
                'areas_for_improvement': entry.get('areas_for_improvement', '')
            })
        
        # Add summary
        csv_data.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'section': 'SUMMARY',
            'question_id': '',
            'question': 'Overall Performance Summary',
            'user_answer': summary.get('summary', ''),
            'score': summary.get('overall_score', ''),
            'feedback': f"Performance Level: {summary.get('performance_level', '')}",
            'tip': f"Recommendations: {', '.join(summary.get('recommendations', []))}",
            'strengths': f"Strengths: {', '.join(summary.get('strengths', []))}",
            'areas_for_improvement': f"Areas for Improvement: {', '.join(summary.get('improvement_areas', []))}"
        })
        
        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False)
        
        return filename
    
    @staticmethod
    def ensure_data_directory():
        """Ensure data directory exists"""
        data_dir = os.path.dirname(Config.QUESTION_BANK_PATH)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)


class ScoreCalculator:
    """Utility functions for score calculations"""
    
    @staticmethod
    def calculate_average_score(transcript: List[Dict]) -> float:
        """Calculate average score from transcript"""
        if not transcript:
            return 0.0
        
        scores = [entry.get('score', 0) for entry in transcript]
        return round(sum(scores) / len(scores), 1)
    
    @staticmethod
    def get_performance_metrics(transcript: List[Dict]) -> Dict:
        """Get comprehensive performance metrics"""
        if not transcript:
            return {
                'total_questions': 0,
                'average_score': 0.0,
                'performance_level': 'Beginner',
                'questions_attempted': 0,
                'questions_skipped': 0
            }
        
        scores = [entry.get('score', 0) for entry in transcript]
        skipped = len([entry for entry in transcript if entry.get('user_answer') == '[SKIPPED]'])
        
        average_score = round(sum(scores) / len(scores), 1)
        performance_level = Config.get_performance_level(average_score)
        
        return {
            'total_questions': len(transcript),
            'average_score': average_score,
            'performance_level': performance_level,
            'questions_attempted': len(transcript) - skipped,
            'questions_skipped': skipped,
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0
        }
