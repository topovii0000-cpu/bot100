import os
from fastapi import FastAPI, Request
import httpx
import json

app = FastAPI()

# Получаем данные из переменных окружения
GROQ_URL = os.getenv("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions?project_id=project_01k92gvcg6f8pveava7f06fw4g")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ORG = os.getenv("GROQ_ORG", "org_01k92gvc0jf8ntz82tsctxyd12")

HEADERS = {
    "accept": "application/json",
    "authorization": f"Bearer {GROQ_API_KEY}",
    "content-type": "application/json",
    "groq-organization": GROQ_ORG,
    "origin": "https://console.groq.com",
    "referer": "https://console.groq.com/",
    "user-agent": "FastAPI Client"
}

@app.post("/answer")
async def answer(request: Request):
    # Проверяем наличие API ключа
    if not GROQ_API_KEY:
        return {"error": "API key not configured"}
    
    data = await request.json()
    user_message = data.get("message", "")

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "temperature": 1,
        "max_completion_tokens": 8192,
        "top_p": 1,
        "stop": None,
        "stream": False,
        "reasoning_effort": "medium"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        return {"error": f"Groq API error {response.status_code}", "details": response.text}

    result = response.json()
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"answer": content}

# Добавляем корневой эндпоинт
@app.get("/")
async def root():
    return {"status": "API is running"}
