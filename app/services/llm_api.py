import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# --- إعدادات Groq المجانية ---
# المفتاح الذي أرسلتِه يا هندسة
GROQ_API_KEY = "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"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

def generate_text(user_message: str) -> str:
    """استدعاء Groq المجاني باستخدام مكتبة OpenAI"""
    try:
        # الربط مع سيرفرات Groq
        client = OpenAI(
            base_url=GROQ_BASE_URL,
            api_key=GROQ_API_KEY
        )
        
        # استخدام موديل Llama 3 (مجاني وسريع جداً)
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Keep your responses concise and friendly."
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq Error: {e}")
        # إرجاع الخطأ لتسهيل تتبعه في تلغرام
        return f"يا هندسة، حصل خطأ في Groq: {str(e)}"