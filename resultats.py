import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
from scorer_optimeyes import scorer_profil, plot_jauge_multizone, afficher_radar

FICHIER_ID_DRIVE = "162CoThxy9GcuJIWLB_jcpGxXBWsUz7UD"

# Connexion Google Drive
def connect_drive():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["google"],
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

@st.cache_data(ttl=60)
def telecharger_donnees():
    service = connect_drive()
    request = service.files().get_media(fileId=FICHIER_ID_DRIVE)
    buffer = BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    buffer.seek(0)
    return pd.read_excel(buffer)

# --- Charger ligne à partir de l’URL ---
def charger_profil(url_id):
    df = telecharger_donnees()
    ligne = df[df["Url_ID"] == url_id]
    return ligne

# --- UI ---
st.set_page_config(page_title="Passeport Visuel Optimeyes", layout="centered")

url_id = st.query_params.get("id")
if not url_id:
    st.error("❌ Aucun identifiant de profil fourni.")
    st.stop()

ligne = charger_profil(url_id)
if ligne.empty:
    st.error("❌ Profil introuvable.")
    st.stop()
    
st.image("optimeyes_logo_black.png", width=400)
donnees = ligne.iloc[0].to_dict()
code_sujet = donnees.get("Code_Sujet", url_id[:8])
st.title(f"🎫 Passeport Visuo-Cognitif de {code_sujet}")
resultat = scorer_profil(donnees)

