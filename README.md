# Excel Mock Interviewer

A dynamic, AI-powered Streamlit application that conducts comprehensive Excel skills interviews using Google's Gemini API.

## Features

- **Dynamic Question Generation**: AI-generated questions at startup, or loads from question bank
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
# Edit .streamlit/secrets.toml and add your API key

# Run the app
streamlit run app.py
```

### 2. Streamlit Cloud Deployment

1. **Push to GitHub**: Upload all files to a GitHub repository

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `app.py`

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
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── question_bank.json     # Fallback question bank
├── .streamlit/
│   └── secrets.toml      # API key configuration
└── README.md             # This file
```

## How It Works

### Question Generation
- On first run, checks for `question_bank.json`
- If not found, calls Gemini API to generate 6 fresh questions
- Questions cover: formulas, pivot tables, data validation, error handling, Power Query, automation

### Interview Flow
1. **Intro Phase**: Welcome screen with interview overview
2. **Question Phase**: Present each question with text area for answers
3. **Evaluation Phase**: AI evaluates answer and provides detailed feedback
4. **Summary Phase**: Overall performance analysis and recommendations

### State Management
- Uses `st.session_state` for persistent data across reruns
- Tracks: questions, current index, answers, scores, transcript
- Enables proper question flow and prevents data loss

### AI Integration
- **Question Generation**: Creates diverse, progressive difficulty questions
- **Answer Evaluation**: Scores answers 0-5 with detailed feedback
- **Performance Summary**: Analyzes overall performance with actionable insights

## Interview Topics Covered

1. **Basic Functions** (Level 1-2)
   - VLOOKUP vs INDEX/MATCH
   - Basic pivot tables

2. **Intermediate Skills** (Level 3-4)
   - Error handling and prevention
   - Data validation systems
   - Conditional formatting

3. **Advanced Features** (Level 5-6)
   - Power Query data transformation
   - VBA automation and reporting

## Customization

### Adding Custom Questions
Edit `question_bank.json` with your own questions:

```json
{
  "id": 1,
  "question_text": "Your question here",
  "model_answer": "Expected answer",
  "difficulty": 1
}
```

### Modifying AI Prompts
Update the prompt templates in `app.py`:
- `QUESTION_GENERATION_PROMPT`
- `EVALUATION_PROMPT_TEMPLATE`
- `SUMMARY_PROMPT_TEMPLATE`

## Technical Details

### Dependencies
- **Streamlit**: Web app framework
- **google-generativeai**: Gemini API client
- **pandas**: Data manipulation for CSV export

### Error Handling
- Retry logic for API calls (max 2 retries)
- Graceful handling of quota limits
- User-friendly error messages
- JSON parsing error recovery

### Data Export
- Timestamped CSV files with complete transcript
- Downloadable through Streamlit interface
- Includes questions, answers, scores, and feedback

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `GEMINI_API_KEY` is set in secrets
   - Verify key is valid and has quota remaining

2. **Question Generation Fails**
   - App falls back to `question_bank.json`
   - Check API connectivity and quota

3. **CSV Download Issues**
   - Files save to app directory
   - Use download button for cloud deployments

### Support

For issues or feature requests, check:
- Streamlit documentation: [docs.streamlit.io](https://docs.streamlit.io)
- Gemini API documentation: [ai.google.dev](https://ai.google.dev)

## License

This project is open source and available under the MIT License.
