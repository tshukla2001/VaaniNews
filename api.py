from fastapi import FastAPI
from fastapi.responses import JSONResponse
from utils import fetch_news_articles, comparative_analysis, final_summary_of_all, generating_text_to_speech
from google.cloud import translate_v2 as translate

# Initialize FastAPI application
app = FastAPI()

# Dictionary to store the final output structure
final_output = {
    "Company": "",
    "Articles":[],
    "Comparative Sentiment Score": {},
    "Final Sentiment Analysis": ""
}

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/fetch_news")
def fetch_news(company: str):
    """
    Fetches news articles related to the given company, performs sentiment analysis, and returns the results.
    
    Parameters:
        company (str): Name of the company to fetch news articles for.
    
    Returns:
        dict: A dictionary containing the company name, fetched articles, sentiment scores, and final sentiment analysis.
    """

    final_output["Company"] = company

    # Fetch articles related to the company
    articles_content = fetch_news_articles(company)
    final_output["Articles"] = articles_content

    # Perform comparative sentiment analysis on the fetched articles
    comp_analysis = comparative_analysis(articles_content)
    final_output["Comparative Sentiment Score"] = comp_analysis

    # Generate a final summary sentiment analysis
    final_summary = final_summary_of_all(articles_content)
    final_output["Final Sentiment Analysis"] = final_summary

    return final_output


@app.get("/translate")
def translate_text(text: str, target_language="hi"):
    """
    Translates the given text to the specified target language using Google Cloud Translation API.
    
    Parameters:
        text (str): The text to be translated.
        target_language (str): The target language code.
    """

    client = translate.Client()

    # Perform translation
    result = client.translate(text, target_language=target_language)

    return result["translatedText"]


@app.get("/generate_tts")
def text_to_speech(text: str):
    """
    Generates a Text-to-Speech (TTS) output for the given text.
    
    Parameters:
        text (str): The text to be converted to speech.
    """

    try:
        return generating_text_to_speech(text)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
