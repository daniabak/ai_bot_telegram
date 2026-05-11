import json
import logging
import httpx

logger = logging.getLogger(__name__)

# Load config
with open("app/config.json") as f:
    config = json.load(f)

PROVIDER = config.get("LLM_PROVIDER", "ollama")

SYSTEM_PROMPT = (
    "You are a helpful AI assistant available via Telegram. "
    "Keep responses concise — ideally under 200 words — since users are on a messaging app. "
    "Use short paragraphs for readability."
)

def _call_ollama(user_message: str) -> str:
    """Call Ollama's native API."""
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
    """Call any OpenAI-compatible API (OpenAI, OpenRouter, etc.)."""
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

def _call_gemini(user_message: str) -> str:
    """Call Google Gemini API."""
    cfg = config.get("GEMINI", {})
    api_key = cfg.get("API_KEY", "")
    model = cfg.get("MODEL_NAME", "gemini-2.0-flash")

    with httpx.Client(timeout=120) as client:
        resp = client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            json={
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"parts": [{"text": user_message}]}]
            }
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def generate_text(user_message: str) -> str:
    """Generate a response using the configured LLM provider."""
    try:
        if PROVIDER == "ollama":
            return _call_ollama(user_message)
        elif PROVIDER == "openai":
            cfg = config.get("OPENAI", {})
            return _call_openai_compatible(
                user_message,
                base_url="https://api.openai.com/v1",
                api_key=cfg.get("API_KEY", ""),
                model=cfg.get("MODEL_NAME", "gpt-4o-mini")
            )
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
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")
    except Exception as e:
        logger.error(f"LLM error ({PROVIDER}): {e}")
        return "Sorry, I'm having trouble processing your request right now."