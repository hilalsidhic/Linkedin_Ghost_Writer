import os
from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

def generate_post(topic: str, style: str) -> str:
    """Generate a LinkedIn post based on topic and writing style"""
    system_instruction = "You are a LinkedIn ghostwriter who creates authentic, engaging posts."
    
    user_prompt = f"""
    Write a new LinkedIn post about: "{topic}"

    Use this style guide:
    {style}

    Guidelines:
    - Be natural and authentic
    - Keep it 100–200 words
    - Include relevant emojis if they match the style
    - Make it engaging and professional
    - Return only the post text, no explanations or quotes around it
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
        
        return response.text if response.text else "Unable to generate post."
        
    except Exception as e:
        return f"Error generating post: {str(e)}"
