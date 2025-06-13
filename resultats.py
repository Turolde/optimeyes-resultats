import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
from scorer_optimeyes import scorer_profil, plot_jauge_multizone, afficher_radar, noter
from passeport_complet import afficher_passeport_complet

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
valeur_brute = donnees.get("Subjectif_Seul", None)

subjectif_seul = False
if isinstance(valeur_brute, (int, float)):
    subjectif_seul = valeur_brute == 1
elif isinstance(valeur_brute, str):
    subjectif_seul = valeur_brute.strip().lower() in ["true", "1", "oui", "yes", "vrai"]


code_sujet = donnees.get("Code_Sujet", url_id[:8])

# Cas 1 : affichage subjectif seul
if subjectif_seul:
    st.image("optimeyes_logo_black.png", width=400)
    st.title(f"🎫 Passeport Visuo-Cognitif de {code_sujet}")
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
        st.markdown("### 📊 Radar d\'autodiagnostique")
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
    afficher_passeport_complet(donnees, resultat)

st.markdown("""
    <hr style="margin-top: 2em; margin-bottom: 1em; border: none; height: 2px;
    background: linear-gradient(to right, #ff6f91, #ff9671, #ffc75f, #d65db1);">

    <div style="background-color: #357273; padding: 16px; border-radius: 12px;
    text-align: center; font-size: 0.9em; color: #802f4e;">

    👩‍⚕️ <strong>Brigitte EKPE LORDONNOIS</strong> · Fondatrice<br>
    💡 Chez <strong>Optimeyes</strong>, nous proposons des solutions innovantes pour optimiser votre vision et vos capacités cognitives grâce à des bilans spécialisés, des entraînements ciblés et des technologies de pointe.<br>
    🔗 <a href="https://optimeyes.fr" target="_blank"
    style="color: #d65db1; font-weight: bold;">Visitez optimeyes.fr</a>
    </div>
    """, unsafe_allow_html=True)
