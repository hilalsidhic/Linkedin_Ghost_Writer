# Write Like Me - LinkedIn Ghostwriter

## Overview

This is a Streamlit-based web application that serves as a personal LinkedIn ghostwriter. The application analyzes a user's existing LinkedIn posts to understand their writing style and generates new posts in the same voice. It uses Google's Gemini AI model for natural language processing and style analysis.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple multi-module architecture with clear separation of concerns:

- **Frontend**: Streamlit web application with custom CSS styling
- **Backend**: Python modules for data processing and AI integration
- **AI Integration**: Google Gemini API for style analysis and content generation
- **Data Processing**: BeautifulSoup and LangChain for parsing LinkedIn data

## Key Components

### 1. Web Interface (`app.py`)
- **Purpose**: Main Streamlit application providing the user interface
- **Features**: 
  - File upload for MHTML files
  - Step-by-step workflow guidance
  - Custom CSS styling for professional appearance
  - Copy-to-clipboard functionality
- **Design**: Clean, modern interface with LinkedIn-inspired color scheme

### 2. Data Loading (`loaders.py`)
- **Purpose**: Extract and process LinkedIn posts from MHTML files
- **Key Functions**:
  - `load_mhtml()`: Loads MHTML files using LangChain
  - `extract_posts()`: Parses and cleans LinkedIn post content
- **Features**:
  - Filters out reposts and shares
  - Removes very short posts (< 10 words)
  - Engagement scoring system (impressions, likes, comments)

### 3. Style Analysis (`style_analyzer.py`)
- **Purpose**: Analyze writing patterns from user's posts
- **AI Model**: Google Gemini 2.5 Pro
- **Analysis Areas**:
  - Tone and voice
  - Sentence structure
  - Common vocabulary and phrases
  - Emoji and hashtag usage
  - Recurring themes

### 4. Content Generation (`generator.py`)
- **Purpose**: Generate new LinkedIn posts matching user's style
- **AI Model**: Google Gemini 2.5 Pro
- **Features**:
  - Topic-based post generation
  - Style-guided content creation
  - 100-200 word limit enforcement
  - Professional tone maintenance

## Data Flow

1. **Input**: User uploads MHTML file of their LinkedIn activity
2. **Processing**: 
   - Parse MHTML content using BeautifulSoup
   - Extract individual posts and clean text
   - Filter and score posts by engagement
3. **Analysis**: 
   - Send top-performing posts to Gemini for style analysis
   - Generate comprehensive style guide
4. **Generation**: 
   - User provides topic/theme
   - Gemini generates new post using analyzed style
5. **Output**: Formatted post ready for LinkedIn with copy functionality

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **LangChain Community**: MHTML document loading
- **BeautifulSoup4**: HTML parsing and text extraction
- **Google GenAI**: AI model integration
- **pyperclip**: Clipboard functionality

### AI Services
- **Google Gemini 2.5 Pro**: Primary AI model for both style analysis and content generation
- **API Key**: Required environment variable `GEMINI_API_KEY`

### Data Processing
- **MHTML Support**: Processes LinkedIn export files
- **HTML Parsing**: Extracts clean text from complex LinkedIn HTML structure
- **Regular Expressions**: Text cleaning and pattern matching

## Deployment Strategy

### Environment Setup
- **Python Environment**: Requires Python 3.8+
- **Environment Variables**: 
  - `GEMINI_API_KEY`: Google AI API key
- **Dependencies**: Install via `pip install -r requirements.txt`

### Local Development
- **Run Command**: `streamlit run app.py`
- **Port**: Default Streamlit port (8501)
- **File Storage**: Temporary files for MHTML processing

### Production Considerations
- **API Key Management**: Secure storage of Gemini API key
- **File Handling**: Temporary file cleanup after processing
- **Error Handling**: Graceful degradation for API failures
- **Rate Limiting**: Consider API usage limits for Gemini

### Security Notes
- **Data Privacy**: Files processed locally, not stored permanently
- **API Security**: Gemini API key should be properly secured
- **User Data**: No persistent storage of user content or LinkedIn data

The application prioritizes user privacy by processing MHTML files locally and not storing any personal LinkedIn data permanently. The modular architecture allows for easy maintenance and future enhancements.