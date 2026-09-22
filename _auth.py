import streamlit as st


def require_auth():
    if st.session_state.get("_pwd_ok"):
        return

    def _submit():
        pwd = st.session_state.get("_pwd_input", "")
        st.session_state["_pwd_ok"] = (pwd == st.secrets.get("password_pmo", "brescia19"))

    # ── Ocultar chrome de Streamlit + estilos corporativos Nine Fitness ──────
    st.markdown("""
    <style>
      #MainMenu, footer, header { visibility: hidden; }
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stAppViewContainer"] { background: #111318; }
      [data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }

      /* Botón rojo corporativo Nine Fitness */
      .stButton > button {
        background-color: #D31224 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: .04em !important;
        padding: 10px 0 !important;
        width: 100% !important;
        transition: background .2s, box-shadow .2s !important;
      }
      .stButton > button:hover {
        background-color: #B00E1D !important;
        box-shadow: 0 4px 16px rgba(211,18,36,.45) !important;
      }

      /* Input limpio */
      [data-testid="stTextInput"] input {
        background: #1E2028 !important;
        border: 1px solid #2E3040 !important;
        border-radius: 6px !important;
        color: #fff !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
      }
      [data-testid="stTextInput"] input:focus {
        border-color: #D31224 !important;
        box-shadow: 0 0 0 2px rgba(211,18,36,.25) !important;
      }
      [data-testid="stTextInput"] label { color: #888 !important; font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Layout centrado ───────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<div style='height:72px'></div>", unsafe_allow_html=True)

        # Tarjeta de login
        st.markdown("""
        <div style="
          background:#1A1C24;border-radius:14px;
          border:1px solid #2A2D3A;
          box-shadow:0 12px 40px rgba(0,0,0,.6);
          padding:40px 36px 32px;
          text-align:center;
          margin-bottom:20px
        ">
          <!-- Logo texto en lugar de imagen -->
          <div style="
            display:inline-flex;align-items:center;justify-content:center;
            width:56px;height:56px;border-radius:12px;
            background:#D31224;margin-bottom:18px
          ">
            <span style="font-size:26px;line-height:1">9</span>
          </div>
          <div style="font-size:11px;color:#555;text-transform:uppercase;
                      letter-spacing:3px;margin-bottom:6px">
            Nine Fitness Group S.L.
          </div>
          <div style="font-size:20px;font-weight:800;color:#fff;
                      letter-spacing:.04em;margin-bottom:4px">
            DIRECCIÓN DE OBRA
          </div>
          <div style="font-size:10px;color:#444;text-transform:uppercase;
                      letter-spacing:2.5px">
            Acceso restringido · PMO
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Formulario
        st.text_input(
            "Contraseña de acceso",
            type="password",
            key="_pwd_input",
            on_change=_submit,
            placeholder="Introduce la contraseña corporativa...",
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Acceder al Panel →", use_container_width=True):
            _submit()

        if "_pwd_ok" in st.session_state and not st.session_state["_pwd_ok"]:
            st.error("Contraseña incorrecta. Contacta con Darío López.")

        st.markdown("""
        <p style="text-align:center;color:#333;font-size:11px;margin-top:20px">
          Plataforma exclusiva para el equipo de PMO y Dirección Técnica.
        </p>
        """, unsafe_allow_html=True)

    st.stop()
