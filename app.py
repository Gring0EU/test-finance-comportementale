import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Recherche Finance Comportementale", layout="wide")

# Initialisation des variables de session
if 'step_la' not in st.session_state:
    st.session_state.update({
        'step_la': 1,
        'current_gain': 500.0,
        'bounds': [0.0, 2000.0],
        'finished_la': False,
        'user_data': {}
    })

# --- TITRE ---
st.title("📊 Collecte de Données : Profil de l'Investisseur")
st.markdown("---")

tabs = st.tabs(["👤 État Civil", "🎲 Test de Décision", "🧠 Échelles Psychologiques", "💾 Synthèse & Export"])

# --- TAB 1 : IDENTITÉ & PROFIL ---
with tabs[0]:
    st.subheader("Informations Personnelles")
    col1, col2 = st.columns(2)
    
    with col1:
        nom = st.text_input("Nom", "")
        prenom = st.text_input("Prénom", "")
        age = st.number_input("Âge", 18, 99, 25)
        
    with col2:
        genre = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"])
        nationalite = st.text_input("Nationalité (ex: Française, Belge...)", "")
        tf_freq = st.slider("Fréquence de trading (Nombre de transactions par an)", 0, 250, 12)

    # Sauvegarde dans la session
    st.session_state.user_data.update({
        'Nom': nom,
        'Prenom': prenom,
        'Genre': genre,
        'Nationalite': nationalite,
        'Age': age,
        'TF': tf_freq
    })

# --- TAB 2 : BISECTION (AVERSION À LA PERTE) ---
with tabs[1]:
    st.subheader("Mesure de l'Aversion à la Perte (λ)")
    
    if not st.session_state.finished_la:
        st.write(f"**Étape {st.session_state.step_la} sur 5**")
        st.info(f"Scénario : 50% de chance de gagner **{int(st.session_state.current_gain)}€** contre 50% de chance de perdre **500€**.")
        
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("✅ J'ACCEPTE LE PARI"):
                st.session_state.bounds[1] = st.session_state.current_gain
                st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                st.session_state.step_la += 1
                st.rerun()
        with c_b:
            if st.button("❌ JE REFUSE LE PARI"):
                st.session_state.bounds[0] = st.session_state.current_gain
                st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                st.session_state.step_la += 1
                st.rerun()
                
        if st.session_state.step_la > 5:
            st.session_state.finished_la = True
            st.rerun()
    else:
        lambda_final = st.session_state.current_gain / 500
        st.success(f"Test terminé. Coefficient Lambda (λ) : {lambda_final:.2f}")
        st.session_state.user_data['LA_Lambda'] = lambda_final

# --- TAB 3 : PSYCHOLOGIE (LIKERT) ---
with tabs[2]:
    st.subheader("Regret et Perception du Risque")
    with st.form("likert_scales"):
        st.write("**Aversion au Regret (RA)**")
        ra1 = st.select_slider("Je regrette mes décisions quand le marché baisse juste après un achat.", options=[1, 2, 3, 4, 5], value=3)
        ra2 = st.select_slider("J'attends que le prix remonte pour ne pas vendre à perte.", options=[1, 2, 3, 4, 5], value=3)
        
        st.divider()
        st.write("**Perception du Risque (RP)**")
        rp1 = st.select_slider("Le marché financier actuel est imprévisible et risqué.", options=[1, 2, 3, 4, 5], value=3)
        
        if st.form_submit_button("Calculer les scores"):
            st.session_state.user_data['RA_Score'] = (ra1 + ra2) / 2
            st.session_state.user_data['RP_Score'] = rp1
            st.success("Scores enregistrés !")

# --- TAB 4 : SYNTHÈSE ET EXPORT ---
with tabs[3]:
    if 'LA_Lambda' in st.session_state.user_data and 'RA_Score' in st.session_state.user_data:
        st.subheader("Récapitulatif des données collectées")
        
        # DataFrame final
        df = pd.DataFrame([st.session_state.user_data])
        # Calcul du terme d'interaction pour la régression
        df['Interaction_LA_RP'] = df['LA_Lambda'] * df['RP_Score']
        
        st.dataframe(df)
        
        # Visualisation
        l_val = st.session_state.user_data['LA_Lambda']
        x = np.linspace(-100, 100, 200)
        y = [val if val >= 0 else -l_val * abs(val) for val in x]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, name="Utilité perçue", line=dict(color='blue', width=3)))
        fig.update_layout(title=f"Fonction d'Utilité de {nom} {prenom}", xaxis_title="Gains / Pertes", yaxis_title="Valeur Psychologique")
        st.plotly_chart(fig)
        
        # Export CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(f"📥 Télécharger les données de {nom}_{prenom}", csv, f"data_{nom}_{prenom}.csv", "text/csv")
    else:
        st.warning("Veuillez remplir toutes les sections (Profil, Test et Échelles) pour finaliser.")
