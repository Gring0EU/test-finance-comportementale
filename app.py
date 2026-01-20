import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION DE L'APPLICATION ---
st.set_page_config(page_title="Recherche Finance Comportementale", layout="wide")

# Initialisation des variables de session (mémoire de l'app)
if 'step_la' not in st.session_state:
    st.session_state.update({
        'step_la': 1,
        'current_gain': 500.0,
        'bounds': [0.0, 2000.0],
        'finished_la': False,
        'user_data': {}
    })

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #007bff; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# --- TITRE ET INTRODUCTION ---
st.title("🔬 Collecte de Données : Biais et Comportement d'Investissement")
st.info("Ce test est anonyme. Les données collectées serviront exclusivement à l'analyse statistique de mon mémoire.")

tabs = st.tabs(["👤 Profil", "🎲 Test de Décision", "🧠 Échelles", "📊 Synthèse"])

# --- TAB 1 : PROFIL & TRADING ---
with tabs[0]:
    st.subheader("Informations Générales")
    col1, col2 = st.columns(2)
    with col1:
        u_id = st.text_input("Identifiant (ex: P01, P02...)", "P01")
        age = st.number_input("Âge", 18, 99, 25)
    with col2:
        education = st.selectbox("Niveau d'études", ["Bac", "Licence", "Master", "Doctorat"])
        tf_freq = st.slider("Nombre de transactions par an", 0, 200, 12)
    
    st.session_state.user_data.update({'id': u_id, 'age': age, 'edu': education, 'tf': tf_freq})

# --- TAB 2 : BISECTION (AVERSION À LA PERTE) ---
with tabs[1]:
    st.subheader("Test de Bisection : Sensibilité aux Pertes")
    
    if not st.session_state.finished_la:
        st.write(f"**Étape {st.session_state.step_la} sur 5**")
        st.write("Considérez la loterie suivante :")
        
        # Affichage du scénario
        c_a, c_b = st.columns(2)
        with c_a:
            st.metric("Pari risqué (50/50)", f"Gain : {int(st.session_state.current_gain)} €")
            st.metric("Perte potentielle", "- 500 €", delta_color="inverse")
        with c_b:
            st.write("**Préférez-vous :**")
            if st.button("Accepter le Pari 🎰"):
                # Si accepté, le gain est trop élevé, on baisse la borne haute
                st.session_state.bounds[1] = st.session_state.current_gain
                st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                st.session_state.step_la += 1
                st.rerun()
            
            if st.button("Refuser le Pari (0 €) 🛑"):
                # Si refusé, le gain n'est pas assez attractif, on monte la borne basse
                st.session_state.bounds[0] = st.session_state.current_gain
                st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                st.session_state.step_la += 1
                st.rerun()
                
        if st.session_state.step_la > 5:
            st.session_state.finished_la = True
            st.rerun()
    else:
        lambda_final = st.session_state.current_gain / 500
        st.success(f"Test terminé. Votre coefficient calculé est λ = {lambda_final:.2f}")
        st.session_state.user_data['la_lambda'] = lambda_final

# --- TAB 3 : ÉCHELLES LIKERT (RA & RP) ---
with tabs[2]:
    st.subheader("Évaluation Psychologique")
    st.write("Indiquez votre degré d'accord (1: Pas du tout, 5: Tout à fait)")
    
    with st.form("likert_scales"):
        st.markdown("**Aversion au Regret (RA)**")
        ra1 = st.radio("Je regrette amèrement mes décisions quand le cours baisse juste après mon achat.", [1,2,3,4,5], horizontal=True)
        ra2 = st.radio("Je préfère attendre que le prix remonte plutôt que de vendre à perte et admettre une erreur.", [1,2,3,4,5], horizontal=True)
        
        st.divider()
        st.markdown("**Perception du Risque (RP)**")
        rp1 = st.radio("Le marché financier actuel est imprévisible et dangereux.", [1,2,3,4,5], horizontal=True)
        
        submit = st.form_submit_button("Enregistrer mes réponses")
        if submit:
            st.session_state.user_data['ra_score'] = (ra1 + ra2) / 2
            st.session_state.user_data['rp_score'] = rp1
            st.balloons()

# --- TAB 4 : EXPORT ET VISUALISATION ---
with tabs[3]:
    if 'la_lambda' in st.session_state.user_data and 'ra_score' in st.session_state.user_data:
        st.subheader("Synthèse de vos données")
        
        # Préparation du DataFrame final
        df = pd.DataFrame([st.session_state.user_data])
        # Ajout du terme d'interaction pour le modèle
        df['Interaction_LA_RP'] = df['la_lambda'] * df['rp_score']
        
        st.dataframe(df)
        
        # Visualisation de la courbe
        l_val = st.session_state.user_data['la_lambda']
        x = np.linspace(-100, 100, 200)
        # v(x) simplifié : x si x>=0, -lambda * (-x) si x<0
        y = [val if val >= 0 else -l_val * abs(val) for val in x]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, line=dict(color='blue')))
        fig.add_annotation(text=f"Cassure (λ = {l_val:.2f})", x=0, y=0, arrowhead=1)
        fig.update_layout(title="Représentation de votre Aversion à la Perte", xaxis_title="Gains/Pertes", yaxis_title="Valeur perçue")
        st.plotly_chart(fig)
        
        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger le fichier CSV pour l'analyse", csv, f"data_{u_id}.csv", "text/csv")
    else:
        st.warning("Veuillez compléter toutes les sections précédentes.")
