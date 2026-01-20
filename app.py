import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="Étude Finance Comportementale MOREL Hugo", layout="wide")

# Connexion Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialisation de la session
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'step_la' not in st.session_state:
    st.session_state.update({'step_la': 1, 'current_gain': 500.0, 'bounds': [0.0, 2000.0], 'finished_la': False})

st.title("🔬 Étude sur le Profil des Investisseurs MOREL Hugo")

tabs = st.tabs(["👤 État Civil", "🎲 Test λ", "🧠 Psychologie", "📤 Envoi & Export"])
# --- TAB 1 : PROFIL ---
with tabs[0]:
    st.session_state.user_data['Nom'] = st.text_input("Nom")
    st.session_state.user_data['Prenom'] = st.text_input("Prénom")
    st.session_state.user_data['Genre'] = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"])
    st.session_state.user_data['Nationalite'] = st.text_input("Nationalité")
    st.session_state.user_data['Age'] = st.number_input("Âge", 18, 99, 25)
    st.session_state.user_data['TF'] = st.slider("Transactions/an", 0, 250, 10)
# --- TAB 2 : BISECTION AVANCÉE (PRÉCISION & ANTI-ANCRAGE) ---
with tabs[1]:
    st.subheader("🎲 Mesure de l'Aversion à la Perte")

    # 1. INITIALISATION ALÉATOIRE (Une seule fois au début du test)
    if 'valeur_perte' not in st.session_state:
        # On tire au sort une base de perte : 200, 500 ou 1000€
        st.session_state.valeur_perte = np.random.choice([200.0, 500.0, 1000.0])
        # On ajuste les bornes en fonction de la perte (Gain min = 0, Gain max = 4x la perte)
        st.session_state.bounds = [0.0, st.session_state.valeur_perte * 4]
        # Le gain de départ est 1.5x la perte (moyenne théorique de basculement)
        st.session_state.current_gain = st.session_state.valeur_perte * 1.5

    if not st.session_state.finished_la:
        # Barre de progression
        st.write(f"Question **{st.session_state.step_la}** sur 5")
        st.progress(st.session_state.step_la / 5)
        
        st.write("Accepteriez-vous le pari suivant ?")

        # 2. AFFICHAGE DU PARI (Design épuré)
        perte = int(st.session_state.valeur_perte)
        gain = int(st.session_state.current_gain)
        
        st.info(f"""
        **VOTRE SCÉNARIO :**
        - 🟢 **Gagner {gain} €** (Probabilité : 50%)
        - 🔴 **Perdre {perte} €** (Probabilité : 50%)
        """)

        # 3. LES TROIS OPTIONS (Accepter, Indifférent, Refuser)
        col_acc, col_ind, col_ref = st.columns(3)
        
        with col_acc:
            if st.button("✅ ACCEPTER", use_container_width=True):
                # Si accepté, le gain est suffisant, on réduit la borne haute
                st.session_state.bounds[1] = st.session_state.current_gain
                st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                st.session_state.step_la += 1
                st.rerun()

        with col_ind:
            if st.button("⚖️ INDIFFÉRENT", use_container_width=True):
                # Point d'indifférence atteint : on arrête le test ici
                st.session_state.finished_la = True
                st.rerun()

        with col_ref:
            if st.button("❌ REFUSER", use_container_width=True):
                # Si refusé, le gain est trop bas, on augmente la borne basse
                st.session_state.bounds[0] = st.session_state.current_gain
                st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                st.session_state.step_la += 1
                st.rerun()

        # Fin automatique après 5 étapes
        if st.session_state.step_la > 5:
            st.session_state.finished_la = True
            st.rerun()

    else:
        # 4. CALCUL DU LAMBDA (λ)
        # λ = Gain au point d'indifférence / Perte
        lambda_final = round(st.session_state.current_gain / st.session_state.valeur_perte, 2)
        st.session_state.user_data['LA_Lambda'] = lambda_final
        
        st.success(f"📈 **Test terminé !**")
        st.write(f"Votre point d'indifférence se situe à un gain de **{int(st.session_state.current_gain)} €** pour une perte de **{int(st.session_state.valeur_perte)} €**.")
        st.metric(label="Votre Coefficient Lambda (λ)", value=lambda_final)
        
        if lambda_final > 1.0:
            st.write("Cela indique une certaine aversion à la perte.")
        else:
            st.write("Cela indique une neutralité ou une recherche de risque.")
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

