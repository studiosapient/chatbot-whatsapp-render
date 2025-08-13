import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Carrega as variáveis de ambiente de um arquivo .env durante o desenvolvimento local.
# O Render gerencia isso diretamente no painel.
load_dotenv()

app = Flask(__name__)

# Configurações do chatbot
# Estas variáveis são lidas do ambiente do Render (ou do arquivo .env local)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Se alguma variável de ambiente estiver faltando, a aplicação não deve rodar
if not all([VERIFY_TOKEN, ACCESS_TOKEN, PHONE_NUMBER_ID]):
    print("Erro: Variáveis de ambiente faltando. Certifique-se de que VERIFY_TOKEN, ACCESS_TOKEN e PHONE_NUMBER_ID estão definidos.")
    exit()


# Rota de verificação do Webhook (GET)
# A Meta usa esta rota para verificar o seu servidor.
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
# Esta rota recebe todas as mensagens e eventos do WhatsApp.
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.json
    
    # Verifica se a requisição veio de uma conta do WhatsApp Business
    if data and "entry" in data and "changes" in data["entry"][0]:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:
                    message = change["value"]["messages"][0]
                    from_number = message["from"]
                    message_type = message.get("type", "text")

                    if message_type == "text":
                        text = message["text"]["body"]
                        print(f"Mensagem de texto recebida de {from_number}: {text}")
                        
                        # Processa a mensagem e gera uma resposta
                        response_text = process_message(text)
                        
                        # Envia a resposta de volta ao usuário
                        send_whatsapp_message(from_number, response_text)

                    else:
                        print(f"Tipo de mensagem não suportado: {message_type}")
                        # Opcional: Envie uma mensagem de erro ou um menu para tipos não suportados
                        send_whatsapp_message(from_number, "Desculpe, só consigo responder a mensagens de texto por enquanto.")

    return "OK", 200


# Função para enviar mensagens usando a API do WhatsApp Cloud
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
        print(f"Mensagem enviada com sucesso para {to_number}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem para {to_number}: {e}")


# Função para processar a lógica do chatbot (ponto de expansão)
def process_message(text):
    text_lower = text.lower().strip() # .strip() remove espaços em branco extras

    if "olá" in text_lower or "oi" in text_lower or "ola" in text_lower:
        return "Olá! Sou um chatbot de teste. Como posso ajudar você hoje?"
    elif "ajuda" in text_lower:
        return "Posso te ajudar com as seguintes opções: `produto`, `serviço`, ou `contato`."
    elif "produto" in text_lower:
        return "Temos vários produtos incríveis. Qual você gostaria de saber mais?"
    elif "serviço" in text_lower:
        return "Oferecemos diversos serviços de alta qualidade. Me diga qual te interessa."
    elif "contato" in text_lower:
        return "Você pode entrar em contato conosco pelo e-mail: contato@exemplo.com."
    else:
        return "Desculpe, não entendi. Poderia ser mais específico? Tente digitar `ajuda` para ver as opções."


# Se o arquivo for executado diretamente, inicia o servidor Flask em modo de depuração.
if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
