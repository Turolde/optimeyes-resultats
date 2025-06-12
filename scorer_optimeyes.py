# scorer_optimeyes.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

commentaires_indicateurs = {
    "Decision_Visuelle": {
        3: "Décision très rapide, excellente réactivité.",
        2: "Décision de vitesse moyenne, correcte dans l’ensemble.",
        1: "Décision lente, réactivité diminuée.",
        0: "Donnée absente ou non interprétable sur la capacité décisionnelle."
    },
    "Fatigue_Visuelle": {
        3: "Très faible fatigue visuelle ressentie.",
        2: "Fatigue visuelle modérée.",
        1: "Fatigue visuelle importante signalée.",
        0: "Fatigue visuelle non renseignée ou incohérente."
    },
    "Sensibilite_Lumineuse": {
        3: "Aucune sensibilité à la lumière signalée.",
        2: "Sensibilité occasionnelle à la lumière.",
        1: "Sensibilité marquée à la lumière.",
        0: "Aucune donnée disponible sur la sensibilité lumineuse."
    },
    "Vision_Peri": {
        3: "Vision périphérique jugée bonne.",
        2: "Vision périphérique moyenne.",
        1: "Vision périphérique faible.",
        0: "Évaluation périphérique non renseignée ou invalide."
    },
    "Confort_Visuel": {
        3: "Très bon confort visuel perçu.",
        2: "Confort visuel acceptable.",
        1: "Confort visuel faible ou inconfort.",
        0: "Absence de réponse sur le confort visuel."
    },
    "Vitesse_Horizontale": {
        3: "Excellente vitesse visuelle horizontale.",
        2: "Vitesse correcte avec marge de progression.",
        1: "Vitesse visuelle lente ou perturbée.",
        0: "Mesure horizontale non disponible ou inexploitée."
    },
    "Vitesse_Verticale": {
        3: "Très bonne vitesse visuelle verticale.",
        2: "Vitesse verticale modérée.",
        1: "Réduction marquée de la vitesse verticale.",
        0: "Vitesse verticale non mesurée ou invalide."
    },
    "Vision_Faible_Contraste": {
        3: "Aucune difficulté détectée en faible contraste.",
        2: "Légère difficulté avec les contrastes faibles.",
        1: "Difficulté importante à détecter les faibles contrastes.",
        0: "Aucune donnée exploitable sur la vision en faible contraste."
    },
    "Stereopsie": {
        3: "Excellente perception 3D (stéréopsie).",
        2: "Perception 3D correcte.",
        1: "Perception 3D altérée ou lente.",
        0: "Données aberrantes ou interprétation non fiable."
    },
    "GO_NOGO": {
        3: "Très bon contrôle décisionnel (go/no-go).",
        2: "Contrôle correct avec vigilance.",
        1: "Décisions impulsives ou lenteur observée.",
        0: "Go/No-Go non calculable (valeurs manquantes)."
    },
    "GO": {
        3: "Temps de réaction très rapide.",
        2: "Temps de réaction correct, mais améliorable.",
        1: "Temps de réaction lent ou erratique.",
        0: "Temps de réaction non mesuré."
    },
    "NOGO": {
        3: "Très bon contrôle inhibiteur (très peu d'erreurs).",
        2: "Contrôle correct avec quelques erreurs.",
        1: "Impulsivité marquée ou erreurs fréquentes.",
        0: "Donnée inhibitrice absente ou invalide."
    }
}


