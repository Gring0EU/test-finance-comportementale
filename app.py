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

# --- TAB 4 : ENVOI DES RÉSULTATS ---
with tabs[3]:
    if 'LA_Lambda' in st.session_state.user_data:
        # On prépare la ligne à envoyer
        df = pd.DataFrame([st.session_state.user_data])
        df['Interaction_LA_RP'] = df['LA_Lambda'] * df.get('RP_Score', 0)
        
        st.write("### Vos résultats")
        st.table(df)

        if st.button("🚀 ENVOYER AU CHERCHEUR"):
            if conn is not None:
                try:
                    # Charger les données actuelles
                    # IMPORTANT : Vérifiez que l'onglet s'appelle bien "Sheet1" ou changez ici
                    existing_data = conn.read(worksheet="Sheet1")
                    
                    # Fusionner et envoyer
                    updated_df = pd.concat([existing_data, df], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_df)
                    
                    st.balloons()
                    st.success("Données enregistrées dans la base centrale !")
                except Exception as e:
                    st.error(f"Erreur technique : {e}")
                    st.info("Vérifiez que le nom de l'onglet est bien 'Sheet1' et que l'accès est en 'Éditeur'.")
            else:
                st.error("Connexion impossible : Les Secrets ne sont pas configurés sur Streamlit Cloud.")
        
        # Sécurité : Toujours proposer le CSV si le cloud échoue
        st.download_button("📥 Télécharger mon CSV (si l'envoi échoue)", df.to_csv(index=False).encode('utf-8'), "data.csv")
