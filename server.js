const express = require('express');
const bodyParser = require('body-parser');
const app = express();

app.use(bodyParser.json());

// Substitua 'chatbotsimples1234' pelo token que você inventou
const VERIFY_TOKEN = process.env.VERIFY_TOKEN || 'chatbotsimples1234';

// Rota para verificação do webhook (método GET) e recebimento de mensagens (método POST)
app.get('/', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode && token) {
    if (mode === 'subscribe' && token === VERIFY_TOKEN) {
      console.log('Webhook verificado com sucesso!');
      res.status(200).send(challenge);
    } else {
      console.error('Erro na verificação do token!');
      res.sendStatus(403);
    }
  }
});

app.post('/', (req, res) => {
  console.log('Mensagem recebida:');
  console.log(JSON.stringify(req.body, null, 2));
  // Futuramente, aqui você adicionará a lógica de resposta do chatbot
  res.status(200).send('OK');
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
