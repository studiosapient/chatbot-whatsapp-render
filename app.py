from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# Substitua 'chatbotsimples1234' pelo token que você inventou
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'chatbotsimples1234')

# Rota para verificação do webhook (método GET) e recebimento de mensagens (método POST)
@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Lógica de verificação do webhook da Meta
        hub_mode = request.args.get("hub.mode")
        hub_challenge = request.args.get("hub.challenge")
        hub_verify_token = request.args.get("hub.verify_token")

        if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
            print("Webhook verificado com sucesso!")
            return hub_challenge, 200
        else:
            print("Erro na verificação do webhook!")
            return "Erro na verificação do token", 403

    if request.method == "POST":
        # Lógica para receber e processar as mensagens
        data = request.json
        print("Mensagem recebida:")
        print(json.dumps(data, indent=2))
        # Futuramente, aqui você adicionará a lógica de resposta do chatbot
        return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
