from loaders import load_mhtml, extract_posts
from style_analyzer import analyze_style
from generator import generate_post

if __name__ == "__main__":
    # Load saved LinkedIn page
    filepath = "./data/mhilalMHTML.mhtml"
    docs = load_mhtml(filepath)
    posts = extract_posts(docs)

    print(f"Extracted {len(posts)} posts")
    sorted_posts = sorted(posts, key=lambda x: x[1], reverse=True)
    top_5 = sorted_posts[:5]

    # Analyze writing style
    style = analyze_style([p[0] for p in top_5])
    print("\n=== User Writing Style ===\n")
    print(style)

    # Generate a new post
    topic = input("\nEnter a topic for your next post: ")
    new_post = generate_post(topic, style)

    print("\n=== Generated Post ===\n")
    print(new_post)
