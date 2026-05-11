import json
import logging
import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)

# --- 1. تحميل الإعدادات (مع محاولة ذكية للمسار) ---
config = {}
for path in ["app/config.json", "config.json"]:
    try:
        with open(path) as f:
            config = json.load(f)
            break
    except:
        continue

SYSTEM_PROMPT = "You are a helpful AI assistant. Keep it concise."

# --- 2. دالة OpenAI (المعدلة لتجنب الكراش) ---
def _call_openai(user_message: str) -> str:
    # جلب المفتاح من الملف أو استخدامه مباشرة
    cfg = config.get("OPENAI", {})
    
    # وضعنا مفتاحك هنا مباشرة لضمان العمل تحت أي ظرف
    api_key = "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"
    
    try:
        # إنشاء العميل جوا الدالة حصراً مشان ما يعمل Error أول ما يشتغل السيرفر
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=cfg.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI Direct Error: {e}")
        return f"OpenAI Error: {str(e)}"

# --- 3. الدالة الرئيسية ---
def generate_text(user_message: str) -> str:
    # جعلنا المزود ثابتاً لضمان تشغيل OpenAI فوراً
    try:
        return _call_openai(user_message)
    except Exception as e:
        logger.error(f"Error: {e}")
        return "حصل خطأ تقني، جربي مرة تانية."