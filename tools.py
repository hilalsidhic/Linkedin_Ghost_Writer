from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_core.rate_limiters import InMemoryRateLimiter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,
    check_every_n_seconds=0.1,
    max_bucket_size=10
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key="AIzaSyDIw2S8Rf9_WeXZnaGn1KbvRt0-I13-HOk",
    rate_limiter=rate_limiter
)

# -------------------------------------------------
def generate_post(topic: str, style: str) -> str:
    messages = [
        ("system", "You are a professional LinkedIn ghostwriter."),
        ("human", f"""
Write a new LinkedIn post about: "{topic}"

Use this style:
{style}

Guidelines:
- Be authentic, human-like, and clear
- Length: 100–200 words
- No explanations — return only the post text.
""")
    ]
    return llm.invoke(messages).content

# -------------------------------------------------
def estimate_virality(post: str) -> str:
    """Quick virality score without detailed breakdown"""
    messages = [
        ("system", """You are a LinkedIn virality expert. Rate posts 0-100 based on:
        - Emotional impact (25%)
        - Structure/formatting (20%) 
        - Content quality (20%)
        - Engagement potential (15%)
        - Visual appeal (10%)
        - Trend relevance (10%)
        
        Give ONLY the numerical score (0-100), nothing else."""),
        ("human", f"Rate this post's virality potential:\n\n{post}. Just give the score, no explanations.")
    ]
    return llm.invoke(messages).content

# -------------------------------------------------
def rewrite_post(post: str, instruction: str) -> str:
    """
    Rewrite a LinkedIn post while preserving the original author's unique style and voice.
    Focuses on maintaining authenticity while applying specific improvements.
    """
    messages = [
        ("system", """You are an expert LinkedIn ghostwriter who specializes in preserving authentic voice while improving content.

        CRITICAL PRIORITY: PRESERVE ORIGINAL STYLE
        Your main job is to maintain the author's unique:
        - Writing style and tone
        - Vocabulary choices and expressions
        - Sentence structure patterns
        - Personal mannerisms and quirks
        - Emotional expression style
        - Professional voice and personality

        STYLE PRESERVATION TECHNIQUES:
        1. ANALYZE FIRST: Identify the author's unique voice patterns
        2. VOCABULARY MATCHING: Use similar words/phrases they naturally use
        3. SENTENCE RHYTHM: Maintain their typical sentence length and flow
        4. PERSONALITY MARKERS: Keep their humor, formality level, enthusiasm
        5. EXPRESSION STYLE: Preserve how they convey emotions and ideas
        6. STRUCTURAL HABITS: Maintain their paragraph style and organization

        REWRITING APPROACH:
        - Make minimal changes to achieve the instruction
        - Only modify what's necessary for the improvement
        - Keep the author's natural way of expressing ideas
        - Preserve their authentic professional personality
        - Maintain their typical engagement style

        WHAT TO PRESERVE:
        - Personal pronouns usage (I, we, you)
        - Casual vs formal language preference
        - Emoji usage patterns
        - Storytelling approach
        - Industry-specific terminology they use
        - Their natural rhythm and flow"""),
                
                ("human", f"""
        TASK: Rewrite this post to be more {instruction} while keeping the author's original style intact.

        ORIGINAL POST:
        {post}

        ANALYSIS FIRST:
        1. Identify the author's writing style, tone, and voice patterns
        2. Note their vocabulary choices and sentence structure
        3. Recognize their personality markers and mannerisms

        REWRITING REQUIREMENTS:
        - PRESERVE the author's unique voice and style completely
        - MAINTAIN their natural way of expressing ideas
        - KEEP their typical vocabulary and phrasing
        - RETAIN their sentence structure preferences
        - PRESERVE their emotional expression style
        - Only change what's necessary to achieve: {instruction}

        Return ONLY the rewritten post that sounds like the same person wrote it, with no explanations.
        """)
    ]
    return llm.invoke(messages).content

# -------------------------------------------------
def analyze_style(posts: list[str]) -> str:
    joined = "\n\n---\n\n".join(posts)
    messages = [
        ("system", "You are a LinkedIn style expert."),
        ("human", f"""
        Analyze the writing style below.

        Focus on:
        - Tone (casual, formal, witty, inspirational)
        - Sentence length and structure
        - Openings and closings
        - Common words, emojis, hashtags
        - Recurring themes

        Posts:
        {joined}

        Return a clear bullet-point style guide.
        """)
    ]
    return llm.invoke(messages).content

# -------------------------------------------------
def suggest_cta(post: str) -> str:
    messages = [
        ("system", "You are a LinkedIn content specialist."),
        ("human", f"""
        Suggest a good closing CTA line to append to this post.

        Post:
        {post}

        Return only the CTA line.
        """)
    ]
    return llm.invoke(messages).content

# -------------------------------------------------
def suggest_hashtags(topic: str, style: str) -> str:
    messages = [
        ("system", "You are a LinkedIn social media strategist."),
        ("human", f"""
            Suggest 3–5 trending LinkedIn hashtags for this topic:
            "{topic}"

            Make sure they fit this style:
            {style}

            Return only the hashtags, separated by spaces.
            """)
    ]
    return llm.invoke(messages).content