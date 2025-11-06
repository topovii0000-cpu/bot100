import os
from fastapi import FastAPI, Request
import httpx
import json

app = FastAPI()

# Groq API данные
GROQ_URL = os.getenv(
    "GROQ_URL",
    "https://api.groq.com/openai/v1/chat/completions?project_id=project_01k92gvcg6f8pveava7f06fw4g"
)
GROQ_ORG = os.getenv("GROQ_ORG", "org_01k92gvc0jf8ntz82tsctxyd12")

# Stytch API
STYTCH_AUTH_URL = "https://api.stytchb2b.groq.com/sdk/v1/b2b/sessions/authenticate"
STYTCH_AUTH_HEADERS = {
    "accept": "*/*",
    "authorization": "Basic cHVibGljLXRva2VuLWxpdmUtNThkZjU3YTktYTFmNS00MDY2LWJjMGMtMmZmOTQyZGI2ODRmOndGeFZiMGR4MGhaUkVTRV9uQkVHU0Z2Z21BMF90QlVGZkczOV80ckY0eHQ0",
    "content-type": "application/json",
    "origin": "https://console.groq.com",
    "referer": "https://console.groq.com/",
    "user-agent": "FastAPI Client",
    "x-sdk-client": "...",  # сюда вставь данные x-sdk-client из curl
    "x-sdk-parent-host": "https://console.groq.com"
}

@app.post("/answer")
async def answer(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    async with httpx.AsyncClient() as client:
        # 1️⃣ Аутентификация на Stytch
        auth_resp = await client.post(STYTCH_AUTH_URL, headers=STYTCH_AUTH_HEADERS, json={})
        if auth_resp.status_code != 200:
            return {"error": "Stytch authentication failed", "details": auth_resp.text}
        
        auth_data = auth_resp.json()
        session_jwt = auth_data.get("session_jwt") or auth_data.get("data", {}).get("session_jwt")
        if not session_jwt:
            return {"error": "session_jwt not found in Stytch response"}

        # 2️⃣ Запрос к Groq API с использованием session_jwt в заголовках
        groq_headers = {
            "accept": "application/json",
            "authorization": f"Bearer {session_jwt}",
            "content-type": "application/json",
            "groq-organization": GROQ_ORG,
            "origin": "https://console.groq.com",
            "referer": "https://console.groq.com/",
            "user-agent": "FastAPI Client"
        }

        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": "Правильные ответы пиши в [], если их несколько то через запятую!"},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.2,
            "max_completion_tokens": 8192,
            "stop": None,
            "stream": False,
            "reasoning_effort": "high"
        }

        groq_resp = await client.post(GROQ_URL, headers=groq_headers, json=payload)
        if groq_resp.status_code != 200:
            return {"error": f"Groq API error {groq_resp.status_code}", "details": groq_resp.text}

        result = groq_resp.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"answer": content, "session_jwt": session_jwt}

@app.get("/")
async def root():
    return {"status": "API is running"}
