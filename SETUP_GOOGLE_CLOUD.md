# Setup do Google Cloud OAuth para o Gmail Organizer

## 1) Criar projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto.
3. Dê um nome como: `gmail-organizer`

## 2) Ativar a Gmail API

1. No menu lateral, vá em `APIs e serviços` > `Biblioteca`.
2. Procure por `Gmail API`.
3. Clique em `Ativar`.

## 3) Criar credenciais OAuth

1. Vá em `APIs e serviços` > `Credenciais`.
2. Clique em `Criar credenciais` > `ID do cliente OAuth`.
3. Escolha o tipo: `Aplicativo de desktop`.
4. Dê um nome e salve.
5. Faça download do arquivo JSON.

## 4) Salvar o arquivo

Renomeie o arquivo baixado para:

```text
credentials.json
```

E salve na raiz do projeto, junto com os outros arquivos.

## 5) Rodar a autorização

No terminal dentro da pasta do projeto:

```bash
python3 scripts/authorize_gmail.py
```

Isso abre a janela de autorização do Google.

Você vai precisar:
- fazer login na sua conta Gmail
- aceitar os permissos
- depois o token será gravado em `token.json`

## 6) O que a aplicação usa

Escopos:

```text
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/gmail.labels
```

Esses permissos permitem:
- ler mensagens
- marcar como lidas
- criar labels
- mover e-mails para label específica
- manter fora da caixa de entrada

## 7) Importante

Se quiser usar múltiplas contas, você precisa autenticar cada uma separadamente, e depois configurar cada conta dentro do projeto.

## 8) Próximo passo

Depois que o `token.json` for gerado, eu te ajudo a implementar a sincronização real das 3 contas.
