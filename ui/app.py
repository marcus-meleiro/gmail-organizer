from __future__ import annotations

from sqlalchemy import func, select
import streamlit as st

from app.db import SessionLocal
from app.models import EmailCategory, GmailAccount, ProcessedEmail
from app.sync_service import SyncService


st.set_page_config(page_title="Gmail Organizer", page_icon="📬")
st.title("Gmail Organizer")
st.caption("Dashboard de e-mails por categoria e conta")

if st.sidebar.button("Sincronizar agora", type="primary"):
    with SessionLocal() as db:
        sync = SyncService(db)
        st.session_state["sync_result"] = sync.sync_account(
            account_name="Pessoal",
            email_address="marcusadrianomeleiro@gmail.com",
            account_type="pessoal",
            max_results=20,
        )

with SessionLocal() as db:
    category_counts = db.execute(
        select(EmailCategory.category_name, func.count(ProcessedEmail.id))
        .outerjoin(ProcessedEmail, EmailCategory.id == ProcessedEmail.category_id)
        .group_by(EmailCategory.category_name)
        .order_by(EmailCategory.category_name)
    ).all()

    account_counts = db.execute(
        select(GmailAccount.email_address, func.count(ProcessedEmail.id))
        .outerjoin(ProcessedEmail, GmailAccount.id == ProcessedEmail.account_id)
        .group_by(GmailAccount.email_address)
        .order_by(GmailAccount.email_address)
    ).all()

    recent_rows = db.execute(
        select(ProcessedEmail, GmailAccount.email_address, EmailCategory.category_name)
        .join(GmailAccount, ProcessedEmail.account_id == GmailAccount.id)
        .join(EmailCategory, ProcessedEmail.category_id == EmailCategory.id)
        .order_by(ProcessedEmail.saved_at.desc())
        .limit(10)
    ).all()

if "sync_result" in st.session_state:
    st.success(f"Sincronização concluída: {st.session_state['sync_result']}")

with st.sidebar:
    st.header("Contas")
    st.write("Pessoal")
    st.write("Profissional")
    st.write("Faculdade")

cols = st.columns(6)
metric_labels = ["Trabalho", "Processo Seletivo", "Faculdade", "Propaganda", "Banco", "Outros"]
for idx, label in enumerate(metric_labels):
    value = next((count for name, count in category_counts if name == label), 0)
    cols[idx].metric(label, value)

st.subheader("E-mails por conta")
account_cols = st.columns(len(account_counts) or 1)
for i, (email, count) in enumerate(account_counts or [("Sem dados", 0)]):
    account_cols[i].metric(email, count)

st.subheader("Últimos e-mails salvos")
for email, account_email, category_name in recent_rows:
    with st.container():
        st.markdown(f"**{email.subject or 'Sem assunto'}**")
        st.caption(f"{account_email} • {category_name} • {email.saved_at.strftime('%d/%m/%Y %H:%M') if email.saved_at else '-'}")
        st.write(email.snippet or "")
        st.divider()

if not recent_rows:
    st.info("Ainda não há e-mails salvos no banco. Execute a sincronização para popular o dashboard.")
