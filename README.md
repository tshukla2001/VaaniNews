# VaaniNews - News Summarization and Text-to-Speech Application

## Overview
**VaaniNews** is a web-based application. It performs sentiment analysis, comparative analysis, and produces a text-to-speech (TTS) output in Hindi after extracting important details from several news articles about a certain company.  Users can enter a company name into the tool to get an audio output and a structured sentiment report.

## Installation & Setup
### Prerequisites
- Python 3.8+
- Google Cloud credentials for Text-to-Speech and Translation API

### Installation Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/tshukla2001/VaaniNews.git
   cd VaaniNews
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up API keys**:
   - Create a `.env` file in the project directory and add your API keys.
   - Example format:
     ```env
     NEWS_API_KEY=your_news_api_key
     GROQ_API_KEY=your_groq_api_key
     GOOGLE_APPLICATION_CREDENTIALS=./path-to-your-google-credentials.json
     ```

## Model Details
### **Summarization Model**
- Using **Google Generative AI (Gemini-2.0-Flash)** for generating concise article summaries.
- Extracting the most relevant content while filtering out ads and redundant information.

### **Sentiment Analysis Model**
- Using **LangChain-Groq with LLaMA-3.3-70b-Versatile** to analyze sentiment (Positive, Neutral, Negative) from summarized articles.
- Processing the cleaned text using **NLTK** before sentiment evaluation.

### **Text-to-Speech (TTS) Model**
- Using **Google Cloud Text-to-Speech** to convert the final sentiment summary into Hindi speech.
- Generating an MP3 file for playback.

## API Development
The backend is built using **FastAPI** and provides endpoints for news fetching, summarization, translation, and TTS generation.

### **API Endpoints & Usage**
#### **1. Fetch News & Sentiment Analysis**
```http
GET /fetch_news?company=Microsoft
```
- Fetches 10 news articles, summarizes them, and performs sentiment analysis.

#### **2. Translate Text to Hindi**
```http
GET /translate?text=News&target_language=hi
```
- Translates any given text to Hindi using **Google Cloud Translation API**.

#### **3. Generate TTS**
```http
GET /generate_tts?text=Company News
```
- Converts the given text into Hindi speech and returns an audio file.

### **Using the APIs in Postman**
1. Run the backend using:
   ```bash
   uvicorn api:app --reload
   ```
2. Open **Postman** and enter the endpoint URL (e.g., `http://127.0.0.1:8000/fetch_news?company=Microsoft`).
3. Click **Send** to receive the JSON response.

## Assumptions & Limitations
- **News Extraction**: Articles are scraped only from non-JavaScript websites using BeautifulSoup.
- **Sentiment Analysis Accuracy**: Sentiment detection is AI-driven and may not always be 100% accurate.
- **Google Cloud APIs**: Require valid API credentials for Translation and TTS features.
- **Deployment**: The project is designed for deployment on **Hugging Face Spaces** but can be extended to other platforms.

## Running the Application
### Start the FastAPI Backend
```bash
uvicorn api:app --reload
```
### Run the Streamlit Frontend
```bash
streamlit run app.py
```
