def rewrite_post(post, instruction):
    msg = [("system", "You are a LinkedIn ghostwriter."),
           ("human", f"Rewrite the post to be more {instruction}:\n\n{post}")]
    
    response = llm.invoke(msg).content
    print(f"Rewritten post: {response.content[:100]}...")  # Debug
    return llm.invoke(msg).content
