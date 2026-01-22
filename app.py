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

        st.info("Le nombre de transactions par an nous aide à comprendre votre style d'investissement")
# --- TAB 2 : BISECTION AVANCÉE ---
with tabs[1]:
    # 1. GESTION DES RÈGLES
    if 'rules_read' not in st.session_state:
        st.session_state.rules_read = False

    if not st.session_state.rules_read:
        st.subheader("📖 Règles du Test de Décision")
        
        st.markdown("""
        Ce test vise à comprendre comment vous arbitrez entre un **gain potentiel** et une **perte certaine**. 
        Il n'y a pas de réponse mathématiquement "juste" : la meilleure réponse est celle qui reflète votre instinct.
        
        **Comment ça marche ?**
        1. On vous propose un pari de type **Pile ou Face** (50% de chance).
        2. Vous devez décider si vous **Acceptez** de jouer ou si vous **Refusez**.
        3. Si vous refusez, vous ne gagnez rien mais vous ne perdez rien (0 €).
        4. Le test s'ajustera en fonction de vos réponses pour trouver votre **point d'équilibre**.
        """)
        
        st.info("💡 **Le point d'indifférence :** C'est le moment où le gain proposé est juste assez élevé pour que vous acceptiez de risquer la perte.")
        
        if st.button("🚀 J'ai compris, commencer le test"):
            st.session_state.rules_read = True
            st.rerun()

    # 2. INITIALISATION ET LOGIQUE DU TEST
    else:
        st.subheader("🎲 Mesure de l'Aversion à la Perte")

        # Initialisation des variables du test si elles n'existent pas
        if 'valeur_perte' not in st.session_state:
            st.session_state.valeur_perte = float(np.random.choice([200.0, 500.0, 1000.0]))
            st.session_state.bounds = [0.0, st.session_state.valeur_perte * 4]
            st.session_state.current_gain = st.session_state.valeur_perte * 1.5
            st.session_state.step_la = 1
            st.session_state.finished_la = False

        if not st.session_state.finished_la:
            # Sécurité : fin après 5 questions
            if st.session_state.step_la > 5:
                st.session_state.finished_la = True
                st.rerun()

            # Interface de test
            st.write(f"Question **{st.session_state.step_la}** sur 5")
            st.progress(min(st.session_state.step_la / 5, 1.0))
            
            perte = int(st.session_state.valeur_perte)
            gain = int(st.session_state.current_gain)
            
            st.info(f"**VOTRE SCÉNARIO :** \n\n🟢 Gagner **{gain} €** (50%) \n\n🔴 Perdre **{perte} €** (50%)")

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
            
            # Bouton pour recommencer
            if st.button("🔄 Recommencer le test"):
                keys_to_reset = ['step_la', 'valeur_perte', 'bounds', 'current_gain', 'finished_la', 'rules_read']
                for key in keys_to_reset:
                    if key in st.session_state:
                        del st.session_state[key]
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
import smtplib
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def envoyer_resultats_mail(donnees):
    expediteur = "morel.hugo74190@gmail.com"
    destinataire = "morel.hugo74190@gmail.com"
    mot_de_passe = "ywnz zyio xegb xbwk" 

    # 1. Création du message de base
    msg = MIMEMultipart()
    msg['From'] = expediteur
    msg['To'] = destinataire
    msg['Subject'] = f"📊 Résultat Étude - {donnees.get('Nom', 'Anonyme')}"

    # 2. Création du tableau HTML pour le corps du mail
    lignes_tableau = ""
    for cle, valeur in donnees.items():
        lignes_tableau += f"<tr><td style='border:1px solid #ddd;padding:8px;'><b>{cle}</b></td><td style='border:1px solid #ddd;padding:8px;'>{valeur}</td></tr>"

    html = f"""
    <html>
    <body>
        <h3>Récapitulatif des réponses (Vue rapide) :</h3>
        <table style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #4CAF50; color: white;">
                <th style="border:1px solid #ddd;padding:12px;">Variable</th>
                <th style="border:1px solid #ddd;padding:12px;">Valeur</th>
            </tr>
            {lignes_tableau}
        </table>
        <p><i>Le fichier CSV est également joint à ce mail pour votre base de données.</i></p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))

    # 3. Création et Ajout de la pièce jointe CSV
    # On transforme le dictionnaire en DataFrame puis en CSV
    df = pd.DataFrame([donnees])
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(csv_buffer.getvalue().encode('utf-8'))
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename=resultat_{donnees.get('Nom', 'etude')}.csv")
    msg.attach(part)

    # 4. Envoi sécurisé
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(expediteur, mot_de_passe)
    server.sendmail(expediteur, destinataire, msg.as_string())
    server.quit()

# --- TAB 4 : ENVOI, PRÉVISUALISATION & DOWNLOAD ---
with tabs[3]:
    st.subheader("📤 Finalisation de l'étude")

    # 1. VÉRIFICATION DES ÉTAPES
    # On vérifie si les données essentielles sont présentes dans session_state
    nom_saisi = st.session_state.user_data.get('Nom', '').strip()
    prenom_saisi = st.session_state.user_data.get('Prenom', '').strip()
    
    etape1_ok = len(nom_saisi) > 0 and len(prenom_saisi) > 0
    etape2_ok = st.session_state.get('finished_la', False)
    etape3_ok = 'RA_Score' in st.session_state.user_data

    st.markdown("### 📋 État de votre progression")
    
    col_check1, col_check2, col_check3 = st.columns(3)
    
    with col_check1:
        if etape1_ok:
            st.success("✅ Section 1 : OK")
        else:
            st.error("❌ Section 1 : Profil")
            
    with col_check2:
        if etape2_ok:
            st.success("✅ Section 2 : OK")
        else:
            st.error("❌ Section 2 : Test λ")

    with col_check3:
        if etape3_ok:
            st.success("✅ Section 3 : OK")
        else:
            st.warning("⚠️ Section 3 : Psycho")

    st.divider()

    # 2. AFFICHAGE DU CONTENU DYNAMIQUE
    if etape1_ok and etape2_ok:
        st.markdown("### 👁️ Prévisualisation")
        
        # Création du DataFrame pour l'affichage et le CSV
        final_row = pd.DataFrame([st.session_state.user_data])
        st.dataframe(final_row, use_container_width=True)

        col_save, col_dl = st.columns(2)
        
        with col_save:
            st.markdown("#### Envoi direct")
            if st.button("🚀 ENVOYER PAR MAIL", use_container_width=True):
                try:
                    envoyer_resultats_mail(st.session_state.user_data)
                    st.balloons()
                    st.success("Données transmises avec succès !")
                except Exception as e:
                    st.error(f"Erreur d'envoi : {e}")
                    st.info("Note : Vérifiez la validité de votre Google App Password.")

        with col_dl:
            st.markdown("#### Sauvegarde locale")
            csv_data = final_row.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 TÉLÉCHARGER LE CSV",
                data=csv_data,
                file_name=f"etude_finance_{nom_saisi}.csv",
                mime='text/csv',
                use_container_width=True
            )
    else:
        # Message d'avertissement si blocage
        st.warning("⚠️ **L'envoi est bloqué.**")
        
        messages_manquants = []
        if not etape1_ok:
            messages_manquants.append("- Veuillez remplir votre **Nom et Prénom** dans l'onglet **État Civil**.")
        if not etape2_ok:
            messages_manquants.append("- Veuillez terminer le **Test λ** jusqu'à la fin des 5 questions ou cliquer sur 'Indifférent'.")
        
        for msg in messages_manquants:
            st.info(msg)
