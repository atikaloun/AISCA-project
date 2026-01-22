# semantic_engine.py

import os
import json
import time
import pandas as pd
import torch
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity

# === Configuration API Gemini ===
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBOKj_WIFJaeijtN4vcx0qG775a1vO_lrY")
genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 500,
}
GENAI_MODEL = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)

CACHE_FILE = "gemini_cache.json"
SBERT_MODEL = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# === Gestion du cache GenAI ===
def charger_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

_cache = charger_cache()

def appeler_gemini_smart(prompt: str) -> str:
    if prompt in _cache:
        return _cache[prompt]
    try:
        response = GENAI_MODEL.generate_content(prompt)
        _cache[prompt] = response.text
        sauvegarder_cache(_cache)
        return response.text
    except Exception as e:
        if "429" in str(e):
            time.sleep(30)
            return appeler_gemini_smart(prompt)
        return f"Erreur GenAI : {e}"

# === Chargement du référentiel ===
def charger_referentiel(filepath: str = "competencies.xlsx") -> pd.DataFrame:
    df = pd.read_excel(filepath)
    df = df.dropna(subset=['Métier', 'Compétences'])
    df['embedding'] = df['Compétences'].apply(lambda x: SBERT_MODEL.encode(str(x), convert_to_tensor=True))
    return df

# === Enrichissement conditionnel ===
def enrichir_saisie(texte: str, label: str = "") -> str:
    mots = str(texte).split()
    if 0 < len(mots) < 5:
        prompt = f"Enrichis techniquement cette compétence pour un CV : {texte}. Sois très concis."
        return appeler_gemini_smart(prompt)
    return texte

# === Matching sémantique ===
def calculer_matching(profil_complet: str, df_ref: pd.DataFrame):
    user_emb = SBERT_MODEL.encode(profil_complet, convert_to_tensor=True)
    ref_embs = torch.stack(df_ref['embedding'].tolist())
    scores = util.cos_sim(user_emb, ref_embs)[0]
    df_ref['score_sim'] = scores.tolist()
    recommandations = df_ref.groupby('Métier')['score_sim'].mean().sort_values(ascending=False)
    return recommandations, df_ref

# === Génération finale ===
def generer_livrables(profil: str, metier: str, df_ref: pd.DataFrame) -> str:
    mask = df_ref['Métier'] == metier
    lacunes = df_ref[mask].sort_values(by='score_sim').head(3)['Compétences'].tolist()
    prompt = f"""
Tu es un expert RH. Voici le profil utilisateur : {profil}
Métier cible : {metier}
Lacunes détectées : {', '.join(lacunes)}

LIVRABLES :
1. Bio Pro (3 lignes max).
2. Roadmap de progression (3 étapes clés).
Réponds en Markdown.
"""
    return appeler_gemini_smart(prompt)

# === NOUVEAU : Profil numérique + compétences techniques ===

def charger_profil_numerique(filepath: str = "roles_numerical_profile.csv") -> pd.DataFrame:
    return pd.read_csv(filepath)

def reponses_techniques_vers_vecteur(reponses_techniques: dict) -> dict:
    langages = set(reponses_techniques.get("languages", []))
    frameworks = set(reponses_techniques.get("frameworks", []))
    used_genai = reponses_techniques.get("used_genai", "Non") == "Oui"

    return {
        "lang_python": 1 if "Python" in langages else 0,
        "lang_sql": 1 if "SQL" in langages else 0,
        "lang_scala": 1 if "Scala" in langages else 0,
        "framework_pandas": 1 if "Pandas" in frameworks else 0,
        "framework_spark": 1 if "Spark" in frameworks else 0,
        "framework_pytorch": 1 if ("PyTorch" in frameworks or "TensorFlow" in frameworks) else 0,
        "framework_docker": 1 if "Docker" in frameworks else 0,
        "genai": 1 if used_genai else 0,
    }

def calculer_score_numerique(reponses_likert: dict, reponses_techniques: dict, df_profil: pd.DataFrame) -> pd.Series:
    """
    Calcule le score numérique basé uniquement sur :
    - Les sliders Likert (8 axes)
    - Le booléen GenAI
    """
    # Colonnes Likert (doivent exister dans le CSV)
    colonnes_likert = ["python", "sql", "scala", "ml", "dl", "stats", "mlops", "data_engineering"]
    
    # Vecteur utilisateur : normaliser Likert (1-5 → 0-1) + GenAI (0/1)
    user_likert = np.array([reponses_likert.get(col, 3) for col in colonnes_likert]) / 5.0
    used_genai = 1 if reponses_techniques.get("used_genai", "Non") == "Oui" else 0
    user_vec = np.concatenate([user_likert, [used_genai]]).reshape(1, -1)

    # Colonnes du profil (doivent correspondre exactement au CSV)
    colonnes_profil = colonnes_likert + ["genai"]
    
    # Vérification de sécurité
    if not all(col in df_profil.columns for col in colonnes_profil):
        missing = [col for col in colonnes_profil if col not in df_profil.columns]
        raise ValueError(f"Colonnes manquantes dans le CSV : {missing}")

    # Matrice des profils idéaux
    profils_mat = df_profil[colonnes_profil].values.astype(float)
    profils_mat[:, :-1] /= 5.0  # Normaliser les colonnes Likert (sauf 'genai')

    # Similarité cosinus
    from sklearn.metrics.pairwise import cosine_similarity
    sim_scores = cosine_similarity(user_vec, profils_mat)[0]
    return pd.Series(sim_scores, index=df_profil["Métier"])