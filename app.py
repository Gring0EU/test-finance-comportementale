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
        st.write(f"Question {st.session_state.step_la}/5")
        st.info(f"Pari : Gain de {int(st.session_state.current_gain)}€ vs Perte de 500€")
        c1, c2 = st.columns(2)
        if c1.button("✅ ACCEPTER"):
            st.session_state.bounds[1] = st.session_state.current_gain
            st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
            st.session_state.step_la += 1
            st.rerun()
        if c2.button("❌ REFUSER"):
            st.session_state.bounds[0] = st.session_state.current_gain
            st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
            st.session_state.step_la += 1
            st.rerun()
    else:
        l_val = round(st.session_state.current_gain / 500, 2)
        st.success(f"Coefficient Lambda calculé : {l_val}")
        st.session_state.user_data['LA_Lambda'] = l_val

# --- TAB 3 : PSYCHOLOGIE ---
with tabs[2]:
    ra = st.select_slider("Aversion au Regret (1-5)", options=[1,2,3,4,5], value=3)
    rp = st.select_slider("Perception du Risque (1-5)", options=[1,2,3,4,5], value=3)
    if st.button("Enregistrer les scores"):
        st.session_state.user_data['RA_Score'] = ra
        st.session_state.user_data['RP_Score'] = rp
        st.toast("Scores enregistrés !")

# --- TAB 4 : ENVOI ---
with tabs[3]:
    if 'LA_Lambda' in st.session_state.user_data and 'RA_Score' in st.session_state.user_data:
        # Préparation de la ligne
        final_row = pd.DataFrame([st.session_state.user_data])
        final_row['Interaction'] = round(final_row['LA_Lambda'] * final_row['RP_Score'], 2)
        
        st.write("### Aperçu avant envoi")
        st.dataframe(final_row)
        
        if st.button("🚀 ENVOYER AU CHERCHEUR"):
            try:
                # Lecture de l'existant
                # Assurez-vous que l'onglet s'appelle bien Sheet1
                data = conn.read(worksheet="Sheet1")
                
                # Fusion
                updated_df = pd.concat([data, final_row], ignore_index=True)
                
                # Mise à jour
                conn.update(worksheet="Sheet1", data=updated_df)
                st.balloons()
                st.success("Données enregistrées en temps réel !")
            except Exception as e:
                st.error(f"Erreur d'envoi : {e}")
    else:
        st.warning("Veuillez terminer les tests avant d'envoyer.")
