# Arquitetura do projeto

## Visão geral

O sistema conecta-se à API do Gmail usando OAuth 2.0. Ele lê mensagens de contas específicas, classifica por categoria e salva os e-mails em um banco PostgreSQL.

## Componentes principais

### 1. Gmail API
- autenticação com Google OAuth
- leitura de mensagens
- criação de labels
- marcação como lida
- remoção da caixa de entrada (arquivamento)

### 2. Classificador
- regras por palavras-chave
- categorias iniciais: trabalho, processo seletivo, faculdade, propaganda, banco, outros

### 3. Banco de dados
- `gmail_account`
- `email_category`
- `processed_email`
- `sync_log`

### 4. Interface
- Streamlit para dashboard e controle manual
- monitoramento por categoria

## Fluxo

1. Usuário autentica as contas do Gmail.
2. Sistema lista mensagens recentes.
3. Mensagem é classificada com base em remetente, assunto e snippet.
4. Registro é salvo no banco.
5. Mensagem é marcada como lida e movida para uma label específica.
6. Dashboard exibe os dados consolidados.

## Objetivo

Centralizar a organização da caixa de entrada para reduzir ruído e manter mensagens importantes em categorias claras.
