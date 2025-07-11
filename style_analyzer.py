import os
from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

def analyze_style(posts: list[str]) -> str:
    """Analyze writing style from a list of LinkedIn posts"""
    if not posts:
        return "No posts available for analysis."
    
    joined_posts = "\n\n---\n\n".join(posts)
    
    system_instruction = "You are an expert LinkedIn writing style analyst."
    
    user_prompt = f"""
    Below are multiple LinkedIn posts by the same user.

    Analyze and describe:
    - Tone (formal, casual, inspirational, etc.)
    - Sentence style (short, long, direct, storytelling)
    - Typical openings and closings
    - Common words, emojis, hashtags
    - Any recurring themes

    Posts:
    {joined_posts}

    Return a clear bullet-point style guide that captures their unique voice.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            ),
        )
        
        return response.text if response.text else "Unable to analyze writing style."
        
    except Exception as e:
        return f"Error analyzing style: {str(e)}"
