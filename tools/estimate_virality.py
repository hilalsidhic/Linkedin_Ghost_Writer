def estimate_virality(post):
    msg = [("system", "You are a LinkedIn growth expert."),
           ("human", f"Rate this post's potential virality 0–100 and give 1 improvement tip:\n\n{post}")]
    
    response = llm.invoke(msg).content
    print(f"Estimated virality for post: {response.content[:100]}...")
    return response