# SOS Engasgo API - Telegram Integration

API FastAPI que integra autenticação Firebase com notificações via Telegram e persistência em MongoDB. Projeto desenvolvido para comunicação segura com alertas em tempo real e armazenamento de dados.

## 📋 Descrição

Esta é uma API RESTful desenvolvida com **FastAPI** que oferece:

- ✅ Autenticação segura com Firebase
- ✅ Integração com Telegram Bot para envio de mensagens
- ✅ Armazenamento de dados em MongoDB
- ✅ Endpoints protegidos por tokens JWT
- ✅ Pronto para deploy no Vercel
- ✅ Variáveis de ambiente para configuração segura

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno para Python
- **Firebase Admin SDK** - Autenticação e verificação de tokens
- **MongoDB** - Banco de dados NoSQL
- **Motor** - Driver assíncrono para MongoDB
- **HTTPX** - Cliente HTTP assíncrono
- **Uvicorn** - Servidor ASGI
- **Python-dotenv** - Gerenciamento de variáveis de ambiente

## 📦 Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta Firebase
- Telegram Bot Token
- MongoDB (local ou cloud - ex: MongoDB Atlas)
- Connection String do MongoDB

## ⚙️ Configuração

### 1. Criar Ambiente Virtual

```bash
python3 -m venv .venv
```

### 2. Ativar o Ambiente Virtual

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Firebase
FIREBASE_CREDENTIALS_BASE64=<sua_credencial_firebase_em_base64>

# Telegram
TELEGRAM_BOT_TOKEN=<seu_telegram_bot_token>
CHAT_ID_TELEGRAM=<seu_chat_id>
TELEGRAM_WEBHOOK_URL=<url_do_webhook>

# MongoDB
MONGODB_URI=mongodb+srv://<usuario>:<senha>@cluster.mongodb.net/sosengasgo
MONGODB_DATABASE=sosengasgo
```

**Notas:**
- Se `FIREBASE_CREDENTIALS_BASE64` não estiver configurada, a API tentará carregar o arquivo `firebase-service-account.json`
- Para MongoDB local, use: `mongodb://localhost:27017/sosengasgo`
- Para MongoDB Atlas, obtenha a connection string no dashboard da sua conta

### 5. Executar a API Localmente

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

Acesse a documentação interativa em `http://localhost:8000/docs`

## 🌍 Ambiente de Produção

A API está publicada na Vercel em:

- [https://sosengasgo-api-telegram.vercel.app](https://sosengasgo-api-telegram.vercel.app)
- [https://sosengasgo-api-telegram.vercel.app/docs](https://sosengasgo-api-telegram.vercel.app/docs)

## 🔐 Autenticação

Todos os endpoints protegidos utilizam **Firebase ID Tokens** via Bearer Token:

```bash
curl -H "Authorization: Bearer <seu_firebase_token>" http://localhost:8000/seu-endpoint
```

## 📨 Funcionalidades

### Envio de Mensagens no Telegram

A API permite enviar mensagens formatadas para um chat específico no Telegram:

```python
async def send_telegram_message(message: str):
    # Envia mensagem Markdown para o Telegram
```

As mensagens suportam formatação **Markdown**.

### Armazenamento em MongoDB

A API utiliza MongoDB para persistir dados de forma assíncrona:

- Armazenamento de logs de eventos
- Histórico de mensagens enviadas
- Dados de usuários autenticados
- Registros de operações

## 📁 Estrutura de Arquivos

```
├── main.py                        # Arquivo principal da API
├── requirements.txt               # Dependências do projeto
├── firebase-service-account.json  # Credenciais Firebase (não comitar)
├── .env                          # Variáveis de ambiente (não comitar)
├── vercel.json                   # Configuração para deploy Vercel
└── README.md                     # Este arquivo
```

## 🌐 Deploy no Vercel

Este projeto está configurado para deploy automático no Vercel.

### Configurar Variáveis de Ambiente no Vercel:

1. Acesse o dashboard do Vercel
2. Vá em **Settings** → **Environment Variables**
3. Adicione:
   - `FIREBASE_CREDENTIALS_BASE64`
   - `TELEGRAM_BOT_TOKEN`
   - `CHAT_ID_TELEGRAM`
   - `TELEGRAM_WEBHOOK_URL`
    - `MONGODB_URI`
   - `MONGODB_DATABASE`

### Fazer Deploy:

```bash
npm install -g vercel
vercel
```

## ⚠️ Segurança

- ⛔ **Nunca** commite o arquivo `firebase-service-account.json` no repositório
- ⛔ **Nunca** commite o arquivo `.env` no repositório
- ✅ Use variáveis de ambiente para dados sensíveis
- ✅ Mantenha os tokens atualizados
- ✅ Valide todos os tokens de entrada

Adicione ao `.gitignore`:
```
.env
firebase-service-account.json
.venv/
__pycache__/
*.pyc
.DS_Store
```

## 📝 Desativar Ambiente Virtual

Quando terminar de trabalhar, desative o ambiente virtual:

```bash
deactivate
```

## 🐛 Troubleshooting

### Firebase Token Inválido
- Verifique se o token ainda é válido
- Confirme se as credenciais estão corretas

### Erro ao Enviar para Telegram
- Verifique o `TELEGRAM_BOT_TOKEN`
- Confirme se o `CHAT_ID_TELEGRAM` está correto
- Teste o bot manualmente no Telegram

### Erro de Conexão com MongoDB
- Verifique se o `MONGODB_URI` está correto
- Confirme se a conexão de rede está disponível
- Para MongoDB local, certifique-se de que o serviço está rodando
- Para MongoDB Atlas, verifique as permissões de IP whitelist

### Erro de Importação
- Certifique-se de que o ambiente virtual está ativado
- Execute `pip install -r requirements.txt` novamente

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.

---

**Autor:** SOS Engasgo  
**Data:** 2026  
**Versão:** 1.0.0
