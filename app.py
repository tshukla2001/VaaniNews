import os
import requests
import streamlit as st

# Base URL for the backend API
API_BASE_URL = "http://localhost:8000"

# Streamlit UI title and caption
st.title("📰VaaniNews")
st.caption("Bringing News to Life - Summarized, Analyzed & Spoken in Hindi!")

# Input field for entering the company name
company_name = st.text_input("Enter the company name:")

# Creating a layout with four columns
col1, col2, col3, col4 = st.columns([1, 2, 1, 1]) 

# Buttons for fetching news and fetching summaries
with col1:
    fetch_news = st.button("Fetch News")

with col2:
    fetch_summary = st.button("Fetch Summary")

# If either 'Fetch News' or 'Fetch Summary' button is clicked
if fetch_news or fetch_summary:
    # Make an API request to fetch news data for the given company
    response = requests.get(f"{API_BASE_URL}/fetch_news/?company={company_name}")
    
    # Check if the API request was successful
    if response.status_code == 200:
        news_data = response.json()

        # Extract final summary from the response
        final_summary = news_data.get("Final Sentiment Analysis", "")

        # Translate the summary to Hindi (or required language)
        translate_response = requests.get(f"{API_BASE_URL}/translate/?text={final_summary}")

        # Display news details if 'Fetch News' button was clicked
        if fetch_news:
            st.write(f"Below are the details about the latest news about {company_name}:")
            st.json(news_data)
        
        # Display summary if 'Fetch Summary' button was clicked
        elif fetch_summary:
            st.write(f"Below is the summary of the latest news about {company_name}:")
            st.write(final_summary)
        
        # Generate and play Hindi speech if a summary is available
        if final_summary:
            st.write("Generating Hindi Speech for the final summary...")

            tts_response = requests.get(f"{API_BASE_URL}/generate_tts/?text={translate_response.json()}")

            if tts_response.status_code == 200:
                audio_file = "output.mp3"  # Expected output audio file

                # Check if the audio file exists before playing
                if os.path.exists(audio_file):
                    st.audio(audio_file, format="audio/mp3") 
                else:
                    st.error("Audio file was not generated.")
            else:
                st.error("Failed to generate text-to-speech.")
        else:
            st.warning("No summary found to generate speech.")
    else:
        st.error(f"Failed to fetch news about {company_name}")


