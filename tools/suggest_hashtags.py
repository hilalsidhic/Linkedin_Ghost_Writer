def suggest_hashtags(topic, style):
    prompt = f"""Suggest 3–5 relevant and trending LinkedIn hashtags for this topic:
            "{topic}"
            Keep them in line with this style:
            {style}"""
    msg = [("system", "You are a social media strategist."),
           ("human", prompt)]

    response = llm.invoke(msg).content
    print(f"Suggested hashtags for topic '{topic}': {response.content[:100]}...")  # Debugging output
    return llm.invoke(msg).content