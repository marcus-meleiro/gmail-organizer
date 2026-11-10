from __future__ import annotations

from sqlalchemy import func, select
import streamlit as st
from streamlit.components.v1 import html

from app.db import SessionLocal
from app.models import EmailCategory, GmailAccount, ProcessedEmail
from app.sync_service import SyncService


st.set_page_config(page_title="Gmail Organizer", page_icon="📬", layout="wide")


def render_3d_bg() -> None:
    html(
        """
        <div id="mail-3d-bg"></div>
        <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
        <script>
        (() => {
          const host = document.getElementById('mail-3d-bg');
          if (!host) return;
          if (host.dataset.ready === 'true') return;
          host.dataset.ready = 'true';
          host.style.position = 'fixed';
          host.style.inset = '0';
          host.style.pointerEvents = 'none';
          host.style.zIndex = '0';
          host.style.background = 'radial-gradient(circle at top, rgba(28, 92, 255, 0.18), transparent 35%), linear-gradient(180deg, rgba(8, 13, 27, 0.9), rgba(3, 6, 14, 1))';

          const scene = new THREE.Scene();
          scene.fog = new THREE.FogExp2(0x08111f, 0.08);

          const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
          camera.position.z = 8;

          const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
          renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
          renderer.setSize(window.innerWidth, window.innerHeight);
          host.appendChild(renderer.domElement);

          const group = new THREE.Group();
          scene.add(group);

          const ambient = new THREE.AmbientLight(0x7dd3fc, 1.4);
          scene.add(ambient);

          const pointLight = new THREE.PointLight(0x7c3aed, 20, 50, 2);
          pointLight.position.set(0, 3, 6);
          scene.add(pointLight);

          const colors = [0x60a5fa, 0x8b5cf6, 0x22d3ee, 0x34d399];
          const meshes = [];

          for (let i = 0; i < 24; i += 1) {
            const geometry = new THREE.IcosahedronGeometry(0.32 + Math.random() * 0.7, 1);
            const material = new THREE.MeshStandardMaterial({
              color: colors[i % colors.length],
              emissive: colors[i % colors.length],
              emissiveIntensity: 0.6,
              metalness: 0.3,
              roughness: 0.4,
              transparent: true,
              opacity: 0.9,
            });
            const mesh = new THREE.Mesh(geometry, material);
            const radius = 2.4 + Math.random() * 3.8;
            const angle = (i / 24) * Math.PI * 2;
            mesh.position.set(
              Math.cos(angle) * radius,
              (Math.random() - 0.5) * 4,
              Math.sin(angle) * radius
            );
            mesh.rotation.set(Math.random() * 2, Math.random() * 2, Math.random() * 2);
            group.add(mesh);
            meshes.push(mesh);
          }

          const ring = new THREE.Mesh(
            new THREE.TorusGeometry(2.6, 0.025, 24, 200),
            new THREE.MeshStandardMaterial({
              color: 0x93c5fd,
              emissive: 0x93c5fd,
              emissiveIntensity: 1.1,
              transparent: true,
              opacity: 0.7,
            })
          );
          ring.rotation.x = Math.PI / 2.5;
          group.add(ring);

          function animate() {
            requestAnimationFrame(animate);
            group.rotation.y += 0.0035;
            group.rotation.x += 0.0015;
            ring.rotation.z += 0.004;
            meshes.forEach((mesh, index) => {
              mesh.rotation.x += 0.005 + index * 0.0008;
              mesh.rotation.y += 0.006 + index * 0.0007;
            });
            renderer.render(scene, camera);
          }

          animate();

          const resize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
          };

          window.addEventListener('resize', resize);
        })();
        </script>
        """,
        height=0,
    )


def load_dashboard_data():
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
            .limit(8)
        ).all()

        return category_counts, account_counts, recent_rows


