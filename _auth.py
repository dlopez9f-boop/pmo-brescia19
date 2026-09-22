import streamlit as st
from pathlib import Path
import base64


def _logo_b64() -> str:
    p = Path(__file__).parent / "logo_nine.png"
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return ""


def require_auth():
    if st.session_state.get("_pwd_ok"):
        return

    def _submit():
        pwd = st.session_state.get("_pwd_input", "")
        st.session_state["_pwd_ok"] = (pwd == st.secrets["password_pmo"])

    logo = _logo_b64()
    logo_tag = (
        f'<img src="data:image/png;base64,{logo}" '
        f'style="height:52px;margin-bottom:18px;filter:brightness(0)" />'
        if logo else
        '<div style="font-size:32px;font-weight:900;color:#0B1F3A;margin-bottom:18px">9</div>'
    )

    st.markdown(f"""
    <style>
      #MainMenu, footer, header {{ visibility: hidden; }}
      [data-testid="stSidebar"] {{ display: none; }}
      [data-testid="stAppViewContainer"] {{ background: #F2F3F5; }}
      [data-testid="stAppViewBlockContainer"] {{ padding-top: 0 !important; }}

      /* Botón rojo corporativo */
      .stButton > button {{
        background-color: #D31224 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 7px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: .04em !important;
        padding: 11px 0 !important;
        width: 100% !important;
        transition: background .2s, box-shadow .2s !important;
        box-shadow: 0 2px 8px rgba(211,18,36,.18) !important;
      }}
      .stButton > button:hover {{
        background-color: #B00E1D !important;
        box-shadow: 0 4px 16px rgba(211,18,36,.35) !important;
      }}

      /* Input */
      [data-testid="stTextInput"] input {{
        background: #fff !important;
        border: 1.5px solid #DDE1E8 !important;
        border-radius: 7px !important;
        color: #0B1F3A !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
      }}
      [data-testid="stTextInput"] input:focus {{
        border-color: #D31224 !important;
        box-shadow: 0 0 0 3px rgba(211,18,36,.12) !important;
      }}
      [data-testid="stTextInput"] label {{
        color: #6B7280 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
      }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<div style='height:64px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
          background:#fff;
          border-radius:16px;
          border:1px solid #E5E8EF;
          box-shadow:0 8px 32px rgba(11,31,58,.08);
          padding:40px 36px 32px;
          text-align:center;
          margin-bottom:20px
        ">
          {logo_tag}
          <div style="font-size:10px;color:#9CA3AF;text-transform:uppercase;
                      letter-spacing:3px;margin-bottom:8px">
            Nine Fitness Group S.L.
          </div>
          <div style="font-size:20px;font-weight:800;color:#0B1F3A;
                      letter-spacing:.02em;margin-bottom:4px">
            DIRECCIÓN DE OBRA
          </div>
          <div style="font-size:10px;color:#C0C5CF;text-transform:uppercase;
                      letter-spacing:2px;margin-top:2px">
            Acceso restringido · PMO
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.text_input(
            "Contraseña de acceso",
            type="password",
            key="_pwd_input",
            on_change=_submit,
            placeholder="Introduce la contraseña...",
        )
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("Acceder al Panel →", use_container_width=True):
            _submit()

        if "_pwd_ok" in st.session_state and not st.session_state["_pwd_ok"]:
            st.error("Contraseña incorrecta.")

        st.markdown("""
        <p style="text-align:center;color:#C0C5CF;font-size:11px;margin-top:18px">
          Plataforma exclusiva · Equipo PMO y Dirección Técnica
        </p>
        """, unsafe_allow_html=True)

    st.stop()
