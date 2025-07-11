import re
from bs4 import BeautifulSoup
from langchain_community.document_loaders.mhtml import MHTMLLoader

IMPRESSION = 0.5
LIKE = 3
COMMENT = 6

def load_mhtml(filepath: str):
    loader = MHTMLLoader(filepath)
    return loader.load()


def extract_posts(docs):
    posts = []

    for doc in docs:
        text = doc.page_content
        chunks = text.split("Feed post number")
        print(f"Found {len(chunks) - 1} post chunks")

        for chunk in chunks[1:]:
            cleaned = chunk.strip()

            # ✅ Truncate at 'People you may'
            lower = cleaned.lower()
            cutoff_marker = "people you may"
            if cutoff_marker in lower:
                idx = lower.find(cutoff_marker)
                cleaned = cleaned[:idx].strip()
                print("✂️ Truncated at 'People you may...'")

            soup = BeautifulSoup(cleaned, "html.parser")
            extracted = soup.get_text(separator=" ").strip()
            extracted = re.sub(r"\s+", " ", extracted)

            if re.search(r"\breposted\b|\bshared\b", extracted, re.I):
                print("Skipping repost/share...")
                continue

            word_count = len(extracted.split())
            if word_count < 10:
                print(f"Skipping tiny chunk ({word_count} words)")
                continue

            impressions,likes,comments = get_impresssions(extracted)

            score = impressions * IMPRESSION + likes * LIKE + comments * COMMENT
            print(f"Impressions: {impressions}, Likes: {likes}, Comments: {comments}, Score: {score}")
            posts.append((extracted, score))

    return posts


def get_impresssions(extracted: str) -> int:
    impressions = 0
    match = re.search(r"([\d,]+)\s+impressions", extracted, re.I)
    if match:
        impressions = int(match.group(1).replace(",", ""))
        print(f"Found impressions: {impressions}")
    likes = 0
    comments = 0

    marker = "activate to view larger image"
    idx = extracted.lower().find(marker)
    if idx != -1:
        after_marker = extracted[idx + len(marker):]
        num_matches = re.findall(r"(\d+)", after_marker)
        if num_matches:
            likes = int(num_matches[0])
        comment_match = re.search(r"(\d+)\s+comments?", after_marker, re.I)
        if comment_match:
            comments = int(comment_match.group(1))

    else:
        # Try `num num comments` first:
        fallback_pair = re.search(r"(\d+)\s+(\d+)\s+comments?", extracted, re.I)
        if fallback_pair:
            likes = int(fallback_pair.group(1))
            comments = int(fallback_pair.group(2))
        else:
            # Fallback: separate "Like" and "comments"
            like_match = re.search(r"(\d+)\s+Like", extracted, re.I)
            likes = int(like_match.group(1)) if like_match else 0

            comment_match = re.search(r"(\d+)\s+comments?", extracted, re.I)
            comments = int(comment_match.group(1)) if comment_match else 0

        impressions = impressions+likes + comments
        print(f"Fallback likes: {likes}, comments: {comments}")

    return impressions, likes, comments
