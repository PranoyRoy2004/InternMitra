# groq_client.py - Wrapper around the Groq LLM API
# This is the brain of InternMitra - all AI responses come through here

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client with your API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model to use - llama3 is fast and free on Groq
MODEL = os.getenv("MODEL_NAME", "llama3-8b-8192")


def chat_with_groq(messages: list, temperature: float = 0.7, max_tokens: int = 1024) -> str:
    """
    Send a list of messages to Groq and get a response.
    
    Args:
        messages: List of dicts like [{"role": "user", "content": "Hello"}]
        temperature: 0.0 = focused, 1.0 = creative
        max_tokens: Max length of the response
    
    Returns:
        The AI's response as a plain string
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # Extract the text content from the response
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


def get_system_prompt(role: str = "career_assistant") -> str:
    """
    Returns the right system prompt based on what we need the AI to do.
    System prompts define the AI's personality and behavior.
    """
    prompts = {
        "career_assistant": """You are InternMitra, a friendly and expert AI career assistant 
        specialized in helping students and fresh graduates find internships in India and globally.
        You give practical, actionable advice on:
        - Finding and applying to internships
        - Resume and cover letter writing
        - Interview preparation
        - Skill development roadmaps
        - Career planning
        Always be encouraging, specific, and beginner-friendly. 
        Keep responses concise but helpful. Use bullet points when listing items.""",

        "recommender": """You are an internship recommendation engine.
        Based on the user's skills, interests, and experience level,
        suggest the most relevant internship roles.
        Always respond in valid JSON format only - no extra text.
        Be specific about role names, required skills, and learning roadmaps.""",

        "evaluator": """You are an AI evaluation assistant.
        Compare the given AI response with the expected answer.
        Score the similarity from 0.0 to 1.0 based on semantic meaning, not exact wording.
        Respond with only a JSON object: {"score": 0.85, "reason": "..."}"""
    }

    return prompts.get(role, prompts["career_assistant"])