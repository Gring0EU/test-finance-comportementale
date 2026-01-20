import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="Collecte Données Mémoire", layout="wide")

# Connexion au Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialisation des variables
if 'step_la' not in st.session_state:
    st.session_state.update({'step_la': 1, 'current_gain': 500.0, 'bounds': [0.0, 2000.0], 'finished_la': False, 'user_data': {}})

st.title("🔬 Étude Finance Comportementale")
tabs = st.tabs(["👤 Profil", "🎲 Test λ", "🧠 Psychologie", "🚀 Valider & Envoyer"])

# --- TAB 1, 2, 3 (Simplifiés pour l'exemple, gardez votre logique précédente) ---
with tabs[0]:
    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    genre = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"])
    nat = st.text_input("Nationalité")
    age = st.number_input("Âge", 18, 99, 25)
    tf = st.slider("Transactions/an", 0, 200, 10)
    st.session_state.user_data.update({'Nom': nom, 'Prenom': prenom, 'Genre': genre, 'Nationalite': nat, 'Age': age, 'TF': tf})

with tabs[1]:
    # Votre logique de bisection ici...
    if st.button("Simuler fin du test λ"): # Pour vos tests
        st.session_state.user_data['LA_Lambda'] = 2.25
        st.session_state.finished_la = True

with tabs[2]:
    ra = st.slider("Score Regret", 1.0, 5.0, 3.0)
    rp = st.slider("Score Risque", 1.0, 5.0, 3.0)
    st.session_state.user_data.update({'RA_Score': ra, 'RP_Score': rp})

# --- TAB 4 : L'ENVOI RÉEL ---
with tabs[3]:
    st.subheader("Finalisation de l'envoi")
    if 'LA_Lambda' in st.session_state.user_data:
        # Création de la ligne de données
        new_row = pd.DataFrame([st.session_state.user_data])
        new_row['Interaction_LA_RP'] = round(new_row['LA_Lambda'] * new_row['RP_Score'], 2)
        
        st.write("Aperçu de vos données :")
        st.dataframe(new_row)

        if st.button("📤 Envoyer mes réponses"):
            try:
                # 1. Lire les données existantes
                # On utilise Sheet1 (vérifiez bien le nom de l'onglet sur Google !)
                existing_data = conn.read(worksheet="Sheet1")
                
                # 2. Ajouter la nouvelle ligne
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                
                # 3. Mettre à jour le Google Sheet
                conn.update(worksheet="Sheet1", data=updated_df)
                
                st.balloons()
                st.success("✅ Données enregistrées en temps réel sur le serveur !")
            except Exception as e:
                st.error(f"L'envoi a échoué : {e}")
                st.info("Vérifiez que le partage Google Sheet est bien sur 'ÉDITEUR' pour tout le monde.")
    else:
        st.warning("Veuillez terminer les tests avant d'envoyer.")
