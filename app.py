import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
# On utilise un import sécurisé
try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False

# --- CONFIGURATION ---
st.set_page_config(page_title="Recherche Finance Comportementale", layout="wide")

# Initialisation sécurisée de la connexion
conn = None
if HAS_GSHEETS:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.warning("Connexion Google Sheets en attente de configuration dans les Secrets.")
else:
    st.error("La bibliothèque st-gsheets-connection n'est pas installée. Vérifiez votre fichier requirements.txt")
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="Recherche Finance Comportementale", layout="wide")

# Initialisation sécurisée de la connexion
conn = None
try:
    # Cette ligne cherche les secrets dans le tableau de bord Streamlit
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.warning("Mode hors-ligne : La connexion Google Sheets n'est pas encore configurée dans les 'Secrets'.")

# Initialisation des variables de session
if 'step_la' not in st.session_state:
    st.session_state.update({
        'step_la': 1, 'current_gain': 500.0, 'bounds': [0.0, 2000.0],
        'finished_la': False, 'user_data': {}
    })

st.title("📊 Étude sur le Profil des Investisseurs Individuels")

tabs = st.tabs(["👤 État Civil", "🎲 Test de Décision", "🧠 Échelles Psychologiques", "💾 Envoi des Résultats"])

# --- TAB 1 : IDENTITÉ ---
with tabs[0]:
    st.subheader("Informations Personnelles")
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        age = st.number_input("Âge", 18, 99, 25)
    with c2:
        genre = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"])
        nationalite = st.text_input("Nationalité")
        tf_freq = st.slider("Transactions par an", 0, 250, 12)
    st.session_state.user_data.update({'Nom': nom, 'Prenom': prenom, 'Genre': genre, 'Nationalite': nationalite, 'Age': age, 'TF': tf_freq})

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

# --- TAB 3 : PSYCHOLOGIE ---
with tabs[2]:
    with st.form("likert"):
        ra = st.select_slider("Aversion au Regret", options=[1,2,3,4,5], value=3)
        rp = st.select_slider("Perception du Risque", options=[1,2,3,4,5], value=3)
        if st.form_submit_button("Valider"):
            st.session_state.user_data.update({'RA_Score': ra, 'RP_Score': rp})

# --- TAB 4 : ENVOI ---
with tabs[3]:
    if 'LA_Lambda' in st.session_state.user_data:
        df = pd.DataFrame([st.session_state.user_data])
        st.table(df)
        
        if st.button("🚀 ENVOYER LES DONNÉES"):
            if conn is not None:
                try:
                    # Tente de lire et mettre à jour
                    data = conn.read(worksheet="Sheet1")
                    new_df = pd.concat([data, df], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=new_df)
                    st.success("Données envoyées !")
                    st.balloons()
                except Exception as e:
                    st.error("Erreur d'accès au fichier Google Sheets. Vérifiez l'URL dans les Secrets.")
            else:
                st.error("Connexion impossible. Téléchargez le CSV ci-dessous.")
        
        st.download_button("📥 Télécharger CSV (Sécurité)", df.to_csv(index=False).encode('utf-8'), "data.csv")
