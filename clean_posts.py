from langchain_google_genai import ChatGoogleGenerativeAI
import concurrent.futures

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

def clean_posts_parallel(posts):
    cleaned_posts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        futures = [executor.submit(clean_post_text, text) for text, score in posts]
        # Gather results in same order
        for future in concurrent.futures.as_completed(futures):
            cleaned_posts.append(future.result())
    return cleaned_posts

def clean_post_text(post: str) -> str:
    """
    Remove names, job titles, companies, private details, and LinkedIn UI junk.
    Return only the meaningful post text.
    """
    messages = [
        (
            "system",
            "You clean LinkedIn post text. Remove names, company info, job details, and any LinkedIn interface text like 'Visible to anyone', 'Like Comment', 'View analytics', etc. Respond ONLY with clean post content."
        ),
        (
            "human",
            f"Clean this post. Remove names, job details, company names, UI phrases:\n\n{post}\n\nReturn ONLY the clean post content."
        )
    ]

    response = llm.invoke(messages)
    cleaned = response.content.strip()

    # Extra fallback: regex strip of common UI junk
    cleaned = remove_linkedin_ui_garbage(cleaned)

    return cleaned

import re

def remove_linkedin_ui_garbage(text: str) -> str:
    # Basic patterns for common LinkedIn UI noise
    patterns = [
        r'Visible to anyone.*',
        r'Activate to view larger image.*',
        r'Like Comment Repost Send.*',
        r'[0-9,]+ impressions.*',
        r'View analytics.*',
        r'[\s•]+[0-9]+[a-zA-Z]+.*',  # 7mo, 2yr, etc.
    ]

    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()

    return text

def clean_style_guide(post:str) -> str:
    """
    Clean the style guide text by removing any personal names, job titles, or company names.
    """
    messages = [
        (
            "system",
            "You clean LinkedIn style guides. Remove names, job titles, company info, and any personal identifiers. Respond ONLY with clean style guide content."
        ),
        (
            "human",
            f"Clean this style guide. Remove names, job details, company names:\n\n{post}\n\nReturn ONLY the clean style guide content."
        )
    ]

    response = llm.invoke(messages)
    return response.content.strip()