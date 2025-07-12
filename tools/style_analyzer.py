from langchain_google_genai import ChatGoogleGenerativeAI
import os

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
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
    print(f"Analyzed style for {len(posts)} posts: {response.content[:100]}...")  # Debugging output
    return response.content
