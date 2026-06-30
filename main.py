import os
import base64
import json
from datetime import datetime

import httpx
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from pymongo import MongoClient

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

# MongoDB connection
mongo = MongoClient(os.getenv("MONGODB_URI"))
db_mongo = mongo["SOSEngasgo"]
respostas_col = db_mongo["respostas_emergencia"]

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
    uid = user.get("uid", "unknown uid")
    acionamento_id = body.get("acionamento_id", "unknown id")

    # chave única: id_uid
    chave = f"{acionamento_id}_{uid}"

    map_link = f"https://www.google.com/maps?q={lat},{lon}"
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        f"🚨 *Emergência acionada!* 🚨\n\n"
        f"Usuário: {email}\n"
        f"Data e Hora: {agora}\n"
        f"Localização: [Clique aqui]({map_link}). \n\n"
        f"Para confirmar que está a caminho, responda com: \n"
        f"`/confirmado {chave}`\n"
    )

    await send_telegram_message(message)

    return {"status": "ok", "email": email, "latitude": lat, "longitude": lon, "timestamp": agora,
            "chave": chave,
            "mensagem": "Mensagem enviada para o Telegram com sucesso."}

# GET endpoint to confirm the emergency response
@app.get("/api/emergencia/status/{chave}")
async def confirmar_status(chave: str, user=Depends(verify_firebase_token)):
    # Verifica se a chave existe no banco de dados
    resposta = respostas_col.find_one({"chave": chave}, {"_id": 0})
    if not resposta:
        return {"confirmado": False, "status": "not_found", "mensagem": "Chave não encontrada."}

    return {"confirmado": True, "status": "ok", "mensagem": "Status confirmado com sucesso.", "resposta": resposta.get("resposta"), "por": resposta.get("por")}


# POST webhook endpoint to receive messages from Telegram
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()

    message = body.get("message", {})
    if not message or not message.get("text"):
        return {"ok": True}  # Ignore non-text messages
    
    chat_id = message["chat"]["id"]
    text = message["text"].strip()
    nome = message.get("from", {}).get("first_name", "Responsável")

    if text.startswith("/start"):
        async with httpx.AsyncClient() as client:
            await client.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Olá! Este bot está configurado para receber mensagens de emergência. SOSEngasgo API está funcionando corretamente.",
                "parse_mode": "Markdown"
            })

    # /confirmado {chave}
    if text.startswith("/confirmado"):
        partes = text.split(" ", 1)
        if len(partes) == 2:
            chave = partes[1].strip()

            # Salva no MongoDB
            respostas_col.update_one(
                {"chave": chave},
                {"$set": {
                    "chave": chave,
                    "resposta": f"{nome} está a caminho!",
                    "por": nome,
                    "timestamp": datetime.now().isoformat()
                }},
                upsert=True
            )

            # Confirma para o responsável no Telegram
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": chat_id, "text": f"✅ Confirmado! {nome} está a caminho."}
                )

    return {"ok": True}

# Registra o webhook do Telegram
# @app.on_event("startup")
# async def register_telegram_webhook():
#     async with httpx.AsyncClient() as client:
#         await client.get(
#             f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={TELEGRAM_WEBHOOK_URL}",
#             params={"url": TELEGRAM_WEBHOOK_URL}
#         )