import os
import re
import nltk
import requests
import json
import io
from fastapi.responses import StreamingResponse
from google.cloud import texttospeech
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import google.generativeai as genai

# Retrieve API keys from environment variables
news_api = os.environ.get("NEWS_API_KEY")
groq_api = os.environ.get("GROQ_API_KEY")
gen_ai_key = os.environ.get("GENAI_KEY")
google_credential = os.environ.get("GOOGLE_CREDENTIAL")

# Set Google application credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credential


# Configure the generative AI model with an API key
genai.configure(api_key=gen_ai_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Download necessary NLTK data files
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

# Define News API URL
NEWS_API_URL = "https://eventregistry.org/api/v1/article/getArticles"

# Configure Groq Chat Model for NLP tasks
news_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    max_retries=2,
    api_key=groq_api
)

def preprocess_text(text):
    """Preprocess text by converting to lowercase, removing special characters, tokenizing, removing stopwords, and lemmatizing."""
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words("english")]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(tokens)

def fetch_news_articles(company_name):
    """Fetch the latest news articles for a given company using the News API."""
    news_params = {
    "apiKey": f"{news_api}",
    "keyword": f"{company_name.lower()}",
    "keywordLoc": "title",
    "articlesCount": 10,
    "isDuplicateFilter": "skipDuplicates",
    "lang": "eng"
    }

    output_news_articles = []

    response = requests.get(url=NEWS_API_URL, params=news_params)
    data = response.json()

    articles = data["articles"]["results"]

    for article in articles:
        article_details = {
            "Title": article["title"],
            "Summary": "",
            "Sentiment": "",
            "Topics": []
        }

        # Fetch full article content
        headers = {"User-Agent": "DuckDuckBot/1.1; (+https://duckduckgo.com/duckduckbot)"} 
        response = requests.get(article["url"], headers=headers)

        if response.status_code == 200:
            html_content = response.text
        else:
            print(f"Failed to retrieve content. Status code: {response.status_code}")

        soup = BeautifulSoup(html_content, "html.parser")

        news_content = " ".join([d.get_text() for d in soup.find_all("div")])

         # Generate summary of the article
        article_summary_prompt = f"Summarize the following content \n\n{news_content}\n\n in such a way that the user" \
        "gets an idea about what's in the content. Don't use the marketing and ads part in the content" \
        ", just the necessary information from the content. The summary should be of maximum 5 sentences. Return the answer" \
        "in a string format."

        summary = model.generate_content(article_summary_prompt)

        article_details["Summary"] = summary.text

        # Extract keywords from the article summary
        keyword_prompt = PromptTemplate.from_template(
        """
        ###SUMMARY OF THE ARTICLE:
        {summary}
        ###INSTRUCTIONS:
        Look at the above content. The content is the summary of a news article. 
        Analyze the content in detail and identify the most important keywords in the content. 
        Return a maximum of 7 important keywords. Provide a python list of just the most important keywords. Don't include
        any other content.
        """
        )
        
        keyword_chain = keyword_prompt | news_model

        response = keyword_chain.invoke(input={"summary": summary.text})
            
        article_details["Topics"] = response.content

        # Perform sentiment analysis
        cleaned_article = preprocess_text(summary.text)

        sentiment_prompt = PromptTemplate.from_template(
            """
            ###CLEANED SUMMARY OF THE ARTICLE:
            {summary}
            ###INSTRUCTIONS:
            This is a cleaned summary of a news article. Analyze the sentiment of the article properly. 
            Is it Positive, Neutral, or Negative? Give me a single word answer: Positive, Negative or Neutral.
            Return as string data type.
            """
        )
            
        sentiment_chain = sentiment_prompt | news_model

        response = sentiment_chain.invoke(input={"summary": cleaned_article})

        article_details["Sentiment"] = response.content

        output_news_articles.append(article_details)
    
    return output_news_articles


def comparative_analysis(news_articles):
    """Perform comparative sentiment and topic analysis on a set of news articles."""

    prompt = f"""
For every index in the following array: {news_articles}, there are 4 keys: `Title`, `Summary`,
`Sentiment` and `Topics`. Analyze the `Sentiment` keys in all the articles and find the total
for Positive, Negative and Neutral sentiments. Analyze the summaries of all the articles in the
array given in the `Summary` key, find the similar articles and perform a comparative analysis
and find the content for the following headers: Comparison and the Impact. After analyzing all the
articles in the array, also find the common topics in all the articles and as well as
the unique topics in each article using the `Topics` key for each article in the array. Return a json 
which will have the keys like in the below example.

Here is an example where two random articles are compared:

Follow this exact JSON output format:

{{
    "Sentiment Distribution": {{
        "Positive": 1,
        "Negative": 1,
        "Neutral": 0
    }},
    "Coverage Differences": [
        {{
            "Comparison": "Article 1 highlights Tesla's strong sales, while Article 2 discusses regulatory issues.",
            "Impact": "The first article boosts confidence in Tesla's market growth, while the second raises concerns about future regulatory hurdles."
        }},
        {{
            "Comparison": "Article 1 is focused on financial success and innovation, whereas Article 2 is about legal challenges and risks.",
            "Impact": "Investors may react positively to growth news but stay cautious due to regulatory scrutiny."
        }}
    ],
    "Topic Overlap": {{
        "Common Topics": ["Electric Vehicles"],
        "Unique Topics in Article 1": ["Stock Market", "Innovation"],
        "Unique Topics in Article 2": ["Regulations", "Autonomous Vehicles"]
    }}
}}

Now, analyze the articles in the array and return a JSON response in the same format. Don't add any preamble and just return
the json.
    """

    response = model.generate_content(prompt)

    try:
        result_json = response.text
    except json.JSONDecodeError:
        print("Error: Model did not return valid JSON.")
        return None
    
    return result_json


def final_summary_of_all(articles):
    """Generate a final summary of all the news articles collected."""

    final_summary_prompt = f"""
        This is an array of news article dictionaries containing articles : {articles}. At each index, 
        there is a dictionary that contains the details about
        a news article with the following keys: `Title`, `Summary`, `Sentiment` and `Topics`.
        The `Title` key has the title of the news article. The `Summary` key contains the
        summary of the news article. The `Sentiment` key contains the sentiment of the news
        article. The `Topics` key contains an array of important key topics in the news
        article. Now, based on all these details, analyze all the articles in array of article
        dictionaries and give me a final summary in 4-5 lines. Return a string. Just give me the content
        and nothing else.
        """
    
    response = model.generate_content(final_summary_prompt)

    return response.text


def generating_text_to_speech(text, lang="hi-IN", output_file="output.mp3"):
    """Convert the given text to speech in Hindi and save as an audio file."""

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=lang, 
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    audio_stream = io.BytesIO(response.audio_content)
    audio_stream.seek(0)

    return StreamingResponse(audio_stream, media_type="audio/mpeg")


if __name__ == "__main__":
    """Main script execution to fetch, analyze, and summarize news articles."""

    articles_content = fetch_news_articles("Microsoft")
    for article in articles_content:
        print(article)
    comp_analysis = comparative_analysis(articles_content)
    final_summary = final_summary_of_all(articles_content)
    print(comp_analysis)
    print(final_summary)