def noter(variable, valeur):
    if variable == "Decision_Visuelle":
        return 3 if valeur == "Rapide" else 2 if valeur == "Moyenne" else 1 if valeur == "Lente" else 0
    if variable == "Sensibilite_Lumineuse":
        return 3 if valeur == "Non" else 2 if valeur == "Parfois" else 1 if valeur == "Oui" else 0
    if variable == "Vision_Peri":
        return 3 if valeur == "Bon" else 2 if valeur == "Moyen" else 1 if valeur == "Faible" else 0
    if variable == "Vitesse_Horizontale" and isinstance(valeur, (int, float)):
        return 3 if 501 <= valeur <= 700 else 2 if (451 <= valeur <= 500 or 701 <= valeur <= 850) else 1 if valeur <= 450 or valeur > 850 else 0
    if variable == "Vitesse_Verticale" and isinstance(valeur, (int, float)):
        return 1 if valeur <= 300 else 2 if valeur <= 399 else 3 if valeur <= 9999 else 0
    if variable == "Vision_Faible_Contraste" and isinstance(valeur, (int, float)):
        return 3 if valeur == 0 else 1 if valeur > 0 else 0
    if variable == "Fatigue_Visuelle" and isinstance(valeur, (int, float)):
        return 1 if 8 <= valeur <= 10 else 2 if 4 <= valeur <= 7 else 3 if 1 <= valeur <= 3 else 0
    if variable == "Confort_Visuel" and isinstance(valeur, (int, float)):
        return 3 if 8 <= valeur <= 10 else 2 if 4 <= valeur <= 7 else 1 if 1 <= valeur <= 3 else 0
    if variable == "GO" and isinstance(valeur, (int, float)):
        return 3 if valeur <= 500 else 2 if valeur <= 700 else 1
    if variable == "NOGO" and isinstance(valeur, (int, float)):
        return 3 if valeur <= 5 else 2 if valeur <= 15 else 1
    if variable == "Stereopsie" and isinstance(valeur, (int, float)):
        return 3 if 30 <= valeur <= 60 else 2 if 61 <= valeur <= 120 else 1 if valeur >= 121 else 0
    return 0

def noter_go_nogo(go, nogo):
    if go <= 500 and nogo <= 10:
        return 3
    elif go <= 500 and nogo > 10:
        return 2
    elif go > 500 and nogo <= 10:
        return 2
    else:
        return 1

def scorer_profil(d):
    go = d.get("GO")
    nogo = d.get("NOGO")
    go_nogo_score = noter_go_nogo(go, nogo) if go is not None and nogo is not None else 0
    stereopsie_activee = d.get("Stereopsie_activee", True)

    indicateurs_subjectifs = [
        "Decision_Visuelle", "Fatigue_Visuelle",
        "Sensibilite_Lumineuse", "Vision_Peri", "Confort_Visuel"
    ]
    score_subjectif_total = sum([noter(var, d.get(var, 0)) for var in indicateurs_subjectifs])
    indice_subjectif = round((score_subjectif_total / (3 * len(indicateurs_subjectifs))) * 100, 1)

    indicateurs_perf = ["Vitesse_Horizontale", "Vitesse_Verticale", "Vision_Faible_Contraste"]
    if stereopsie_activee:
        indicateurs_perf.append("Stereopsie")

    score_perf_total = sum([noter(var, d.get(var, 0)) for var in indicateurs_perf]) + (2 * go_nogo_score)
    total_points_theoriques = (len(indicateurs_perf) + 2) * 3
    indice_performance = round((score_perf_total / total_points_theoriques) * 100, 1)

    poids_subjectif = 0.4
    amplification = min(abs(indice_subjectif - indice_performance) / 100, 0.6)
    poids_performance = 1.0 - poids_subjectif + amplification
    poids_total = poids_subjectif + poids_performance
    poids_subjectif /= poids_total
    poids_performance /= poids_total
    score_global = round(poids_subjectif * indice_subjectif + poids_performance * indice_performance, 1)

    poids = {
        "Athlète": {"GO_NOGO": 2, "Vitesse_Horizontale": 2, "Vitesse_Verticale": 2, "Vision_Faible_Contraste": 1, "Stereopsie": 3},
        "Pilote": {"GO_NOGO": 2, "Vitesse_Horizontale": 1, "Vitesse_Verticale": 1, "Vision_Faible_Contraste": 1, "Stereopsie": 2},
        "E-sportif": {"GO_NOGO": 2, "Vitesse_Horizontale": 4, "Vitesse_Verticale": 4, "Vision_Faible_Contraste": 1, "Stereopsie": 2},
        "Performer cognitif": {"GO_NOGO": 2, "Vitesse_Horizontale": 1, "Vitesse_Verticale": 1, "Vision_Faible_Contraste": 4, "Stereopsie": 1}
    }

    scores = {}
    for profil, variables in poids.items():
        score = 0
        total_poids = 0
        for var, p in variables.items():
            if var == "Stereopsie" and not stereopsie_activee:
                continue
            valeur = go_nogo_score if var == "GO_NOGO" else d.get(var, 0)
            score += noter(var, valeur) * p
            total_poids += p
        scores[profil] = round((score / (3 * total_poids)) * 100, 1) if total_poids else 0

    profil_dominant = max(scores, key=scores.get)
    score_profil_dominant = scores[profil_dominant]

    ecart = abs(indice_subjectif - indice_performance)
    coherence = "Très bonne" if ecart < 10 else "Moyenne" if ecart < 25 else "Faible"
    alerte_discordance = ecart >= 25

    radar_analytique = {
        "Vitesse visuelle": round((noter("Vitesse_Horizontale", d.get("Vitesse_Horizontale", 0)) + noter("Vitesse_Verticale", d.get("Vitesse_Verticale", 0))) / 2 * 33.33, 1),
        "Résolution spatiale": round((noter("Vision_Faible_Contraste", d.get("Vision_Faible_Contraste", 0)) + (noter("Stereopsie", d.get("Stereopsie", 0)) if stereopsie_activee else 0)) / (2 if stereopsie_activee else 1) * 33.33, 1),
        "Attention périphérique": round(noter("Vision_Peri", d.get("Vision_Peri", 0)) * 33.33, 1),
        "Engagement décisionnel": round((go_nogo_score + noter("Decision_Visuelle", d.get("Decision_Visuelle", 0))) / 2 * 33.33, 1),
        "Surcharge visuelle perçue": round((noter("Fatigue_Visuelle", d.get("Fatigue_Visuelle", 0)) + noter("Sensibilite_Lumineuse", d.get("Sensibilite_Lumineuse", 0))) / 2 * 33.33, 1)
    }

    commentaires = {}
    for var in indicateurs_subjectifs + indicateurs_perf:
        if var == "Stereopsie" and not stereopsie_activee:
            continue
        score = noter(var, d.get(var, 0))
        commentaires[var] = f"Score {score}/3"
    commentaires["GO"] = f"Score {noter('GO', go)}/3"
    commentaires["NOGO"] = f"Score {noter('NOGO', nogo)}/3"
    commentaires["GO_NOGO"] = f"Score {go_nogo_score}/3"

    return {
        "profil": profil_dominant,
        "scores": scores,
        "score_profil_dominant": score_profil_dominant,
        "indice_subjectif": indice_subjectif,
        "indice_performance": indice_performance,
        "score_global": score_global,
        "coherence": coherence,
        "radar_analytique": radar_analytique,
        "alerte_discordance": alerte_discordance,
        "commentaires": commentaires
    }

