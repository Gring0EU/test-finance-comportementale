import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="Recherche Finance Comportementale", layout="wide")

# Connexion à Google Sheets (nécessite configuration des Secrets sur Streamlit Cloud)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Connexion Google Sheets non configurée.")

# Initialisation des variables de session
if 'step_la' not in st.session_state:
    st.session_state.update({
        'step_la': 1,
        'current_gain': 500.0,
        'bounds': [0.0, 2000.0],
        'finished_la': False,
        'user_data': {}
    })

st.title("📊 Étude sur le Profil des Investisseurs Individuels")
st.markdown("---")

tabs = st.tabs(["👤 État Civil", "🎲 Test de Décision", "🧠 Échelles Psychologiques", "💾 Envoi des Résultats"])

# --- TAB 1 : IDENTITÉ ---
with tabs[0]:
    st.subheader("Informations Personnelles")
    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom", "")
        prenom = st.text_input("Prénom", "")
        age = st.number_input("Âge", 18, 99, 25)
    with col2:
        genre = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"])
        nationalite = st.text_input("Nationalité", "")
        tf_freq = st.slider("Nombre de transactions par an", 0, 250, 12)

    st.session_state.user_data.update({
        'Nom': nom, 'Prenom': prenom, 'Genre': genre, 
        'Nationalite': nationalite, 'Age': age, 'TF': tf_freq
    })

# --- TAB 2 : BISECTION (MÉTHODE VAN DOLDER & VANDENBROUCKE) ---
with tabs[1]:
    st.subheader("Mesure de l'Aversion à la Perte (λ)")
    if not st.session_state.finished_la:
        st.write(f"**Étape {st.session_state.step_la} sur 5**")
        st.info(f"Scénario : 50% de chance de gagner **{int(st.session_state.current_gain)}€** vs 50% de perdre **500€**.")
        
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("✅ ACCEPTER LE PARI"):
                st.session_state.bounds[1] = st.session_state.current_gain
                st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                st.session_state.step_la += 1
                st.rerun()
        with c_b:
            if st.button("❌ REFUSER LE PARI"):
                st.session_state.bounds[0] = st.session_state.current_gain
                st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                st.session_state.step_la += 1
                st.rerun()
                
        if st.session_state.step_la > 5:
            st.session_state.finished_la = True
            st.rerun()
    else:
        lambda_final = st.session_state.current_gain / 500
        st.success(f"Coefficient Lambda (λ) calculé : {lambda_final:.2f}")
        st.session_state.user_data['LA_Lambda'] = lambda_final

# --- TAB 3 : PSYCHOLOGIE ---
with tabs[2]:
    st.subheader("Échelles de Regret et de Risque")
    with st.form("likert_form"):
        ra1 = st.select_slider("Je regrette mes décisions quand le marché baisse après un achat.", options=[1,2,3,4,5], value=3)
        ra2 = st.select_slider("J'attends que le prix remonte pour ne pas admettre une perte.", options=[1,2,3,4,5], value=3)
        rp1 = st.select_slider("Le marché financier actuel est imprévisible et risqué.", options=[1,2,3,4,5], value=3)
        
        if st.form_submit_button("Enregistrer les scores"):
            st.session_state.user_data['RA_Score'] = (ra1 + ra2) / 2
            st.session_state.user_data['RP_Score'] = rp1
            st.success("Scores enregistrés !")

# --- TAB 4 : CENTRALISATION ---
with tabs[3]:
    if 'LA_Lambda' in st.session_state.user_data and 'RA_Score' in st.session_state.user_data:
        df = pd.DataFrame([st.session_state.user_data])
        df['Interaction_LA_RP'] = df['LA_Lambda'] * df['RP_Score']
        
        st.write("### Synthèse de vos résultats")
        st.table(df)
        
        # Visualisation de la courbe de Tversky & Kahneman
        l_val = st.session_state.user_data['LA_Lambda']
        x = np.linspace(-100, 100, 200)
        y = [val if val >= 0 else -l_val * abs(val) for val in x]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, line=dict(color='blue', width=3)))
        fig.update_layout(title="Votre Courbe de Valeur Psychologique", xaxis_title="Gains/Pertes", yaxis_title="Valeur")
        st.plotly_chart(fig)

        # BOUTON D'ENVOI FINAL
        if st.button("🚀 ENVOYER MES DONNÉES AU CHERCHEUR"):
            try:
                # Lecture des données existantes pour empiler
                existing_data = conn.read(worksheet="Sheet1")
                updated_df = pd.concat([existing_data, df], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.balloons()
                st.success("Merci ! Vos données ont été ajoutées à la base de recherche.")
            except Exception as e:
                st.error("Erreur d'envoi. Veuillez télécharger le CSV et me l'envoyer par mail.")
                st.download_button("📥 Télécharger CSV", df.to_csv(index=False).encode('utf-8'), "data.csv")
    else:
        st.warning("Complétez les étapes précédentes.")
