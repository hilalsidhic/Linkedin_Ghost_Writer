import os
import re
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.rate_limiters import InMemoryRateLimiter
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ---------------------------------------------------------
# Import your core logic
from loaders import load_mhtml, extract_posts
from tools import (
    analyze_style, generate_post,
    suggest_hashtags, estimate_virality,
    rewrite_post, suggest_cta
)

# ---------------------------------------------------------
# Rate limiter (slow to respect Gemini quotas)
rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,
    check_every_n_seconds=0.1,
    max_bucket_size=10
)

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    rate_limiter=rate_limiter
)

# ---------------------------------------------------------
# ✅ 1️⃣ Gemini doesn’t support OpenAI-style structured function calling.
# So: Parse strings!

def generate_post_tool(input: str) -> str:
    """
    Expects: topic: ..., style: ...
    """
    match = re.search(r"topic:\s*(.*?),\s*style:\s*(.*)", input, re.I)
    if match:
        topic = match.group(1).strip()
        style = match.group(2).strip()
        return generate_post(topic, style)
    return "❌ Could not parse topic/style."

def suggest_hashtags_tool(input: str) -> str:
    match = re.search(r"topic:\s*(.*?),\s*style:\s*(.*)", input, re.I)
    if match:
        topic = match.group(1).strip()
        style = match.group(2).strip()
        return suggest_hashtags(topic, style)
    return "❌ Could not parse topic/style."


def rewrite_post_tool(input: str) -> str:
    try:
        data = json.loads(input)
        post = data["post"]
        instruction = data["instruction"]
        return rewrite_post(post, instruction)
    except Exception as e:
        return f"❌ JSON parse failed: {str(e)}"

# ---------------------------------------------------------
# ✅ 2️⃣ Register your tools (inputs must be plain strings)

tools = [
    Tool(
        name="generate_post",
        func=generate_post_tool,
        description="Generate a new LinkedIn post. Format input: topic: ..., style: ..."
    ),
    Tool(
        name="suggest_hashtags",
        func=suggest_hashtags_tool,
        description="Suggest LinkedIn hashtags. Format input: topic: ..., style: ..."
    ),
    Tool(
        name="estimate_virality",
        func=estimate_virality,
        description="Estimate virality score (0-100). Format input: the post text."
    ),
    Tool(
        name="rewrite_post",
        func=rewrite_post_tool,
        description="Rewrite the post with an instruction. Format input: post: ..., instruction: ..."
    ),
    Tool(
        name="suggest_cta",
        func=suggest_cta,
        description="Suggest a CTA for a post. Format input: the post text."
    )
]

# ---------------------------------------------------------
# ✅ 3️⃣ Initialize the agent (Gemini = Zero-Shot React)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# ---------------------------------------------------------
# ✅ 4️⃣ Agent run wrapper

def run_agent_generate(topic: str, style: str) -> str:
    """
    Calls the agent with a prompt.
    The agent must output tool calls using the input format you expect.
    """

    prompt = f"""
    You are a LinkedIn Ghostwriter agent.

    Tools you have:
    1️⃣ generate_post → Input: topic: ..., style: ...
    2️⃣ suggest_hashtags → Input: topic: ..., style: ...
    3️⃣ suggest_cta → Input: post text

    Your job:
    - First, generate a post about: "{topic}" using the given style.
    - Next, get hashtags, CTA.
    - Combine them all into a final output.

    User's style:
    {style}

    Use the correct format for tool inputs so they parse correctly.
    """

    return agent.invoke({"input": prompt})

def run_agent_estimate_virality(post_text: str) -> str:
    """
    Calls the agent to estimate virality for the given post.
    """

    prompt = f"""
    You are a LinkedIn Virality Analyst Agent.

    Tool you have:
    1️⃣ estimate_virality → Input: the post text.

    Your job:
    - Use `estimate_virality` to analyze the following post:
    
    "{post_text}"

    - Return the virality score (0–100) and the tip.

    Use the correct tool format.
    """

    return agent.invoke({"input": prompt})


def run_agent_rewrite_post(post_text: str, instruction: str) -> str:
    """
    Calls the agent to rewrite the post with the given instruction.
    """

    prompt = f"""
    You are a LinkedIn Post Rewriter Agent.

    Tool you have:
    1️⃣ rewrite_post → Input: JSON with keys: post, instruction

    Your job:
    - Rewrite this post:
    "{post_text}"

    - Follow this instruction: "{instruction}"

    - Always call `rewrite_post` with this JSON format:
    {{"post": "<post text>", "instruction": "<instruction>"}}

    Return only the rewritten post.
    """

    return agent.invoke({"input": prompt})

