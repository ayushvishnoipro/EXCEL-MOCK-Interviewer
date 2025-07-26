# Excel Mock Interviewer

A dynamic, AI-powered Streamlit application that conducts comprehensive Excel skills interviews using Google's Gemini API. This modular application tests both conceptual Excel knowledge and practical data-driven skills with real Excel data.

## Features

- **Dynamic Question Generation**: AI-generated questions at startup, or loads from question bank
- **Multiple Question Types**: Choose from conceptual, data-driven, or mixed question modes
- **Excel Data Analysis**: Questions based on real Excel files with data previews
- **Progressive Difficulty**: 6 questions ranging from basic to advanced Excel concepts
- **Real-time Evaluation**: Immediate AI feedback with scores (0-5) and detailed tips
- **Comprehensive Transcript**: Complete interview history saved to timestamped CSV
- **Performance Analytics**: Overall summary with strengths, weaknesses, and recommendations
- **Professional UI**: Clean, intuitive interface with progress tracking

## Quick Start

### 1. Local Development

```bash
# Clone or download the project
cd Excel\ Interviewer

# Install dependencies
pip install -r requirements.txt

# Set up your Gemini API key
# Create .env file with:
# GEMINI_API_KEY=your_actual_api_key_here

# For Streamlit Cloud:
# Edit .streamlit/secrets.toml and add your API key

# Run the modular app
streamlit run app_new.py

# Or run the original monolithic version
# streamlit run app.py
```

### 2. Streamlit Cloud Deployment

1. **Push to GitHub**: Upload all files to a GitHub repository

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `app_new.py`

3. **Configure Secrets**:
   - In your Streamlit Cloud app settings
   - Go to "Secrets" section
   - Add: `GEMINI_API_KEY = "your_actual_api_key_here"`

4. **Get Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key (free tier available)
   - Add to Streamlit secrets

## File Structure

```
Excel Interviewer/
├── app_new.py                 # Main entry point (modular version)
├── app.py                     # Original monolithic version (backup)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (local)
├── .streamlit/
│   └── secrets.toml          # Streamlit secrets (cloud)
├── data/
│   ├── question_bank.json    # Fallback questions database
│   ├── Employee_Performance_Data.xlsx  # Sample Excel data
│   └── Sales_Data.xlsx       # Sample Excel data
├── src/                      # Main source code
│   ├── main.py              # Application controller
│   ├── config/              # Configuration management
│   ├── services/            # Business logic services
│   ├── ui/                  # User interface components
│   └── utils/               # Utility functions
├── ARCHITECTURE.md          # Detailed architecture documentation
└── README.md                # This file
```

## How It Works

### Question Generation
- **Conceptual Questions**: AI generates Excel concept questions with varying difficulty
- **Data-Driven Questions**: Analyzes Excel files in the data folder and creates questions based on real data
- **Mixed Questions**: Combines both question types for a comprehensive assessment

### Question Types
- **Conceptual**: Tests theoretical Excel knowledge and best practices
- **Data-Driven**: Displays Excel data snippets and asks for formulas or analysis
- **Progressive Difficulty**: Questions increase in complexity as the interview progresses

### Interview Flow
1. **Intro Phase**: Welcome screen with question type selection
2. **Question Phase**: Present each question with data context (if applicable) 
3. **Evaluation Phase**: AI evaluates answer and provides detailed feedback
4. **Summary Phase**: Overall performance analysis and recommendations

### State Management
- Uses `SessionManager` for centralized state control
- Tracks: questions, question types, data sources, current index, answers, scores, transcript
- Enables proper question flow and prevents data loss

### AI Integration
- **Question Generation**: Creates diverse, progressive difficulty questions
- **Data Analysis**: Extracts insights from Excel files for realistic questions
- **Answer Evaluation**: Scores answers 0-5 with detailed feedback
- **Performance Summary**: Analyzes overall performance with actionable insights

## Interview Topics Covered

1. **Basic Functions** (Level 1-2)
   - VLOOKUP vs INDEX/MATCH
   - Basic pivot tables
   - Simple formulas and functions

2. **Intermediate Skills** (Level 3-4)
   - Error handling and prevention
   - Data validation systems
   - Conditional formatting
   - Data analysis and interpretation

3. **Advanced Features** (Level 5-6)
   - Power Query data transformation
   - VBA automation and reporting
   - Complex Excel solutions
   - Excel-based business intelligence

4. **Data-Driven Tasks**
   - Writing formulas for real data
   - Data analysis from Excel files
   - Practical business scenarios
   - Excel-based reporting solutions

## Customization

### Adding Custom Questions
Edit `data/question_bank.json` with your own questions:

```json
{
  "id": 1,
  "question_text": "Your question here",
  "model_answer": "Expected answer",
  "difficulty": 1,
  "question_type": "conceptual"
}
```

### Adding Custom Excel Files
1. Place your Excel files in the `data/` directory
2. Files will be automatically detected and used for data-driven questions
3. Recommended format: clean, structured data with clear column headers

### Modifying AI Prompts
Update the prompt templates in `src/config/prompts.py`:
- `QUESTION_GENERATION_PROMPT`
- `DATA_QUESTION_PROMPT`
- `EVALUATION_PROMPT_TEMPLATE`
- `SUMMARY_PROMPT_TEMPLATE`

## Technical Details

### Dependencies
- **Streamlit**: Web app framework
- **google-generativeai**: Gemini API client
- **pandas**: Data manipulation for CSV export
- **openpyxl**: Excel file reading and analysis
- **xlrd**: Additional Excel file support

### Modular Architecture
- **Configuration Layer**: Settings and prompts
- **Service Layer**: AI integration, question management, Excel analysis
- **UI Layer**: Streamlit components
- **Utils Layer**: Session management, file operations
- **Controller**: Main application flow

### Error Handling
- Retry logic for API calls (max 2 retries)
- Graceful handling of quota limits
- Smart fallback for evaluation when AI fails
- User-friendly error messages
- JSON parsing error recovery

### Data Export
- Timestamped CSV files with complete transcript
- Downloadable through Streamlit interface
- Includes questions, answers, scores, and feedback
- Records question types and data sources

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `GEMINI_API_KEY` is set in `.env` for local or secrets for cloud
   - Verify key is valid and has quota remaining

2. **Question Generation Fails**
   - App falls back to `data/question_bank.json`
   - Check API connectivity and quota

3. **Excel File Analysis Issues**
   - Ensure Excel files are in the `data/` directory
   - Check file format compatibility (xlsx, csv)
   - Verify files have proper column headers

4. **CSV Download Issues**
   - Files save to app directory
   - Use download button for cloud deployments

### Support

For issues or feature requests, check:
- Streamlit documentation: [docs.streamlit.io](https://docs.streamlit.io)
- Gemini API documentation: [ai.google.dev](https://ai.google.dev)

## License

This project is open source and available under the MIT License.