st.markdown(
    """
    <style>
    html, body { background: #080d18; }
    .block-container {
        position: relative;
        z-index: 1;
        padding-top: 1.6rem !important;
        max-width: 1440px !important;
    }
    .glass {
        background: rgba(13, 20, 33, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 20px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.28);
    }
    .hero {
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
    }
    .eyebrow {
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #8bd3ff;
        margin-bottom: 0.6rem;
        font-weight: 700;
    }
    h1 {
        font-size: 2.7rem !important;
        line-height: 1.06 !important;
        margin: 0 0 0.65rem !important;
        color: #f8fbff !important;
    }
    .sub {
        color: #b7c6db !important;
        font-size: 1rem !important;
    }
    .metric-card {
        padding: 1.1rem 1.2rem;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(15, 22, 31, 0.9), rgba(10, 14, 22, 0.82));
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .metric-card .label {
        color: #a7b7d6;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.5rem;
    }
    .metric-card .value {
        color: #eef6ff;
        font-size: 2.0rem;
        font-weight: 700;
    }
    .section-title {
        color: #eef6ff;
        font-size: 1.05rem;
        font-weight: 650;
        margin: 1.2rem 0 0.85rem 0;
    }
    .mail-item {
        padding: 1rem 1rem 0.9rem;
        border-radius: 16px;
        background: rgba(13, 19, 29, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.12);
        margin-bottom: 0.85rem;
    }
    .mail-item strong {
        color: #f8fbff;
        font-size: 1rem;
    }
    .mail-item .meta {
        color: #8dd3ff;
        font-size: 0.78rem;
        margin-bottom: 0.5rem;
    }
    .mail-item .snippet {
        color: #c7d4ea;
        font-size: 0.92rem;
        line-height: 1.5;
    }
    .stButton > button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #38bdf8, #8b5cf6);
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 18px 38px rgba(96, 165, 250, 0.28);
        padding: 0.8rem 1.5rem !important;
    }
    .stSidebar {
        background: rgba(7, 12, 19, 0.74) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

render_3d_bg()

st.markdown(
    """
    <div class='glass hero'>
      <div class='eyebrow'>Gmail workflow</div>
      <h1>Gmail Organizer</h1>
      <div class='sub'>Mensagens organizadas por conta, categoria e prioridade.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("Sincronizar agora", type="primary"):
    with SessionLocal() as db:
        sync = SyncService(db)
        st.session_state["sync_result"] = sync.sync_account(
            account_name="Pessoal",
            email_address="marcusadrianomeleiro@gmail.com",
            account_type="pessoal",
            max_results=20,
        )

if "sync_result" in st.session_state:
    st.success(f"Sincronização concluída: {st.session_state['sync_result']}")

category_counts, account_counts, recent_rows = load_dashboard_data()

metric_labels = ["Trabalho", "Processo Seletivo", "Faculdade", "Propaganda", "Banco", "Outros"]
metrics = st.columns(6)
for idx, label in enumerate(metric_labels):
    value = next((count for name, count in category_counts if name == label), 0)
    with metrics[idx]:
        st.markdown(
            f"""
            <div class='metric-card'>
              <div class='label'>{label}</div>
              <div class='value'>{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div class='section-title'>E-mails por conta</div>", unsafe_allow_html=True)
account_cols = st.columns(len(account_counts) or 1)
for i, (email, count) in enumerate(account_counts or [("Sem dados", 0)]):
    with account_cols[i]:
        st.markdown(
            f"""
            <div class='metric-card'>
              <div class='label'>{email}</div>
              <div class='value'>{count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div class='section-title'>Últimos e-mails salvos</div>", unsafe_allow_html=True)
if recent_rows:
    for email, account_email, category_name in recent_rows:
        st.markdown(
            f"""
            <div class='mail-item'>
              <strong>{email.subject or 'Sem assunto'}</strong>
              <div class='meta'>{account_email} • {category_name} • {email.saved_at.strftime('%d/%m/%Y %H:%M') if email.saved_at else '-'}</div>
              <div class='snippet'>{(email.snippet or '').replace('<', '&lt;').replace('>', '&gt;')[:220]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("Ainda não há e-mails salvos. Execute a sincronização para popular o dashboard.")
