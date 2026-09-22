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
        f'style="height:48px;margin-bottom:20px;filter:brightness(0)" />'
        if logo else
        '<div style="font-size:28px;font-weight:900;color:#0B1F3A;margin-bottom:16px">NINE FITNESS</div>'
    )

    st.markdown("""
    <style>
      /* Ocultar chrome Streamlit */
      #MainMenu, footer, header { visibility: hidden !important; }
      [data-testid="stSidebar"] { display: none !important; }

      /* Fondo blanco total */
      html, body,
      [data-testid="stAppViewContainer"],
      [data-testid="stAppViewBlockContainer"],
      [data-testid="block-container"],
      .main, .block-container,
      section[data-testid="stMain"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
      }
      [data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }

      /* Botón gold corporativo */
      .stButton > button {
        background-color: #C9A96E !important;
        color: #0B1F3A !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: .06em !important;
        padding: 12px 0 !important;
        width: 100% !important;
        box-shadow: 0 2px 10px rgba(201,169,110,.30) !important;
        transition: background .2s, box-shadow .2s !important;
      }
      .stButton > button:hover {
        background-color: #B8935A !important;
        box-shadow: 0 4px 18px rgba(201,169,110,.45) !important;
      }

      /* Input limpio */
      [data-testid="stTextInput"] input {
        background: #F8F6F1 !important;
        border: 1.5px solid #DDD5C0 !important;
        border-radius: 8px !important;
        color: #0B1F3A !important;
        padding: 11px 14px !important;
        font-size: 14px !important;
      }
      [data-testid="stTextInput"] input:focus {
        border-color: #C9A96E !important;
        box-shadow: 0 0 0 3px rgba(201,169,110,.18) !important;
        background: #FFFDF8 !important;
      }
      [data-testid="stTextInput"] input::placeholder { color: #AAA08A !important; }
      [data-testid="stTextInput"] label {
        color: #5A5040 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: .03em !important;
      }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
          background: #FFFFFF;
          border-radius: 16px;
          border: 1px solid #E8E0CE;
          box-shadow: 0 8px 40px rgba(11,31,58,.10);
          padding: 44px 38px 36px;
          text-align: center;
          margin-bottom: 22px;
        ">
          {logo_tag}
          <div style="
            display:inline-block;
            border-top: 1px solid #E8E0CE;
            border-bottom: 1px solid #E8E0CE;
            padding: 5px 16px;
            margin-bottom: 14px;
          ">
            <span style="font-size:9px;color:#C9A96E;text-transform:uppercase;
                         letter-spacing:4px;font-weight:700">
              Nine Fitness Group S.L.
            </span>
          </div>
          <div style="font-size:22px;font-weight:800;color:#0B1F3A;
                      letter-spacing:.03em;margin-bottom:6px">
            DIRECCIÓN DE OBRA
          </div>
          <div style="font-size:10px;color:#AAA08A;text-transform:uppercase;
                      letter-spacing:2.5px">
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
        if st.button("ACCEDER AL PANEL →", use_container_width=True):
            _submit()

        if "_pwd_ok" in st.session_state and not st.session_state["_pwd_ok"]:
            st.error("Contraseña incorrecta.")

        st.markdown("""
        <p style="text-align:center;color:#C8BFA8;font-size:11px;margin-top:20px;
                  text-transform:uppercase;letter-spacing:1.5px">
          Plataforma exclusiva · PMO y Dirección Técnica
        </p>
        """, unsafe_allow_html=True)

    st.stop()
