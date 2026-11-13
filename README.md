# Gmail Organizer - Em Desenvolvimento

Sistema para organizar e-mails pessoais, profissionais e acadêmicos usando Python, Gmail API, PostgreSQL e Streamlit.

## Visão geral

Este projeto conecta múltiplas contas do Gmail, classifica mensagens por categoria e salva os registros em um banco PostgreSQL. Os e-mails são marcados como lidos e movidos para labels específicas no Gmail para sair da caixa de entrada sem perder o conteúdo.

## Contas suportadas

- Pessoal: `user@gmail.com`
- Profissional: `user.dev@gmail.com`
- Faculdade: `user@sga.pucminas.br`

## Categorias

- Trabalho
- Processo Seletivo
- Faculdade
- Propaganda
- Banco
- Outros

## Stack

- Python 3.11+
- Gmail API
- OAuth 2.0
- PostgreSQL
- SQLAlchemy
- Streamlit

## Estrutura do projeto

```text
.
├── app/
│   ├── __init__.py
│   ├── classifier.py
│   ├── config.py
│   ├── db.py
│   ├── gmail_service.py
│   ├── main.py
│   ├── models.py
│   ├── repository.py
│   └── sync_service.py
├── scripts/
│   ├── authorize_gmail.py
│   ├── sync_gmail.py
│   └── sync_preview.py
├── ui/
│   └── app.py
├── .env.example
├── .gitignore
├── README.md
├── SETUP_GOOGLE_CLOUD.md
├── docker-compose.yml
├── requirements.txt
├── token.json
└── credentials.json
```

## Pré-requisitos

- Python 3.11+
- Docker + Docker Compose
- Google Cloud Console com Gmail API ativada
- Conta Google autorizada via OAuth 2.0

## Configuração do banco

```bash
docker-compose up -d
python3 -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Autorização do Gmail

Crie o arquivo `credentials.json` no diretório da raiz do projeto, depois rode:

```bash
python3 scripts/authorize_gmail.py --email 
python3 scripts/authorize_gmail.py --email 
python3 scripts/authorize_gmail.py --email 
```

## Sincronização de e-mails

```bash
python3 scripts/sync_gmail.py --account-name "Pessoal" --email "user@gmail.com" --account-type pessoal --max-results 20
python3 scripts/sync_gmail.py --account-name "Profissional" --email "user@gmail.com" --account-type profissional --max-results 20
python3 scripts/sync_gmail.py --account-name "Faculdade" --email "user@sga.pucminas.br" --account-type faculdade --max-results 20
```

## Dashboard

```bash
streamlit run ui/app.py
```

## Observações

- o projeto permite múltiplas contas do Gmail com tokens separados
- e-mails são salvos em PostgreSQL para evitar duplicidade
- categoria e labels são aplicadas automaticamente por regras simples
- a organização está pronta para evoluir para regras mais inteligentes ou IA

## Próximo passo planejado

- melhorar o classificador com regras mais robustas
- adicionar filtros por data e categoria
- criar painel de revisão manual
- implementar busca por assunto/remetente
