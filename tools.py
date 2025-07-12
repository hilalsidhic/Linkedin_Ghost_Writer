from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_core.rate_limiters import InMemoryRateLimiter

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
    messages = [
        ("system", "You are a LinkedIn growth strategist."),
        ("human", f"""
Review this post's virality potential (0–100).
Give the rating only, no explanations.

Post:
{post}
""")
    ]
    return llm.invoke(messages).content

# -------------------------------------------------
def rewrite_post(post: str, instruction: str) -> str:
    messages = [
        ("system", "You are a LinkedIn ghostwriter."),
        ("human", f"""
        Rewrite this post to be more {instruction}.

        Post:
        {post}

        Return only the rewritten text, no explanations.
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