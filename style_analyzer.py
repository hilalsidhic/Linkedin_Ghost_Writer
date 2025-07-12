from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key="AIzaSyBGhnGtJJW3elHPEdztuhLozOh4tAP-Agg"
)

def analyze_style(posts: list[str]) -> str:
    joined_posts = "\n\n---\n\n".join(posts)

    messages = [
        (
            "system",
            "You are an expert LinkedIn writing style analyst."
        ),
        (
            "human",
            f"""
            Below are multiple LinkedIn posts by the same user.

            Analyze and describe:
            - Tone (formal, casual, inspirational, etc.)
            - Sentence style (short, long, direct, storytelling)
            - Typical openings and closings
            - Common words, emojis, hashtags
            - Any recurring themes

            Posts:
            {joined_posts}

            Return a clear bullet-point style guide.
            """
        )
        ]

    response = llm.invoke(messages)

    return response.content
