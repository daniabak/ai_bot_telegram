import json
import logging
import httpx
import google.generativeai as genai
from openai import OpenAI  # استيراد مكتبة OpenAI الرسمية

logger = logging.getLogger(__name__)

# تحميل الإعدادات من المسار الصحيح
try:
    with open("app/config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    # احتياطياً في حال كان الملف في المجلد الرئيسي مباشرة
    with open("config.json") as f:
        config = json.load(f)

PROVIDER = config.get("LLM_PROVIDER", "openai") # افتراضياً OpenAI الآن

SYSTEM_PROMPT = (
    "You are a helpful AI assistant available via Telegram. "
    "Keep responses concise — ideally under 200 words — since users are on a messaging app. "
    "Use short paragraphs for readability."
)

# --- إعداد عملاء المكتبات الرسمية ---
openai_cfg = config.get("OPENAI", {})
openai_client = OpenAI(api_key=openai_cfg.get("API_KEY", ""))

# --- دوال الاستدعاء ---

def _call_openai(user_message: str) -> str:
    """استخدام مكتبة OpenAI الرسمية (الأكثر استقراراً)"""
    model = openai_cfg.get("MODEL_NAME", "gpt-4o-mini")
    
    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        max_tokens=800
    )
    return response.choices[0].message.content

def _call_gemini(user_message: str) -> str:
    """استخدام مكتبة جوجل الرسمية"""
    cfg = config.get("GEMINI", {})
    api_key = cfg.get("API_KEY", "")
    model_name = cfg.get("MODEL_NAME", "gemini-1.5-flash")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}"
    response = model.generate_content(full_prompt)
    
    return response.text

def _call_ollama(user_message: str) -> str:
    """Call Ollama's native API via httpx."""
    cfg = config.get("OLLAMA", {})
    endpoint = cfg.get("ENDPOINT", "http://localhost:11434")
    model = cfg.get("MODEL_NAME", "llama3")

    with httpx.Client(timeout=120) as client:
        resp = client.post(
            f"{endpoint}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            }
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

def _call_openai_compatible(user_message: str, base_url: str, api_key: str, model: str) -> str:
    """استدعاء يدوي للمنصات المتوافقة مثل OpenRouter"""
    with httpx.Client(timeout=120) as client:
        resp = client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ]
            }
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

# --- الدالة الرئيسية التي يستدعيها البوت ---

def generate_text(user_message: str) -> str:
    """توليد الرد بناءً على المزود المختار في الإعدادات."""
    try:
        if PROVIDER == "openai":
            return _call_openai(user_message)
            
        elif PROVIDER == "gemini":
            return _call_gemini(user_message)
            
        elif PROVIDER == "openrouter":
            cfg = config.get("OPENROUTER", {})
            return _call_openai_compatible(
                user_message,
                base_url="https://openrouter.ai/api/v1",
                api_key=cfg.get("API_KEY", ""),
                model=cfg.get("MODEL_NAME", "meta-llama/llama-3-8b-instruct")
            )
            
        elif PROVIDER == "ollama":
            return _call_ollama(user_message)
            
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")
            
    except Exception as e:
        logger.error(f"LLM error ({PROVIDER}): {e}")
        return "عذراً ، واجهت مشكلة في معالجة طلبك حالياً. حاول مرة أخرى لاحقاً."