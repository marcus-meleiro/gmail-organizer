CREATE TABLE IF NOT EXISTS gmail_account (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (email_address)
);

CREATE TABLE IF NOT EXISTS email_category (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    label_name VARCHAR(150) NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS processed_email (
    id SERIAL PRIMARY KEY,
    gmail_message_id VARCHAR(255) NOT NULL,
    account_id INTEGER NOT NULL REFERENCES gmail_account(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES email_category(id),
    sender_email VARCHAR(255),
    sender_name VARCHAR(255),
    subject VARCHAR(500),
    snippet TEXT,
    received_at TIMESTAMP,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'saved',
    thread_id VARCHAR(255),
    UNIQUE (gmail_message_id, account_id)
);

CREATE TABLE IF NOT EXISTS sync_log (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES gmail_account(id) ON DELETE SET NULL,
    run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_processed INTEGER DEFAULT 0,
    total_saved INTEGER DEFAULT 0,
    total_ignored INTEGER DEFAULT 0,
    details TEXT
);

INSERT INTO email_category (category_name, slug, label_name, active)
VALUES
    ('Trabalho', 'trabalho', 'Trabalho', TRUE),
    ('Processo Seletivo', 'processo-seletivo', 'Processo Seletivo', TRUE),
    ('Faculdade', 'faculdade', 'Faculdade', TRUE),
    ('Propaganda', 'propaganda', 'Propaganda', TRUE),
    ('Banco', 'banco', 'Banco', TRUE),
    ('Outros', 'outros', 'Outros', TRUE)
ON CONFLICT (slug) DO NOTHING;
