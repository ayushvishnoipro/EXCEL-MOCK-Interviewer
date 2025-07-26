# Excel Mock Interviewer - Modular Architecture

## 📁 Project Structure

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
│   ├── Employee_Performance_Data.xlsx  # Sample Excel data for data-driven questions
│   └── Sales_Data.xlsx       # Sample Excel data for data-driven questions
├── ARCHITECTURE.md           # This file - architecture documentation
├── src/                      # Main source code
│   ├── __init__.py
│   ├── main.py              # Application controller
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py      # App settings and constants
│   │   └── prompts.py       # AI prompt templates
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── gemini_service.py       # Gemini AI integration
│   │   ├── question_service.py     # Question management
│   │   └── excel_analysis_service.py  # Excel file analysis
│   ├── ui/                  # User interface components
│   │   ├── __init__.py
│   │   └── components.py    # Streamlit UI components
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── session_manager.py   # Session state management
│       └── file_manager.py      # File operations & scoring
└── README.md                # Documentation
```

## 🏗️ Architecture Overview

### **Separation of Concerns**

1. **Configuration Layer** (`src/config/`)
   - `settings.py`: Application constants, API keys, performance levels
   - `prompts.py`: AI prompt templates for questions, evaluation, summary

2. **Service Layer** (`src/services/`)
   - `gemini_service.py`: Handles all Gemini API interactions
   - `question_service.py`: Manages question loading, generation, validation
   - `excel_analysis_service.py`: Analyzes Excel files and generates data-driven questions

3. **UI Layer** (`src/ui/`)
   - `components.py`: Reusable Streamlit UI components
   - Separates presentation logic from business logic
   - Handles both conceptual and data-driven question display

4. **Utility Layer** (`src/utils/`)
   - `session_manager.py`: Centralized session state management
   - `file_manager.py`: File operations, scoring calculations

5. **Controller Layer** (`src/main.py`)
   - `ExcelInterviewApp`: Main application orchestrator
   - Coordinates all layers and handles application flow
   - Supports different question types and interview modes

## 🔧 Key Improvements

### **Modularity Benefits**
- ✅ **Maintainable**: Each module has a single responsibility
- ✅ **Testable**: Individual components can be unit tested
- ✅ **Scalable**: Easy to add new features or modify existing ones
- ✅ **Reusable**: Components can be reused across different parts
- ✅ **Readable**: Clear separation makes code easier to understand

### **Data-Driven Questions**
- **Excel File Analysis**: Automatically analyzes Excel files in the data directory
- **Dynamic Question Generation**: Creates questions based on actual Excel data
- **Data Visualization**: Displays relevant data snippets for context
- **Flexible Question Types**: Supports conceptual, data-driven, or mixed questions
- **Real-world Focus**: Tests practical Excel skills with authentic data challenges

### **Data-Driven Questions**
- **Excel File Analysis**: Dynamic analysis of Excel files in the data directory
- **Smart Question Generation**: AI creates questions based on actual Excel data structure
- **Data Visualization**: Shows relevant Excel data snippets with column info and insights
- **Mixed Question Types**: Allows conceptual, data-driven, or mixed interview modes
- **Practical Testing**: Evaluates real-world Excel skills with authentic data challenges

### **Error Handling**
- Centralized error handling in services
- Graceful fallbacks for AI service failures
- Smart evaluation fallbacks with contextual responses
- Type checking and validation for Excel data structures
- User-friendly error messages through UI components

### **Configuration Management**
- Single source of truth for all settings
- Easy to modify behavior without touching core logic
- Environment-specific configurations

### **State Management**
- Centralized session state operations
- Type-safe state access methods
- Clear state lifecycle management

## 🚀 Running the Modular Version

### **Local Development**
```bash
# Use the new modular entry point
streamlit run app_new.py
```

### **Cloud Deployment**
Update your Streamlit Cloud configuration to use `app_new.py` as the main file.

## 🔄 Migration from Monolithic

The original `app.py` is preserved as a backup. The new modular version (`app_new.py`) provides the same functionality with better:

- **Code organization**
- **Error handling**
- **Maintainability**
- **Testing capabilities**

## 🧪 Testing Strategy

Each module can be tested independently:

```python
# Example: Testing the GeminiService
from src.services.gemini_service import GeminiService

def test_gemini_service():
    service = GeminiService()
    questions = service.generate_questions(3)
    assert len(questions) == 3

# Example: Testing the ExcelAnalysisService
from src.services.excel_analysis_service import ExcelAnalysisService
import pandas as pd

def test_excel_analysis():
    service = ExcelAnalysisService()
    files = service.get_available_excel_files()
    assert len(files) > 0
    
    file_info = service.get_excel_file_info(files[0])
    assert 'filename' in file_info
    assert 'column_names' in file_info
```

## 📈 Future Enhancements

The modular architecture makes it easy to add:

- **Advanced Data Analysis** (enhance ExcelAnalysisService)
- **Interactive Excel Problems** (extend UI components for data input)
- **Excel Formula Validation** (add formula validation service)
- **New question types** (add to QuestionService)
- **Different AI providers** (create new service class)
- **Custom UI themes** (extend UI components)
- **Analytics dashboard** (add new UI module)
- **User authentication** (add auth service)
- **Question difficulty adaptation** (enhance question service)

## 🤝 Contributing

1. **Add new features** by creating new modules
2. **Extend existing functionality** by modifying specific services
3. **Improve UI** by enhancing components
4. **Add tests** for each module to ensure reliability

The modular structure makes it easy for multiple developers to work on different parts simultaneously without conflicts.
