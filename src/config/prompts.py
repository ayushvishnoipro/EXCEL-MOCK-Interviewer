"""
Prompt templates for the Excel Mock Interviewer
"""

class PromptTemplates:
    """Collection of all prompt templates"""
    
    INTERVIEWER_PERSONA = """
    You are an expert Excel interviewer conducting a professional skills assessment. 
    You are thorough, encouraging, and provide constructive feedback. 
    Your responses must always be in valid JSON format as specified.
    """
    
    QUESTION_GENERATION_PROMPT = """
    Generate exactly 6 Excel interview questions as a JSON array. 
    
    CRITICAL JSON RULES:
    - Use single quotes (') instead of double quotes (") in question and answer text
    - NO nested double quotes anywhere in the content
    - Keep each text field concise but informative
    - Use only basic ASCII characters
    
    Create unique, practical Excel scenarios covering:
    - Basic formulas (difficulty 1-2)
    - Pivot tables and analysis (difficulty 3-4) 
    - Advanced features and automation (difficulty 5-6)

    Exact format (copy exactly, replace content):
    [
      {
        "id": 1,
        "question_text": "Create a formula to calculate tiered commission rates where sales under 10000 get 3%, sales 10000-25000 get 5%, and sales over 25000 get 7%.",
        "model_answer": "Use nested IF: =IF(A1<=10000,A1*0.03,IF(A1<=25000,A1*0.05,A1*0.07)). This checks conditions in order and applies appropriate rate.",
        "difficulty": 1
      },
      {
        "id": 2,
        "question_text": "How would you create a dynamic dropdown list where the second dropdown options depend on the first dropdown selection?",
        "model_answer": "Create named ranges for each category. Use INDIRECT function in second dropdown validation. Set first dropdown to list of categories, second dropdown formula to =INDIRECT(A1) where A1 contains first dropdown value.",
        "difficulty": 2
      },
      {
        "id": 3,
        "question_text": "Design a pivot table to show monthly sales trends with year-over-year comparison and percentage growth calculation.",
        "model_answer": "Add Date to Rows (group by month), Sales to Values. Add Year as second field in Rows. Create calculated field for growth: (Current Year - Previous Year)/Previous Year. Format as percentage and add conditional formatting for visual trends.",
        "difficulty": 3
      },
      {
        "id": 4,
        "question_text": "Explain how to use Power Query to combine and clean data from multiple CSV files with inconsistent column names.",
        "model_answer": "Use Data > Get Data > From File > From Folder. Transform data by promoting headers, renaming columns to match, removing duplicates, and standardizing data types. Use Append Queries to combine all files. Create connection for automatic refresh.",
        "difficulty": 4
      },
      {
        "id": 5,
        "question_text": "Create an automated system that updates charts and sends email reports when new data is added to a worksheet.",
        "model_answer": "Use Excel Tables for dynamic ranges, PivotCharts for auto-updating visuals. VBA Worksheet_Change event to trigger updates. Use Outlook automation in VBA to send emails with charts as images. Include error handling and scheduling options.",
        "difficulty": 5
      },
      {
        "id": 6,
        "question_text": "Design a comprehensive data validation and error-checking system for a financial model with cross-sheet dependencies.",
        "model_answer": "Implement data validation rules with custom formulas, use ISERROR and IFERROR functions throughout. Create summary dashboard with error counts using COUNTIF. Add conditional formatting for error highlighting. Use structured references and named ranges for maintainability.",
        "difficulty": 6
      }
    ]
    
    Replace the example content but keep the exact same structure and avoid all quotes in text.
    """
    
    EVALUATION_PROMPT_TEMPLATE = """
    {persona}

    Evaluate this Excel interview answer. Respond with ONLY a complete JSON object.

    Question: {question}
    User Answer: {answer}
    Model Answer: {model_answer}

    IMPORTANT: Your response must be a COMPLETE JSON object. Do not truncate or cut off your response.

    Respond with exactly this format (keep it concise):
    {{
        "score": 4,
        "feedback": "Brief assessment of answer quality and accuracy",
        "tip": "One specific tip for improvement", 
        "strengths": "What the user did well",
        "areas_for_improvement": "One key area to work on"
    }}

    Rules:
    - score: integer 0-5 (0=wrong, 3=partial, 5=excellent)
    - Keep all text fields short and concise (under 100 characters each)
    - No quotes or special characters in text fields
    - Be encouraging but honest
    - Return ONLY the JSON, nothing else
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
    
    EXCEL_DATA_QUESTION_PROMPT = """
    Generate {num_questions} Excel formula questions based on this real dataset:
    
    File: {filename}
    Columns: {columns}
    Data Sample (first 3 rows):
    {sample_data}
    Total Rows: {total_rows}
    
    Create practical Excel formula questions that require analyzing this specific data.
    Focus on real business scenarios like:
    - Calculating totals with conditions (SUMIF, COUNTIF)
    - Finding data with lookups (VLOOKUP, INDEX/MATCH) 
    - Creating dynamic reports and analysis
    - Data validation and error handling
    
    IMPORTANT: Reference the actual column names and data values shown above.
    
    Return exactly this JSON format:
    [
      {{
        "id": 1,
        "question_text": "Based on the data above from {filename}, write an Excel formula to [specific task using actual column names]",
        "model_answer": "=SPECIFIC_FORMULA_HERE with explanation of each part",
        "difficulty": 3,
        "question_type": "data_driven",
        "data_context": "Brief description of relevant data columns",
        "expected_formula_pattern": "Function pattern like SUMIF, VLOOKUP, etc."
      }}
    ]
    
    Make questions specific to the actual column names and data shown above.
    Use realistic business scenarios that would apply to this type of data.
    """
