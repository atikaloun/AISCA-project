# app.py

import streamlit as st
import os
from datetime import datetime
import json
import pandas as pd 
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
    scala_level = st.slider("Niveau en Scala", 1, 5, 2)  
    ml_level = st.slider("Machine Learning (régression, classification, validation)", 1, 5, 3)
    dl_level = st.slider("Deep Learning (PyTorch/TensorFlow, CNN/Transformers)", 1, 5, 2)
    stats_level = st.slider("Statistiques (tests, biais/variance, probabilités)", 1, 5, 3)
    mlops_level = st.slider("MLOps (Docker, déploiement, monitoring)", 1, 5, 2)
    data_eng_level = st.slider("Data Engineering (ETL, Spark, pipelines)", 1, 5, 2)

    st.markdown("---")

    # === 2. Expériences concrètes (texte libre) ===
    st.header("2. Expériences concrètes")

    proj_python = st.text_area(
        "Décrivez une expérience où vous avez conçu ou optimisé des flux de données (pipelines ETL) ou une architecture Big Data. Précisez les technologies utilisées (ex: Spark, Docker, SQL).",
        height=80
    )
    
    ml_pipeline = st.text_area(
        "Détaillez un projet de Machine Learning ou d'IA que vous avez réalisé. Expliquez le choix de vos algorithmes (ex: Transformers, CNN, régressions).",
        height=80
    )
    
    dl_project = st.text_area(
        "Décrivez comment vous avez déjà transformé des données brutes en tableaux de bord (dashboards) ou en analyses statistiques pour répondre à un besoin métier. Avec quels outils ?.",
        height=80
    )
    
    data_pipeline = st.text_area(
        "Expliquez votre approche pour définir une architecture globale de données ou pour piloter la stratégie d'un produit IA.",
        height=80
    )

    st.markdown("---")

    # === 3. Compétences en IA ===
    st.header("3. Compétences en IA")


    

    
    used_genai = st.radio(
        "As-tu utilisé des LLM ou APIs d’IA générative ?",
        ("Oui", "Non")
    )
    genai_tools = ""  # toujours défini

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

    submitted = st.form_submit_button("Analyser mes compétences")

    if submitted:
        responses = {
            "timestamp": datetime.now().isoformat(),
            "likert": {
                "python": python_level,
                "sql": sql_level,
                "scala": scala_level,  # ajouté
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
                "data_pipeline": data_pipeline
            },
            "technical": {
    
                
                "used_genai": used_genai,
               
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

# === Traitement après soumission ===
if st.session_state.submitted:
    try:
        from semantic_engine import (
            charger_referentiel,
            enrichir_saisie,
            calculer_matching,
            generer_livrables,
            charger_profil_numerique,
            calculer_score_numerique
        )

        # Charger les deux référentiels
        df_ref_sem = charger_referentiel("competencies.xlsx")  # ← CSV maintenant
        df_ref_num = charger_profil_numerique("roles_numerical_profile.csv")



        # --- Score sémantique ---
        free_texts = [
            st.session_state.responses["free_text"]["proj_python"],
            st.session_state.responses["free_text"]["ml_pipeline"],
            st.session_state.responses["free_text"]["dl_project"],
            st.session_state.responses["free_text"]["data_pipeline"]
        ]
        free_texts = [txt.strip() for txt in free_texts if txt.strip()]

        if not free_texts:
            st.error("⚠️ Veuillez remplir au moins un champ de texte libre.")
        else:
            enriched = [enrichir_saisie(txt) for txt in free_texts]
            profil_complet = ". ".join(enriched) + "."

            with st.spinner("Analyse sémantique..."):
                rec_sem, _ = calculer_matching(profil_complet, df_ref_sem)
                # Normaliser entre 0 et 1
                min_sem, max_sem = rec_sem.min(), rec_sem.max()
                if max_sem > min_sem:
                    rec_sem_norm = (rec_sem - min_sem) / (max_sem - min_sem)
                else:
                    rec_sem_norm = rec_sem / (max_sem + 1e-8)

            # --- Score numérique (avec langages, frameworks, GenAI) ---
            with st.spinner("Analyse numérique..."):
                rec_num = calculer_score_numerique(
                    st.session_state.responses["likert"],
                    st.session_state.responses["technical"],
                    df_ref_num
                )

            # --- Fusion pondérée : 60% sémantique + 40% numérique ---
            tous_metiers = set(rec_sem_norm.index) | set(rec_num.index)
            score_final = {}
            for metier in tous_metiers:
                s_sem = rec_sem_norm.get(metier, 0.0)
                s_num = rec_num.get(metier, 0.0)
                score_final[metier] = 0.6 * s_sem + 0.4 * s_num

            score_final = pd.Series(score_final).sort_values(ascending=False)
            metier_top = score_final.index[0]
            score_top = score_final.iloc[0]

            st.success(f"✅ **Métier recommandé** : `{metier_top}` (score combiné : `{score_top:.3f}`)")

            # --- Génération des livrables ---
            with st.spinner("Génération de la bio et du plan..."):
                livrables = generer_livrables(profil_complet, metier_top, df_ref_sem)
            st.markdown(livrables)

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.code(str(e), language="python")