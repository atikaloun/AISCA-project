
import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="AISCA", page_icon="🧠", layout="centered")
st.title("🧠 AISCA")
st.subheader("Analyse Sémantique des Compétences")
st.markdown("---")

if "submitted" not in st.session_state:
    st.session_state.submitted = False

with st.form("questionnaire"):
    python_level = st.slider("Niveau en Python", 1, 5, 3)
    proj_python = st.text_area("Décrivez un projet Python récent", height=100)
    submitted = st.form_submit_button("Analyser")

    if submitted:
        responses = {"python": python_level, "projet": proj_python}
        os.makedirs("data", exist_ok=True)
        with open("data/response.json", "w") as f:
            json.dump(responses, f)
        st.session_state.responses = responses
        st.session_state.submitted = True

if st.session_state.submitted:
    st.success("✅ Réponses enregistrées !")
    st.json(st.session_state.responses)

# ÉTAPE 3 : Lancer Streamlit + Ngrok
import subprocess
import threading
from pyngrok import ngrok

# Lancer Streamlit en arrière-plan
def run_streamlit():
    subprocess.Popen([
        "streamlit", "run", "app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ])

threading.Thread(target=run_streamlit, daemon=True).start()

# Exposer via ngrok
public_url = ngrok.connect(8501)
print(f"\n🔗 Votre app Streamlit est accessible ici : {public_url}\n")
print("⚠️ Valable ~2 heures. Ne fermez pas ce notebook !")