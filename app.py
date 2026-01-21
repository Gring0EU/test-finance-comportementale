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
# --- TAB 2 : BISECTION AVANCÉE ---
with tabs[1]:
    # 1. GESTION DES RÈGLES
    if 'rules_read' not in st.session_state:
        st.session_state.rules_read = False

    if not st.session_state.rules_read:
        st.subheader("📖 Règles du Test de Décision")
        st.markdown("""
        Ce test mesure votre **point d'indifférence** : le moment où le gain proposé compenserait juste assez le risque de perte pour que vous hésitiez à jouer.
        
        **Comment ça marche ?**
        1. Pari **Pile ou Face** (50% chance).
        2. Vous **Acceptez**, **Refusez** ou vous déclarez **Indifférent**.
        3. Si vous refusez, le gain proposé augmentera. Si vous acceptez, il diminuera.
        """)
        if st.button("J'ai compris, commencer le test"):
            st.session_state.rules_read = True
            st.rerun()

    # 2. INITIALISATION ET TEST
    else:
        st.subheader("🎲 Mesure de l'Aversion à la Perte")

        # Initialisation si nécessaire
        if 'valeur_perte' not in st.session_state:
            st.session_state.valeur_perte = float(np.random.choice([200.0, 500.0, 1000.0]))
            st.session_state.bounds = [0.0, st.session_state.valeur_perte * 4]
            st.session_state.current_gain = st.session_state.valeur_perte * 1.5

        if not st.session_state.finished_la:
            # Vérification de sécurité pour ne pas dépasser 5 questions
            if st.session_state.step_la > 5:
                st.session_state.finished_la = True
                st.rerun()

            # Interface de test
            st.write(f"Question **{st.session_state.step_la}** sur 5")
            st.progress(min(st.session_state.step_la / 5, 1.0))
            
            perte = int(st.session_state.valeur_perte)
            gain = int(st.session_state.current_gain)
            
            st.info(f"**VOTRE SCÉNARIO :** \n🟢 Gagner **{gain} €** (50%)  \n🔴 Perdre **{perte} €** (50%)")

            col_acc, col_ind, col_ref = st.columns(3)
            
            with col_acc:
                if st.button("✅ ACCEPTER", use_container_width=True):
                    st.session_state.bounds[1] = st.session_state.current_gain
                    st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                    st.session_state.step_la += 1
                    st.rerun()

            with col_ind:
                if st.button("⚖️ INDIFFÉRENT", use_container_width=True):
                    st.session_state.finished_la = True
                    st.rerun()

            with col_ref:
                if st.button("❌ REFUSER", use_container_width=True):
                    st.session_state.bounds[0] = st.session_state.current_gain
                    st.session_state.current_gain = (st.session_state.bounds[0] + st.session_state.bounds[1]) / 2
                    st.session_state.step_la += 1
                    st.rerun()

        else:
            # 3. AFFICHAGE DES RÉSULTATS
            lambda_final = round(st.session_state.current_gain / st.session_state.valeur_perte, 2)
            st.session_state.user_data['LA_Lambda'] = lambda_final
            
            st.success("📈 **Test terminé !**")
            st.metric(label="Votre Coefficient Lambda (λ)", value=lambda_final)
            
            st.write(f"Votre point d'indifférence se situe à un gain de **{int(st.session_state.current_gain)} €** pour une perte de **{int(st.session_state.valeur_perte)} €**.")
            
            if st.button("🔄 Recommencer le test"):
                # Reset spécifique pour le test λ
                for key in ['step_la', 'valeur_perte', 'bounds', 'current_gain', 'finished_la']:
                    if key in st.session_state: del st.session_state[key]
                st.rerun()
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
import streamlit as st
import pandas as pd
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- FONCTION D'ENVOI ---
def envoyer_resultats_mail(donnees):
    expediteur = "morel.hugo74190@gmail.com"
    destinataire = "morel.hugo74190@gmail.com"
    
    # /!\ ATTENTION : Vérifiez bien votre code de 16 lettres sans espaces
    # Il doit ressembler à : "abcd efgh ijkl mnop"
    mot_de_passe = "ywnz zyio xegb xbwk" # J'ai ajouté un 'w' pour l'exemple (16 lettres)

    msg = MIMEMultipart()
    msg['From'] = expediteur
    msg['To'] = destinataire
    msg['Subject'] = f"Résultat Étude - {donnees.get('Nom', 'Anonyme')}"

    corps = "Voici les résultats de l'étude :\n\n"
    for cle, valeur in donnees.items():
        corps += f"{cle} : {valeur}\n"
    
    msg.attach(MIMEText(corps, 'plain'))

    # Connexion sécurisée
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(expediteur, mot_de_passe)
    server.sendmail(expediteur, destinataire, msg.as_string())
    server.quit()

# --- DANS VOTRE TAB 4 (Assurez-vous de l'indentation) ---
# ... (votre code précédent)
with tabs[3]: # Onglet Envoi
    if 'LA_Lambda' in st.session_state.user_data:
        st.markdown("### 📤 Finalisation")
        
        col_save, col_dl = st.columns(2)
        
        with col_save:
            st.markdown("#### 1. Sauvegarde en ligne")
            if st.button("🚀 ENVOYER MES RÉSULTATS PAR MAIL"):
                try:
                    # On utilise les données stockées dans la session
                    envoyer_resultats_mail(st.session_state.user_data)
                    st.balloons()
                    st.success("Vos résultats ont été envoyés avec succès !")
                except Exception as e:
                    st.error(f"Erreur d'envoi : {e}")
                    st.warning("Vérifiez que votre code Google App Password a bien 16 lettres.")
