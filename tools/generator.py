
def generate_post(topic: str, style: str) -> str:
    messages = [
        (
            "system",
            "You are a LinkedIn ghostwriter."
        ),
        (
            "human",
            f"""
            Write a new post about: "{topic}"

            Use this style guide:
            {style}

            - Be natural and authentic
            - Keep it 100–200 words
            - Return only the post text, no explanations.
            """
        )
    ]

    response = llm.invoke(messages)
    print(f"Generated post for topic '{topic}': {response.content[:100]}...")  # Debugging output
    return response.content
