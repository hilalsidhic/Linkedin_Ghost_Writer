def suggest_cta(post):
    msg = [("system", "You are a LinkedIn content specialist."),
           ("human", f"Suggest a call-to-action line to append to this post:\n\n{post}")]
    response = llm.invoke(msg).content
    print(f"Suggested CTA for post: {response.content[:100]}...")  #
    return llm.invoke(msg).content