# --- Scores principaux ---
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        f"""<div style='background-color: #1e3a5f; padding: 20px; border-radius: 12px; text-align: center; color: white;'>
            <h4>🎯 Score de perception subjective</h4>
            <div style='font-size: 2.5em; font-weight: bold; color: #66ccff;'>{resultat['indice_subjectif']} %</div>
        </div>""",
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""<div style='background-color: #442b00; padding: 20px; border-radius: 12px; text-align: center; color: white;'>
            <h4>🧪 Score de performance clinique</h4>
            <div style='font-size: 2.5em; font-weight: bold; color: #ffa64d;'>{resultat['indice_performance']} %</div>
        </div>""",
        unsafe_allow_html=True
    )

# --- Cohérence ---
couleur_coherence = {
    "Très bonne": "#66ff99",
    "Moyenne": "#ffd966",
    "Faible": "#ff6666"
}.get(resultat["coherence"], "#cccccc")

st.markdown(
    f"""<div style='margin-top: 20px; padding: 15px; border-radius: 10px; background-color: #2a2a2a; color: white;'>
        <p>🔍 <strong>Cohérence entre perception et performance :</strong>
        <span style='color: {couleur_coherence}; font-weight: bold;'> {resultat["coherence"]}</span></p>
    </div>""",
    unsafe_allow_html=True
)

if resultat["alerte_discordance"]:
    st.markdown(
        """<div style='margin-top: 10px; padding: 12px; border-radius: 8px; background-color: #5c0000; color: #ffe6e6;'>
        ⚠️ Attention : écart élevé entre perception et performance.
        </div>""",
        unsafe_allow_html=True
    )

# --- Profil dominant ---
st.subheader("🎯 Résultat du Profiling")
col_g, col_d = st.columns([6, 4])
with col_g:
    st.markdown("### 🔄 Score par profil")
    afficher_radar(resultat["scores"])
with col_d:
    st.markdown("### 📋 Détail des scores")
    for profil, score in resultat["scores"].items():
        couleur = {
            "Athlète": "#90CBC1", "Pilote": "#A5B4DC",
            "E-sportif": "#D8A5B8", "Performer cognitif": "#B6A49C"
        }.get(profil, "#ccc")
        emoji = {
            "Athlète": "🏃‍♂️", "Pilote": "🏎️",
            "E-sportif": "🎮", "Performer cognitif": "🧠"
        }.get(profil, "👁️")
        st.markdown(
            f"""<div style='background-color:{couleur};padding:8px 12px;margin-bottom:8px;
            border-radius:8px;font-weight:600;color:#1f1f1f;'>
            {emoji} {profil} : <span style='float:right;'>{score} %</span>
            </div>""", unsafe_allow_html=True
        )

# --- Radar analytique ---
st.markdown("---")
st.subheader("🔬 Analyse des 5 axes cognitifs et visuels")
col_g, col_d = st.columns([6, 4])
with col_g:
    afficher_radar(resultat["radar_analytique"])
with col_d:
    st.markdown("### 🧠 Scores par axe")
    for axe, score in resultat["radar_analytique"].items():
        st.markdown(
            f"""<div style='background-color:#e0e0e0;padding:8px 12px;margin-bottom:8px;
            border-radius:8px;font-weight:600;color:#1f1f1f;'>
            {axe} : <span style='float:right;'>{score} %</span>
            </div>""", unsafe_allow_html=True
        )

# --- Jauges de performance ---
st.markdown("---")
st.subheader("📏 Jauges de performance")

mapping_indicateurs = {
    "vitesse_horizontale": "Vitesse_Horizontale",
    "vitesse_verticale": "Vitesse_Verticale",
    "go": "GO",
    "nogo": "NOGO",
    "vision_faible_contraste": "Vision_Faible_Contraste",
    "stereopsie": "Stereopsie"
}

df_config = pd.read_csv("Vivatech_Optimeyes.csv", sep=";", encoding="latin1")

# Préparer les seuils
seuils_reference = {
    row["Item"].strip(): {
        "min": float(row["Min"]),
        "max": float(row["Max"]),
        "borne1": row["Borne1"],
        "borne2": row["Borne2"],
        "borne3": row["Borne3"],
        "borne4": row["Borne4"]
    }
    for _, row in df_config.iterrows()
    if row["Item"].strip() in mapping_indicateurs.values()
}

col1, col2 = st.columns(2)
compteur = 0

for cle_logique, indicateur in mapping_indicateurs.items():
    if indicateur == "Stereopsie" and not donnees.get("Stereopsie_activee", True):
        continue

    valeur = donnees.get(indicateur)
    if pd.isnull(valeur):
        continue

    seuils = seuils_reference.get(indicateur, {"min": 0, "max": 100})
    bornes = [seuils.get(f"borne{i}") for i in range(1, 5)]

# Couleurs adaptées
    great = "#66ccaa"     # vert doux
    good = "#b5d991"      # vert-jaune doux
    average = "#ffd580"   # beige doré
    bad = "#ff9c8a"       # corail
    worst = "#d66a6a"     # rouge doux

    if indicateur == "Stereopsie":
        couleurs = [bad, great, average, bad]
    elif indicateur == "Vitesse_Horizontale":
        couleurs = [bad, average, great, average, bad]
    elif indicateur == "Vitesse_Verticale":
        couleurs = [bad, average, great]
    elif indicateur == "GO":
        couleurs = [great, average, bad]
    elif indicateur == "NOGO":
        couleurs = [great, bad]
    elif indicateur == "Vision_Faible_Contraste":
        if valeur == 0:
            badge = "🟢 Bonne vision faible contraste"
            message = "Aucune difficulté détectée en faible contraste."
            couleur_fond = "#1e5631"
        else:
            badge = "🔴 Échec ou difficulté"
            message = "Difficulté à détecter les faibles contrastes."
            couleur_fond = "#8b1e3f"
            
        col = col1 if compteur % 2 == 0 else col2
        with col:
            st.markdown(
                f"""
                <div style='background-color: {couleur_fond}; padding: 16px; border-radius: 10px; text-align: center; color: white;'>
                    <div style='font-size: 1.1em; font-weight: bold;'>{badge}</div>
                    <p style='margin-top: 6px; font-size: 0.9em;'>{message}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        compteur += 1
        continue
    else:
        couleurs = None

    fig = plot_jauge_multizone(
        nom=indicateur,
        valeur=valeur,
        min_val=seuils["min"],
        max_val=seuils["max"],
        bornes_abs=bornes,
        custom_colors=couleurs    
    )
    col = col1 if compteur % 2 == 0 else col2
    with col:
        st.pyplot(fig)

        # VRAI commentaire associé
        commentaire = resultat["commentaires"].get(indicateur, "")
        if commentaire and isinstance(commentaire, str) and not commentaire.lower().startswith("score"):
            st.markdown(f"<span style='font-size: 0.9em; color: grey;'>{commentaire}</span>", unsafe_allow_html=True)

    compteur += 1

# --- Données saisies ---
st.markdown("---")
