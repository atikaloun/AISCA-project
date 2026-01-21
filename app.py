# app.py — Interface AISCA enrichie (léger + métier)

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
    # === 1. Auto-évaluation (Likert) ===
    st.header("1. Auto-évaluation (échelle de 1 à 5)")

    python_level = st.slider("Niveau en Python", 1, 5, 3)
    sql_level = st.slider("Maîtrise de SQL (CTE, window functions)", 1, 5, 3)
    ml_level = st.slider("Machine Learning (régression, classification, validation)", 1, 5, 3)
    dl_level = st.slider("Deep Learning (PyTorch/TensorFlow, CNN/Transformers)", 1, 5, 2)
    stats_level = st.slider("Statistiques (tests, biais/variance, probabilités)", 1, 5, 3)
    mlops_level = st.slider("MLOps (Docker, déploiement, monitoring)", 1, 5, 2)
    data_eng_level = st.slider("Data Engineering (ETL, Spark, pipelines)", 1, 5, 2)

    st.markdown("---")

    # === 2. Expériences concrètes (texte libre) ===
    st.header("2. Expériences concrètes")

    proj_python = st.text_area(
        "Décris un projet Python structuré (modules, classes, tests).",
        height=80
    )
    
    ml_pipeline = st.text_area(
        "Explique ton pipeline ML de bout en bout (préparation → évaluation).",
        height=80
    )
    
    dl_project = st.text_area(
        "As-tu entraîné un modèle profond (CNN, Transformer) ? Décris-le.",
        height=80
    )
    
    data_pipeline = st.text_area(
        "As-tu construit un pipeline de données (ETL, streaming) ? Raconte.",
        height=80
    )
    
    deploy_ml = st.text_area(
        "Comment as-tu déployé un modèle en production ? (Docker, API, etc.)",
        height=80
    )

    st.markdown("---")

    # === 3. Compétences techniques ===
    st.header("3. Compétences techniques")

    languages = st.multiselect(
        "Langages maîtrisés",
        ["Python", "SQL", "R", "Scala", "Java", "JavaScript", "Autre"],
        default=["Python", "SQL"]
    )
    
    frameworks = st.multiselect(
        "Frameworks / bibliothèques",
        ["Pandas", "Scikit-learn", "TensorFlow", "PyTorch", "Spark", "OpenCV", "Hugging Face", "Docker", "Airflow", "Kafka"]
    )
    
    used_genai = st.radio(
        "As-tu utilisé des LLM ou APIs d’IA générative ?",
        ("Oui", "Non")
    )
    if used_genai == "Oui":
        genai_tools = st.text_input("Lesquels ? (ex. : Gemini, OpenAI, Ollama)")
    else:
        genai_tools = ""

    st.markdown("---")

    # === 4. Orientation professionnelle ===
    st.header("4. Rôles ciblés")

    target_roles = st.multiselect(
        "Quels rôles t’intéressent ?",
        [
            "Data Analyst", "Data Scientist", "Machine Learning Engineer", "AI Engineer",
            "NLP Engineer", "Computer Vision Engineer", "Data Engineer", "BigData Engineer",
            "Analytics Engineer", "BI Developer", "Statisticien", "Quantitative Analyst",
            "MLOps Engineer", "Data Architect", "AI Product Manager"
        ],
        default=["Data Scientist"]
    )

    # === Soumission ===
    submitted = st.form_submit_button("Analyser mes compétences")

    if submitted:
        responses = {
            "timestamp": datetime.now().isoformat(),
            "likert": {
                "python": python_level,
                "sql": sql_level,
                "ml": ml_level,
                "dl": dl_level,
                "stats": stats_level,
                "mlops": mlops_level,
                "data_engineering": data_eng_level
            },
            "free_text": {
                "proj_python": proj_python,
                "ml_pipeline": ml_pipeline,
                "dl_project": dl_project,
                "data_pipeline": data_pipeline,
                "deploy_ml": deploy_ml
            },
            "technical": {
                "languages": languages,
                "frameworks": frameworks,
                "used_genai": used_genai,
                "genai_tools": genai_tools
            },
            "career": {
                "target_roles": target_roles
            }
        }

        os.makedirs("data", exist_ok=True)
        with open("data/latest_response.json", "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)

        st.session_state.responses = responses
        st.session_state.submitted = True

# === Affichage après soumission ===
if st.session_state.submitted:
    st.success("✅ Vos réponses ont été enregistrées !")
    with st.expander("Voir vos réponses brutes"):
        st.json(st.session_state.responses)