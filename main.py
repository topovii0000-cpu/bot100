from fastapi import FastAPI, Request
import httpx
import json
import uvicorn

app = FastAPI()

# Константы
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions?project_id=project_01k92gvcg6f8pveava7f06fw4g"
GROQ_API_KEY = "eyJhbGciOiJSUzI1NiIsImtpZCI6Imp3ay1saXZlLTMyNDg5ODNiLWEzYWYtNGVlZi1iZDAyLTQ4YTEyOWU3NmIyYSIsInR5cCI6IkpXVCJ9..."  # ← твой токен

HEADERS = {
    "accept": "application/json",
    "authorization": f"Bearer {GROQ_API_KEY}",
    "content-type": "application/json",
    "groq-organization": "org_01k92gvc0jf8ntz82tsctxyd12",
    "origin": "https://console.groq.com",
    "referer": "https://console.groq.com/",
    "user-agent": "FastAPI Client"
}

@app.post("/answer")
async def answer(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    # Формируем тело запроса
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "temperature": 1,
        "max_completion_tokens": 8192,
        "top_p": 1,
        "stop": None,
        "stream": False,  # убираем stream, чтобы получить обычный JSON
        "reasoning_effort": "medium"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_URL, headers=HEADERS, json=payload)

    # Проверяем статус
    if response.status_code != 200:
        return {"error": f"Groq API error {response.status_code}", "details": response.text}

    result = response.json()
    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"answer": content}

