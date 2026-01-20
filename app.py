import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="Étude Finance Comportementale", layout="wide")

# Connexion Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialisation de la session
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'step_la' not in st.session_state:
    st.session_state.update({'step_la': 1, 'current_gain': 500.0, 'bounds': [0.0, 2000.0], 'finished_la': False})

st.title("🔬 Étude sur le Profil des Investisseurs")

tabs = st.tabs(["👤 État Civil", "🎲 Test λ", "🧠 Psychologie", "📤 Envoi & Export"])
# --- TAB 1 : PROFIL (Menu déroulant Pays ajouté) ---
with tabs[0]:
    st.subheader("Informations Personnelles")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.user_data['Nom'] = st.text_input("Nom")
        st.session_state.user_data['Prenom'] = st.text_input("Prénom")
        st.session_state.user_data['Age'] = st.number_input("Âge", 18, 99, 25)
    with c2:
        st.session_state.user_data['Genre'] = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"])
        # MENU DÉROULANT PAYS
        st.session_state.user_data['Nationalite'] = st.selectbox("Pays de résidence", PAYS_LISTE)
        st.session_state.user_data['TF'] = st.slider("Nombre de transactions par an", 0, 250, 10)
# --- TAB 2 : BISECTION ---
with tabs[1]:
    if not st.session_state.finished_la:
        st.write(f"**Étape {st.session_state.step_la} / 5**")
        st.info(f"Pari : 50% de gagner {int(st.session_state.current_gain)}€ vs 50% de perdre 500€")
        if st.button("✅ ACCEPTER"):
            st.session_state.bounds[1] = st.session_state.current_gain
            st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
            st.session_state.step_la += 1
            st.rerun()
        if st.button("❌ REFUSER"):
            st.session_state.bounds[0] = st.session_state.current_gain
            st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
            st.session_state.step_la += 1
            st.rerun()
        if st.session_state.step_la > 5:
            st.session_state.finished_la = True
            st.rerun()
    else:
        l_val = st.session_state.current_gain / 500
        st.success(f"Lambda : {l_val:.2f}")
        st.session_state.user_data['LA_Lambda'] = l_val

# --- TAB 3 : PSYCHOLOGIE APPROFONDIE ---
with tabs[2]:
    st.subheader("🧠 Évaluation des Biais Émotionnels & Cognitifs")
    st.write("Indiquez votre degré d'accord avec les affirmations suivantes (1 : Pas du tout d'accord, 5 : Tout à fait d'accord)")

    with st.form("likert_form_complete"):
        # --- SOUS-SECTION : AVERSION AU REGRET (RA) ---
        st.markdown("#### 1. Aversion au Regret (Regret Aversion)")
        st.caption("Mesure de la douleur liée aux erreurs de décision passées ou futures.")
        
        col_ra1, col_ra2 = st.columns(2)
        with col_ra1:
            ra_com = st.select_slider(
                "Regret de commission : 'Je regrette amèrement quand je vends une action et que son prix monte juste après.'",
                options=[1, 2, 3, 4, 5], value=3
            )
        with col_ra2:
            ra_om = st.select_slider(
                "Regret d'omission : 'Je m'en veux terriblement quand je ne saisis pas une opportunité qui s'avère gagnante.'",
                options=[1, 2, 3, 4, 5], value=3
            )
        ra_hold = st.select_slider(
            "Inertie : 'Je préfère garder un titre perdant plutôt que de le vendre et confirmer mon erreur.'",
            options=[1, 2, 3, 4, 5], value=3
        )

        st.divider()

        # --- SOUS-SECTION : PERCEPTION DU RISQUE (RP) ---
        st.markdown("#### 2. Perception du Risque (Risk Perception)")
        st.caption("Mesure de votre jugement subjectif sur l'incertitude actuelle des marchés.")
        
        col_rp1, col_rp2 = st.columns(2)
        with col_rp1:
            rp_uncer = st.select_slider(
                "Incertitude : 'Le marché boursier est actuellement trop imprévisible pour un investisseur moyen.'",
                options=[1, 2, 3, 4, 5], value=3
            )
        with col_rp2:
            rp_loss = st.select_slider(
                "Probabilité de perte : 'La probabilité de subir une perte majeure dans les 6 prochains mois est élevée.'",
                options=[1, 2, 3, 4, 5], value=3
            )
        
        st.divider()

        if st.form_submit_button("🧪 Calculer et Valider mon Profil Psychologique"):
            # Calcul des scores composites (Moyennes)
            # RA Score est la moyenne des 3 items de regret
            st.session_state.user_data['RA_Score'] = round((ra_com + ra_om + ra_hold) / 3, 2)
            # RP Score est la moyenne des 2 items de perception du risque
            st.session_state.user_data['RP_Score'] = round((rp_uncer + rp_loss) / 2, 2)
            
            st.success("Profil psychologique enregistré avec succès !")
            st.info(f"Votre score de Regret : {st.session_state.user_data['RA_Score']}/5 | Votre Perception du Risque : {st.session_state.user_data['RP_Score']}/5")
# --- TAB 4 : ENVOI, PRÉVISUALISATION & DOWNLOAD ---
with tabs[3]:
    if 'LA_Lambda' in st.session_state.user_data and 'RA_Score' in st.session_state.user_data:
        # Création du DataFrame de prévisualisation
        final_row = pd.DataFrame([st.session_state.user_data])
        final_row['Interaction'] = round(final_row['LA_Lambda'] * final_row['RP_Score'], 2)
        
        st.markdown("### 👁️ Prévisualisation de vos données")
        st.write("Voici les informations qui seront transmises au chercheur :")
        st.dataframe(final_row, use_container_width=True)

        st.divider()
        
        col_save, col_dl = st.columns(2)
        
        with col_save:
            st.markdown("#### 1. Sauvegarde en ligne")
            if st.button("🚀 ENVOYER AU GOOGLE SHEET"):
                try:
                    # Lecture sans cache (ttl=0)
                    data = conn.read(worksheet="Sheet1", ttl=0)
                    # Ajout de la ligne
                    updated_df = pd.concat([data, final_row], ignore_index=True)
                    # Mise à jour du Google Sheet
                    conn.update(worksheet="Sheet1", data=updated_df)
                    st.balloons()
                    st.success("Données enregistrées avec succès !")
                except Exception as e:
                    st.error(f"Erreur d'envoi : {e}")

        with col_dl:
            st.markdown("#### 2. Sauvegarde locale")
            # Fonction de conversion CSV
            csv_data = final_row.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 TÉLÉCHARGER MON CSV",
                data=csv_data,
                file_name=f"resultats_{st.session_state.user_data['Nom']}.csv",
                mime='text/csv',
                help="Téléchargez vos résultats directement sur votre ordinateur."
            )
    else:
        st.warning("⚠️ Veuillez compléter les étapes précédentes (Profil, Test λ et Psychologie) pour débloquer l'envoi.")
        st.warning("Veuillez terminer les tests avant d'envoyer.")

