import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

GROQ_API_KEY = "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"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

def generate_text(user_message: str) -> str:
    try:
        client = OpenAI(
            base_url=GROQ_BASE_URL,
            api_key=GROQ_API_KEY
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer concisely."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq Error: {e}")
        return f"Groq Error: {str(e)}"