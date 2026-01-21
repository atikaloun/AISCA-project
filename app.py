# app.py — Interface complète AISCA

import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="AISCA - Analyse Sémantique des Compétences",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 AISCA")
st.subheader("Analyse Sémantique pour la Cartographie des Compétences et la Recommandation de Métiers")
st.markdown("---")

if "submitted" not in st.session_state:
    st.session_state.submitted = False

with st.form("questionnaire"):
    st.header("1. Auto-évaluation (échelle de 1 à 5)")

    python_level = st.slider("Niveau en Python", 1, 5, 3)
    ml_level = st.slider("Expérience en Machine Learning", 1, 5, 3)
    sql_level = st.slider("Maîtrise des bases de données (SQL/NoSQL)", 1, 5, 3)
    nlp_level = st.slider("Expérience en traitement du langage naturel (NLP)", 1, 5, 2)
    mlops_level = st.slider("Capacité à déployer des modèles (MLOps, API, Docker...)", 1, 5, 2)

    st.markdown("---")
    st.header("2. Expériences concrètes (réponses libres)")

    proj_python = st.text_area(
        "Décrivez un projet récent où vous avez utilisé Python pour analyser ou transformer des données.",
        height=100
    )
    
    proj_ml = st.text_area(
        "Racontez une expérience où vous avez entraîné ou évalué un modèle de machine learning.",
        height=100
    )
    
    proj_nlp = st.text_area(
        "Avez-vous déjà travaillé sur un projet impliquant du traitement du langage (ex. : classification de texte, chatbot) ? Décrivez-le.",
        height=100
    )
    
    proj_auto = st.text_area(
        "Décrivez une situation où vous avez automatisé une tâche répétitive (extraction, reporting, scripts).",
        height=100
    )
    
    tools_used = st.text_area(
        "Quels outils ou frameworks utilisez-vous régulièrement ? (ex. : Pandas, Spark, Power BI, Git...)",
        height=80
    )

    st.markdown("---")
    st.header("3. Compétences techniques")

    languages = st.multiselect(
        "Langages de programmation maîtrisés",
        ["Python", "SQL", "R", "JavaScript", "Scala", "Autre"],
        default=["Python"]
    )
    
    bi_tools = st.multiselect(
        "Outils de visualisation / BI utilisés",
        ["Power BI", "Tableau", "Matplotlib / Seaborn", "Plotly / Dash", "Aucun"]
    )
    
    used_genai = st.radio(
        "Avez-vous déjà utilisé des modèles de langage (LLM) ou APIs d’IA générative ?",
        ("Oui", "Non")
    )
    if used_genai == "Oui":
        genai_tools = st.text_input("Lesquels ? (ex. : Gemini, OpenAI, Ollama...)")
    else:
        genai_tools = ""

    deployment_env = st.multiselect(
        "Environnements de déploiement utilisés",
        ["Local", "Cloud (AWS/GCP/Azure)", "Docker", "Notebooks (Colab/Jupyter)", "Je ne déploie pas"]
    )

    st.markdown("---")
    st.header("4. Orientation professionnelle")

    target_role = st.selectbox(
        "Quel type de rôle vous intéresse le plus ?",
        [
            "Data Analyst",
            "Data Scientist",
            "Machine Learning Engineer",
            "Data Engineer",
            "NLP Specialist",
            "Autre"
        ]
    )
    if target_role == "Autre":
        other_role = st.text_input("Précisez :")
    else:
        other_role = ""

    # Bouton de soumission
    submitted = st.form_submit_button("Analyser mes compétences")

    if submitted:
        # Collecte des réponses
        responses = {
            "timestamp": datetime.now().isoformat(),
            "likert": {
                "python": python_level,
                "ml": ml_level,
                "sql": sql_level,
                "nlp": nlp_level,
                "mlops": mlops_level
            },
            "free_text": {
                "proj_python": proj_python,
                "proj_ml": proj_ml,
                "proj_nlp": proj_nlp,
                "proj_auto": proj_auto,
                "tools_used": tools_used
            },
            "technical": {
                "languages": languages,
                "bi_tools": bi_tools,
                "used_genai": used_genai,
                "genai_tools": genai_tools,
                "deployment_env": deployment_env
            },
            "career": {
                "target_role": other_role if target_role == "Autre" else target_role
            }
        }

        # Sauvegarde locale
        os.makedirs("data", exist_ok=True)
        with open("data/latest_response.json", "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)

        st.session_state.responses = responses
        st.session_state.submitted = True

# Affichage après soumission
if st.session_state.submitted:
    st.success("✅ Vos réponses ont été enregistrées !")
    with st.expander("Voir vos réponses brutes"):
        st.json(st.session_state.responses)