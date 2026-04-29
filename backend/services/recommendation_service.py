# recommendation_service.py - Generates internship recommendations using AI + RAG
# Combines RAG similarity search with Groq LLM for intelligent suggestions

import json
from services.groq_client import chat_with_groq, get_system_prompt
from services.rag_service import retrieve_relevant_internships


def generate_recommendations(skills: list, interests: str, experience_level: str) -> dict:
    """
    Generate personalized internship recommendations.
    Steps:
        1. Use RAG to find relevant internships from our dataset
        2. Ask Groq to reason over them and generate structured output
        3. Parse and return the recommendations

    Args:
        skills: List of user skills e.g. ["Python", "ML"]
        interests: Free text e.g. "I love building AI products"
        experience_level: "beginner", "intermediate", or "advanced"

    Returns:
        Dict with recommendations list and general advice
    """

    # Step 1 - RAG: Find relevant internships from our dataset
    relevant_internships = retrieve_relevant_internships(skills, interests, top_k=4)

    # Format them for the prompt
    internship_context = json.dumps(relevant_internships, indent=2)

    # Step 2 - Build the prompt for Groq
    prompt = f"""
You are an internship recommendation engine.

USER PROFILE:
- Skills: {', '.join(skills)}
- Interests: {interests}
- Experience Level: {experience_level}

RELEVANT INTERNSHIPS FROM OUR DATABASE:
{internship_context}

Based on this profile and the internship data above, respond ONLY with a valid JSON object.
No extra text, no markdown, just raw JSON in this exact format:

{{
  "recommendations": [
    {{
      "role": "Role Name",
      "company_type": "Startup / MNC / Research Lab",
      "skills_required": ["skill1", "skill2", "skill3"],
      "learning_roadmap": ["step1", "step2", "step3", "step4"],
      "difficulty": "Beginner / Intermediate / Advanced"
    }}
  ],
  "advice": "One paragraph of personalized career advice for this user."
}}

Provide exactly 3 recommendations. Make them specific and actionable.
"""

    messages = [
        {"role": "system", "content": get_system_prompt("recommender")},
        {"role": "user", "content": prompt}
    ]

    # Step 3 - Call Groq
    raw_response = chat_with_groq(messages, temperature=0.5, max_tokens=1500)

    # Step 4 - Parse JSON response safely
    try:
        # Clean up response in case there's any extra text
        cleaned = raw_response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        result = json.loads(cleaned)
        return result

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"Raw response: {raw_response}")

        # Fallback response if parsing fails
        return {
            "recommendations": [
                {
                    "role": "Python Backend Intern",
                    "company_type": "Startup",
                    "skills_required": skills[:3] if skills else ["Python", "APIs", "SQL"],
                    "learning_roadmap": [
                        "Strengthen core Python skills",
                        "Learn FastAPI or Flask",
                        "Build a REST API project",
                        "Deploy on Render"
                    ],
                    "difficulty": experience_level.capitalize()
                }
            ],
            "advice": f"Based on your skills in {', '.join(skills[:2]) if skills else 'technology'}, focus on building real projects and applying consistently."
        }