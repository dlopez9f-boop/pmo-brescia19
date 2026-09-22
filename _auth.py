import streamlit as st


def require_auth():
    if st.session_state.get("_pwd_ok"):
        return

    def _submit():
        pwd = st.session_state.get("_pwd_input", "")
        st.session_state["_pwd_ok"] = (pwd == st.secrets.get("password_pmo", "brescia19"))

    st.markdown("""<style>
    [data-testid="stSidebar"]{display:none}
    [data-testid="stAppViewContainer"]{background:#0e1117}
    </style>""", unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown("""
        <div style="text-align:center;padding:60px 0 32px">
          <div style="font-size:44px">🏋️</div>
          <div style="font-size:20px;font-weight:900;color:#fff;margin:8px 0">PMO · Nine Fitness Group</div>
          <div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-top:4px">
            Acceso restringido
          </div>
        </div>""", unsafe_allow_html=True)
        st.text_input("Contraseña", type="password", key="_pwd_input",
                      on_change=_submit, placeholder="Introduce la contraseña...")
        if st.button("Acceder →", use_container_width=True, type="primary"):
            _submit()
        if "_pwd_ok" in st.session_state and not st.session_state["_pwd_ok"]:
            st.error("Contraseña incorrecta.")

    st.stop()
