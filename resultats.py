import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
from scorer_optimeyes import scorer_profil, plot_jauge_multizone, afficher_radar, noter

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

donnees = ligne.iloc[0].to_dict()
resultat = scorer_profil(donnees)
valeur_brute = str(donnees.get("Subjectif_Seul", "")).strip().lower()
subjectif_seul = valeur_brute in ["true", "1", "oui", "yes"]

st.image("optimeyes_logo_black.png", width=400)
code_sujet = donnees.get("Code_Sujet", url_id[:8])
st.title(f"🎫 Passeport Visuo-Cognitif de {code_sujet}")

# Cas 1 : affichage subjectif seul
if subjectif_seul:
    st.markdown("""<div style='background-color: #1e3a5f; padding: 20px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px;'>
        <h4>🎯 Score global de perception (subjectif)</h4>
        <div style='font-size: 2.8em; font-weight: bold; color: #66ccff;'>""" + str(resultat["indice_subjectif"]) + " %</div></div>", unsafe_allow_html=True)

    variables_subjectives = [
        "Decision_Visuelle", "Fatigue_Visuelle", "Sensibilite_Lumineuse",
        "Vision_Peri", "Confort_Visuel"
    ]
    labels_readables = {
        "Decision_Visuelle": "Décision",
        "Fatigue_Visuelle": "Fatigue",
        "Sensibilite_Lumineuse": "Sensibilité",
        "Vision_Peri": "Vision périphérique",
        "Confort_Visuel": "Confort"
    }
    scores_subjectifs_radar = {
        labels_readables[var]: noter(var, donnees.get(var))
        for var in variables_subjectives
        if var in donnees and pd.notnull(donnees[var])
    }

    col_g, col_d = st.columns([6, 4])
    with col_g:
        st.markdown("### 📊 Radar subjectif")
        if scores_subjectifs_radar:
            afficher_radar(scores_subjectifs_radar)
        else:
            st.info("Aucune donnée subjective à afficher dans le radar.")
    with col_d:
        st.markdown("### 📋 Valeurs saisies")
        for var in variables_subjectives:
            val = donnees.get(var)
            if pd.notnull(val):
                label = labels_readables.get(var, var)
                st.markdown(f"""
                    <div style='background-color: #eaeaea; padding: 10px 14px; border-radius: 8px;
                                margin-bottom: 10px; font-weight: bold; color: #333;'>
                        {label} : <span style='float:right;'>📝 {val}</span>
                    </div>
                """, unsafe_allow_html=True)

# Cas 2 : passeport complet
else:
    exec(open("passeport_complet.py").read())
