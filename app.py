import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="Collecte Recherche", layout="wide")

# Connexion UNIQUE à Google Sheets (Pas de SQL ici)
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialisation des variables de session
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'step_la' not in st.session_state:
    st.session_state.update({'step_la': 1, 'current_gain': 500.0, 'bounds': [0.0, 2000.0], 'finished_la': False})

st.title("🔬 Étude Finance Comportementale")

tabs = st.tabs(["👤 État Civil", "🎲 Test λ", "🧠 Psychologie", "📤 Envoi"])

# --- TAB 1 : PROFIL ---
with tabs[0]:
    st.session_state.user_data['Nom'] = st.text_input("Nom")
    st.session_state.user_data['Prenom'] = st.text_input("Prénom")
    st.session_state.user_data['Genre'] = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"])
    st.session_state.user_data['Nationalite'] = st.text_input("Nationalité")
    st.session_state.user_data['Age'] = st.number_input("Âge", 18, 99, 25)
    st.session_state.user_data['TF'] = st.slider("Transactions/an", 0, 250, 10)

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
# --- TAB 4 : ENVOI ---
import uuid
from datetime import datetime

with tabs[3]:
    user_data = st.session_state.get('user_data', {})
    
    # Vérification des clés nécessaires
    if 'LA_Lambda' in user_data and 'RP_Score' in user_data:
        try:
            # Conversion en float pour éviter les erreurs
            la = float(user_data['LA_Lambda'])
            rp = float(user_data['RP_Score'])
            
            # Préparation de la ligne
            final_row = pd.DataFrame([user_data])
            final_row['Interaction'] = round(la * rp, 2)
            
            # Ajout d'un ID unique et d'un horodatage
            final_row['Submission_ID'] = str(uuid.uuid4())
            final_row['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            st.write("### Aperçu avant envoi")
            st.dataframe(final_row)
            
            # Bouton d'envoi
            if st.button("🚀 ENVOYER AU CHERCHEUR"):
                try:
                    # Lecture des données existantes
                    data = conn.read(worksheet="Sheet1")
                    
                    # Si data est vide, créer un DataFrame vide avec mêmes colonnes
                    if data is None or data.empty:
                        data = pd.DataFrame(columns=final_row.columns)
                    elif not isinstance(data, pd.DataFrame):
                        data = pd.DataFrame(data)
                    
                    # Fusionner les données
                    updated_df = pd.concat([data, final_row], ignore_index=True)
                    
                    # Mise à jour de la feuille
                    conn.update(worksheet="Sheet1", data=updated_df.values.tolist())
                    
                    st.balloons()
                    st.success("✅ Données enregistrées en temps réel !")
                
                except Exception as e:
                    st.error(f"Erreur d'envoi : {e}")
        
        except ValueError:
            st.error("Les valeurs LA_Lambda et RP_Score doivent être des nombres.")
    
    else:
        st.warning("Veuillez terminer les tests avant d'envoyer.")
