import os
import base64
import json
import tempfile
from datetime import datetime

import httpx
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
security = HTTPBearer()

# Firebase Credentials from environment variable
b64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")
if b64:
    cred_dict = json.loads(base64.b64decode(b64).decode("utf-8"))
    cred = credentials.Certificate(cred_dict)
else:
    cred = credentials.Certificate("firebase-service-account.json")

firebase_admin.initialize_app(cred)

#configurações
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID_TELEGRAM = os.getenv("CHAT_ID_TELEGRAM")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")

# Função para verificar o token do Firebase
async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")
    
# Enviar mensagem para o Telegram
async def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "chat_id": CHAT_ID_TELEGRAM, 
            "text": message,
            "parse_mode": "Markdown"
        })

    result = response.json()
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail=f"Failed to send message to Telegram: {result.get('description')}")
    
# POST endpoint to receive messages and send them to Telegram
@app.post("/api/emergencia/acionar")
async def acionar_emergencia(request: Request, user=Depends(verify_firebase_token)):
    body = await request.json()
    lat = body.get("latitude", 0)
    lon = body.get("longitude", 0)
    email = user.get("email", "unknown user")

    map_link = f"https://www.google.com/maps?q={lat},{lon}"
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        f"🚨 *Emergência acionada!* 🚨\n\n"
        f"Usuário: {email}\n"
        f"Data e Hora: {agora}\n"
        f"Localização: [Clique aqui]({map_link})"
    )

    await send_telegram_message(message)

    return {"status": "ok", "email": email, "latitude": lat, "longitude": lon, "timestamp": agora,
            "mensagem": "Mensagem enviada para o Telegram com sucesso."}

# POST webhook endpoint to receive messages from Telegram
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()

    message = body.get("message", {})
    if not message or not message.get("text"):
        return {"ok": True}  # Ignore non-text messages
    
    chat_id = message["chat"]["id"]
    text = message["text"].strip()

    if text.startswith("/start"):
        async with httpx.AsyncClient() as client:
            await client.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Olá! Este bot está configurado para receber mensagens de emergência. SOSEngasgo API está funcionando corretamente.",
                "parse_mode": "Markdown"
            })

    return {"ok": True}

# Registra o webhook do Telegram
# @app.on_event("startup")
# async def register_telegram_webhook():
#     async with httpx.AsyncClient() as client:
#         await client.get(
#             f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={TELEGRAM_WEBHOOK_URL}",
#             params={"url": TELEGRAM_WEBHOOK_URL}
#         )