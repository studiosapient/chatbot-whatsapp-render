import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configurações do chatbot (melhor usar variáveis de ambiente no Render)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


# Rota de verificação do Webhook (GET)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado com sucesso!")
        return challenge, 200
    else:
        print("Falha na verificação do Webhook.")
        return "Erro de verificação", 403


# Rota para receber mensagens (POST)
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.json
    
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:
                    message = change["value"]["messages"][0]
                    from_number = message["from"]
                    text = message["text"]["body"]
                    
                    print(f"Mensagem recebida de {from_number}: {text}")
                    
                    # --- Sua Lógica de Chatbot Aqui ---
                    # Processa a mensagem e gera uma resposta
                    response_text = process_message(text)
                    
                    # Envia a resposta de volta ao usuário
                    send_whatsapp_message(from_number, response_text)
    
    return "OK", 200

# Função para enviar mensagens via a API do WhatsApp
def send_whatsapp_message(to_number, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Levanta um erro para respostas HTTP ruins
        print("Mensagem enviada com sucesso!")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")

# Exemplo de uma função de lógica simples para o chatbot
def process_message(text):
    text_lower = text.lower()
    if "olá" in text_lower or "oi" in text_lower:
        return "Olá! Como posso ajudar você?"
    elif "ajuda" in text_lower:
        return "Posso te ajudar com as seguintes opções: produto, serviço, ou contato."
    elif "produto" in text_lower:
        return "Temos vários produtos. Qual você gostaria de saber mais?"
    else:
        return "Desculpe, não entendi. Poderia ser mais claro?"

if __name__ == "__main__":
    app.run(debug=True)