def afficher_radar(valeurs, taille=(4, 4), titre=None):
    labels = list(valeurs.keys())
    donnees = list(valeurs.values())
    donnees += donnees[:1]
    angles = [n / float(len(labels)) * 2 * np.pi for n in range(len(labels))] + [0]
    fig, ax = plt.subplots(figsize=taille, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#cccaca')
    ax.plot(angles, donnees, linewidth=2, color='#444')
    ax.fill(angles, donnees, color='#8888ff', alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    if titre:
        ax.set_title(titre, fontsize=12, pad=20)
    st.pyplot(fig)

def plot_jauge_multizone(nom, valeur, min_val, max_val, bornes_abs=[], custom_colors=None):
    default_colors = ["#ff4d4d", "#ff944d", "#ffd633", "#4caf50", "#2196f3", "#9c27b0"]
    couleurs = custom_colors if custom_colors else default_colors
    try:
        bornes = sorted([float(b) for b in bornes_abs if str(b).strip() != ""])
    except:
        bornes = []
    bornes = [min_val] + bornes + [max_val]
    zones = list(zip(bornes[:-1], bornes[1:]))
    fig, ax = plt.subplots(figsize=(5, 0.6))
    fig.patch.set_facecolor('#cccaca')
    ax.set_facecolor('#e0e0e0')
    for i, (start, end) in enumerate(zones):
        color = couleurs[i] if i < len(couleurs) else "#cccccc"
        ax.barh(0, end - start, left=start, color=color, edgecolor="white")
    ax.axvline(valeur, color="#004080", linewidth=1)
    ax.text(valeur, -0.6, f"{valeur:.0f}", ha='center', va='top', fontsize=11, color="#004080", fontweight='bold')
    ax.set_xlim(min_val, max_val)
    ax.set_yticks([])
    ax.set_xticks([min_val, max_val])
    ax.set_title(nom, fontsize=13, loc='left')
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig
