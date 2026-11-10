# Configuração da autenticação do Gmail

## Passo a passo

1. Acesse o Google Cloud Console.
2. Crie um projeto novo.
3. Ative a API Gmail.
4. Crie credenciais OAuth 2.0.
5. Baixe o arquivo `credentials.json`.
6. Coloque o arquivo na raiz do projeto.
7. Configure as variáveis no arquivo `.env`.
8. Execute a aplicação e autentique a conta.

## Escopos usados

```text
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/gmail.labels
```

## Observação

A autenticação deve ser feita manualmente pela conta do usuário. Cada conta precisa ser consentida no Google.
