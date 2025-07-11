from langchain_google_genai import ChatGoogleGenerativeAI
import os

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key="AIzaSyBGhnGtJJW3elHPEdztuhLozOh4tAP-Agg"
)

def generate_post(topic: str, style: str) -> str:
    messages = [
        (
            "system",
            "You are a LinkedIn ghostwriter."
        ),
        (
            "human",
            f"""
            Write a new post about: "{topic}"

            Use this style guide:
            {style}

            - Be natural and authentic
            - Keep it 100–200 words
            - Return only the post text, no explanations.
            """
        )
    ]

    response = llm.invoke(messages)
    return response.content
