import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import os

# Configuration de l'application
st.set_page_config(page_title="Système d'Analyse Statistique Pédagogique", layout="wide")

# ==========================================
# INITIALISATION DES BASES DE DONNÉES (SESSION)
# ==========================================
if 'db_apprenants' not in st.session_state:
    st.session_state.db_apprenants = pd.DataFrame(columns=[
        "ID", "Sexe", "Classe", "Etablissement", "Frequence_Ex", 
        "Types_Ex", "Comprehension_Consignes", "Outils_Dispo", 
        "Impact_Comprehension", "Difficultes", "Exemple_Exercice", 
        "Attentes_Prof", "Utilite_Citoyenne"
    ])

if 'id_a_modifier' not in st.session_state:
    st.session_state.id_a_modifier = None

# =========================================================
# MOTEUR INTERPRÉTATIF GLOBAL
# =========================================================
def generer_synthese_axe(axe_colonne, df):
    total = len(df)
    if total == 0:
        return {
            "Critique": "Aucune donnée n'est actuellement enregistrée pour cet indicateur.",
            "Interpretation": "L'analyse est suspendue en attente de soumissions via le formulaire questionnaire.",
            "Solution": "Recommandation : Veuillez renseigner des fiches apprenants pour générer un diagnostic."
        }
        
    counts = df[axe_colonne].value_counts()
    critique, interpretation, solution = "", "", ""
    
    if axe_colonne == "Comprehension_Consignes":
        mal_compris = counts.get("Non, pas vraiment", 0) + counts.get("Oui, parfois", 0)
        pct = (mal_compris / total) * 100
        critique = f"L'évaluation quantitative révèle une zone d'ombre didactique majeure : {pct:.1f}% des apprenants manifestent un déficit d'assimilation (partiel ou total) vis-à-vis des consignes dictées lors des travaux pratiques."
        interpretation = "Ce phénomène met en exergue un écart de décodage sémantique. La formulation textuelle ou conceptuelle des instructions fait face à une barrière d'autonomie cognitive chez les élèves, souvent accentuée par le manque de phases de contextualisation en amont."
        solution = "Axe d'optimisation : Instaurer un protocole de clarification systémique. Impliquer un élève témoin pour reformuler la consigne avec ses propres mots avant le lancement de l'activité, et vulgariser les verbes d'action sous forme d'infographies méthodologiques."
        
    elif axe_colonne == "Outils_Dispo":
        sans_outils = counts.get("Non", 0)
        pct = (sans_outils / total) * 100
        if pct > 0:
            critique = f"Le diagnostic infrastructurel met en relief une fracture logistique contraignante : {pct:.1f}% de la population échantillonnée évolue sans les supports matériels obligatoires (manuels, atlas, extraits de documents)."
            interpretation = "La carence en outils didactiques individuels agit comme un vecteur d'iniquité d'apprentissage. Elle ralentit la cadence d'exécution des ateliers pratiques et restreint l'ancrage empirique des connaissances théoriques."
            solution = "Axe d'optimisation : Mettre en place un écosystème de mutualisation au sein de la classe (ingénierie par binômes solidaires) et concevoir un répertoire de fiches documentaires plastifiées à usage partagé."
        else:
            critique = "L'indicateur logistique présente un profil optimal : 100% des apprenants disposent de l'environnement matériel requis."
            interpretation = "Cette convergence matérielle garantit l'alignement pédagogique et offre des conditions idéales pour une mise en pratique fluide et immédiate des savoirs."
            solution = "Axe d'optimisation : Capitaliser sur cette robustesse logistique pour introduire graduellement des supports documentaires plus complexes ou des composantes numériques complémentaires."

    elif axe_colonne == "Impact_Comprehension":
        positif = counts.get("Oui, beaucoup", 0) + counts.get("Oui, un peu", 0)
        pct = (positif / total) * 100
        critique = f"La corrélation empirique est solidement validée : {pct:.1f}% des apprenants attribuent une valeur ajoutée explicite aux exercices pratiques dans le processus de clarification des cours magistraux."
        interpretation = "Cela corrobore les théories du constructivisme pédagogique : le passage par la manipulation textuelle, cartographique ou statistique donne du sens au savoir abstrait, ancrant les concepts d'Histoire-Géographie dans la mémoire sémantique à long terme."
        solution = "Axe d'optimisation : Institutionnaliser ces ateliers pratiques à intervalles réguliers tout en veillant à une gestion rigoureuse du temps (micro-ateliers rythmés) pour préserver l'équilibre du programme annuel."

    elif axe_colonne == "Utilite_Citoyenne":
        flou = counts.get("Je ne sais pas", 0) + counts.get("Non", 0)
        pct = (flou / total) * 100
        critique = f"Un découplage civique sensible est identifié : {pct:.1f}% des élèves n'établissent pas de lien direct ou conscient entre la finalité des exercices pratiques et leur projection en tant que citoyens actifs."
        interpretation = "L'Éducation à la Citoyenneté souffre d'un biais d'abstraction. Elle émerge comme une discipline purement académique évaluative plutôt que comme une boîte à outils pratique dédiée à la compréhension et à la transformation des réalités sociétales."
        solution = "Axe d'optimisation : Réancrer l'enseignement civique dans l'immédiateté du terrain. Adosser les exercices à des cas concrets de gouvernance de proximité (analyse du budget participatif d'une commune, enquêtes collectives de salubrité de quartier, simulations de conseils municipaux)."

    return {"Critique": critique, "Interpretation": interpretation, "Solution": solution}

# =========================================================
# GÉNÉRATION DU RAPPORT EXECUTIVE (PDF HAUTE QUALITÉ)
# =========================================================
def generer_pdf_statistique(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    if df.empty:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Rapport Analytique - Aucune donnee disponible", ln=True, align="C")
        return pdf.output()
        
    axes_analyse = [
        {"titre": "1. NIVEAU DE COMPREHENSION DES CONSIGNES DEDUITES", "colonne": "Comprehension_Consignes"},
        {"titre": "2. ANALYSE LOGISTIQUE : DISPONIBILITE DES OUTILS", "colonne": "Outils_Dispo"},
        {"titre": "3. IMPACT COGNITIF SUR LA COMPREHENSION THEORIQUE", "colonne": "Impact_Comprehension"},
        {"titre": "4. PERCEPTION ET ADEQUATION DE L'UTILITE CITOYENNE", "colonne": "Utilite_Citoyenne"}
    ]
    
    for axe in axes_analyse:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(27, 94, 32) 
        pdf.cell(0, 10, axe["titre"], ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)
        
        col = axe["colonne"]
        counts = df[col].value_counts()
        total = len(df)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(230, 240, 235)
        pdf.cell(85, 8, " Modalite de reponse", border=1, fill=True)
        pdf.cell(40, 8, "Effectif (Nbr)", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Pourcentage (%)", border=1, fill=True, align="C")
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 10)
        for val, count in counts.items():
            pct = (count / total) * 100
            pdf.cell(85, 8, f" {str(val)}", border=1)
            pdf.cell(40, 8, str(count), border=1, align="C")
            pdf.cell(45, 8, f"{pct:.1f} %", border=1, align="C")
            pdf.ln()
            
        pdf.ln(8)
        
        synthese = generer_synthese_axe(col, df)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "CRITIQUE ET AUDIT STATISTIQUE :", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, synthese["Critique"].encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "INTERPRETATION PEDAGOGIQUE ET REPERCUSSIONS :", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, synthese["Interpretation"].encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(46, 125, 50) 
        pdf.cell(0, 5, "AXES STRATEGIQUES DE REMEDIATION :", ln=True)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 5, synthese["Solution"].encode('latin-1', 'replace').decode('latin-1'))
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        if not counts.empty:
            plt.figure(figsize=(4.5, 2.2))
            plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, 
                    colors=['#2e7d32', '#ffb300', '#c62828', '#1565c0'][:len(counts)])
            plt.tight_layout()
            filename = f"temp_chart_{col}.png"
            plt.savefig(filename, dpi=200)
            plt.close()
            pdf.image(filename, x=60, y=pdf.get_y() + 2, w=90)
            os.remove(filename)
        
    return pdf.output()

# ==========================================
# NAVIGATION & DESIGN DES INTERFACES
# ==========================================
st.sidebar.title("📌 Menu de Navigation")
page = st.sidebar.radio("Aller vers :", ["📝 Formulaire Questionnaire", "📊 Espace Analyse & Reports"])

# --------------------------------------------------
# 1. INTERFACE FORMULAIRE QUESTIONNAIRE
# --------------------------------------------------
if page == "📝 Formulaire Questionnaire":
    st.markdown(
        """
        <div style="background-color: #f4fbf7; padding: 25px; border-radius: 10px; border-left: 6px solid #2e7d32; margin-bottom: 25px;">
            <h2 style="color: #1b5e20; margin-top: 0; font-family: 'Arial'; font-weight: bold;">EVALUATION PEDAGOGIQUE DES APPRENANTS</h2>
            <h5 style="color: #2e7d32; font-weight: bold; margin-top: 15px;">Avis sur les Dispositifs d'Exercices Pratiques</h5>
            <p style="color: #333333; font-style: italic; font-size: 14.5px;">
                Ce questionnaire vise à collecter vos retours d'expérience concernant les applications concrètes menées en Histoire-Géographie et Éducation à la Citoyenneté.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    with st.form("form_saisie", clear_on_submit=True):
        st.subheader("I. Profil Général de l'Apprenant")
        col1, col2 = st.columns(2)
        with col1:
            sexe = st.radio("1. Sexe :", ["Masculin", "Féminin"])
            classe = st.selectbox("2. Classe actuelle :", ["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"])
        with col2:
            etablissement = st.text_input("3. Établissement d'attache :", placeholder="Ex: LES PINTALKS")

        st.markdown("---")
        st.subheader("II. Diagnostic de l'Expérience Pratique")
        frequence = st.select_slider("1. Fréquence d'exposition :", options=["Jamais", "Rarement", "Parfois", "Souvent", "Toujours"])
        types_ex = st.multiselect("2. Nature des exercices :", ["Lecture de cartes", "Analyse d'un texte ou d'une image", "Travail en groupe", "Sorties ou enquêtes", "Jeux de rôle"])
        
        c1, c2, c3 = st.columns(3)
        with c1:
            consignes = st.radio("3. Clarté des consignes :", ["Oui, toujours", "Oui, parfois", "Non, pas vraiment"])
        with c2:
            outils = st.radio("4. Outils disponibles :", ["Oui", "Non"])
        with c3:
            impact = st.radio("5. Impact perçu :", ["Oui, beaucoup", "Oui, un peu", "Non, pas vraiment", "Pas du tout"])

        st.markdown("---")
        st.subheader("III. Enquêtes sur les Barrières d'Apprentissage")
        difficultes = st.multiselect("1. Contraintes identifiées :", ["Pas assez de matériel", "Pas assez de temps", "Le professeur ne donne pas assez d'explications", "Difficulté à travailler en groupe"])
        exemple = st.text_area("2. Exemple d'exercice complexe :")

        st.markdown("---")
        st.subheader("IV. Perspectives Stratégiques et Citoyenneté")
        attentes = st.multiselect("1. Attentes prioritaires :", ["Plus de matériel", "Plus d'explications", "Plus de temps"])
        citoyennete = st.radio("2. Utilité citoyenne :", ["Oui", "Non", "Je ne sais pas"])

        if st.form_submit_button("💾 Enregistrer la fiche d'évaluation"):
            if not etablissement:
                st.error("L'établissement doit être renseigné.")
            else:
                prochain_id = int(st.session_state.db_apprenants["ID"].max() + 1) if not st.session_state.db_apprenants.empty else 1
                nouvelle_reponse = {
                    "ID": prochain_id, "Sexe": sexe, "Classe": classe, "Etablissement": etablissement,
                    "Frequence_Ex": frequence, "Types_Ex": ", ".join(types_ex), "Comprehension_Consignes": consignes,
                    "Outils_Dispo": outils, "Impact_Comprehension": impact,
                    "Difficultes": ", ".join(difficultes), "Exemple_Exercice": exemple,
                    "Attentes_Prof": ", ".join(attentes), "Utilite_Citoyenne": citoyennete
                }
                st.session_state.db_apprenants = pd.concat([st.session_state.db_apprenants, pd.DataFrame([nouvelle_reponse])], ignore_index=True)
                st.success("Fiche indexée avec succès.")

# --------------------------------------------------
# 2. INTERFACE ANALYSE & CRITIQUE EXECUTIVE
# --------------------------------------------------
else:
    st.title("Analytique")
    df_app = st.session_state.db_apprenants

    if df_app.empty:
        st.info("💡 La base de données est actuellement vierge. Utilisez le Formulaire Questionnaire pour collecter vos premières fiches apprenants.")
    else:
        st.write("### ⚙️ Gestion et Modération des réponses")
        
        # Bouton Global pour TOUT vider d'un coup de manière transparente
        if st.button("🗑️ Vider l'intégralité de l'application (Démarrage à blanc)"):
            st.session_state.db_apprenants = pd.DataFrame(columns=df_app.columns)
            st.session_state.id_a_modifier = None
            st.success("Toutes les données ont été effacées définitivement.")
            st.rerun()
            
        st.markdown("---")

        # Liste des fiches disponibles basée de façon stricte sur l'état dynamique actuel
        liste_options = [f"ID: {row['ID']} - Genre: {row['Sexe']} ({row['Classe']} - {row['Etablissement']})" for _, row in df_app.iterrows()]
        
        # Sélection
        choix_apprenant = st.selectbox("Sélectionner une fiche élève à éditer ou supprimer :", liste_options, key="select_apprenant_key")
        
        if choix_apprenant:
            id_selectionne = int(choix_apprenant.split(" - ")[0].replace("ID: ", ""))
            ligne_apprenant = df_app[df_app["ID"] == id_selectionne].iloc[0]

            col_btn1, col_btn2, _ = st.columns([1, 1, 4])
            
            with col_btn1:
                if st.button("📝 Éditer les variables", key=f"edit_{id_selectionne}"):
                    st.session_state.id_a_modifier = id_selectionne
            
            with col_btn2:
                # La suppression force l'actualisation immédiate pour faire disparaître l'élément du selectbox
                if st.button("❌ Supprimer définitivement cette fiche", key=f"del_{id_selectionne}"):
                    st.session_state.db_apprenants = df_app[df_app["ID"] != id_selectionne].reset_index(drop=True)
                    if st.session_state.id_a_modifier == id_selectionne:
                        st.session_state.id_a_modifier = None
                    st.success(f"La fiche ID {id_selectionne} a bien été effacée.")
                    st.rerun()

            if st.session_state.id_a_modifier == id_selectionne:
                st.warning(f"Modification de la fiche ID {id_selectionne}")
                with st.form("form_modification"):
                    m_sexe = st.radio("Sexe :", ["Masculin", "Féminin"], index=["Masculin", "Féminin"].index(ligne_apprenant["Sexe"]))
                    m_classe = st.selectbox("Classe :", ["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"], index=["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"].index(ligne_apprenant["Classe"]))
                    m_etablissement = st.text_input("Établissement :", value=str(ligne_apprenant["Etablissement"]))
                    
                    opt_consignes = ["Oui, toujours", "Oui, parfois", "Non, pas vraiment"]
                    idx_cons = opt_consignes.index(ligne_apprenant["Comprehension_Consignes"]) if ligne_apprenant["Comprehension_Consignes"] in opt_consignes else 0
                    m_consignes = st.radio("Compréhension consignes :", opt_consignes, index=idx_cons)
                    
                    m_outils = st.radio("Outils disponibles :", ["Oui", "Non"], index=["Oui", "Non"].index(ligne_apprenant["Outils_Dispo"]))
                    m_impact = st.radio("Apport sur la compréhension :", ["Oui, beaucoup", "Oui, un peu", "Non, pas vraiment", "Pas du tout"], index=["Oui, beaucoup", "Oui, un peu", "Non, pas vraiment", "Pas du tout"].index(ligne_apprenant["Impact_Comprehension"]))
                    m_citoyennete = st.radio("Utilité citoyenne :", ["Oui", "Non", "Je ne sais pas"], index=["Oui", "Non", "Je ne sais pas"].index(ligne_apprenant["Utilite_Citoyenne"]))
                    
                    btn_maj1, btn_maj2 = st.columns(2)
                    with btn_maj1:
                        if st.form_submit_button("✅ Valider les modifications"):
                            idx = st.session_state.db_apprenants[st.session_state.db_apprenants["ID"] == id_selectionne].index[0]
                            st.session_state.db_apprenants.at[idx, "Sexe"] = m_sexe
                            st.session_state.db_apprenants.at[idx, "Classe"] = m_classe
                            st.session_state.db_apprenants.at[idx, "Etablissement"] = m_etablissement
                            st.session_state.db_apprenants.at[idx, "Comprehension_Consignes"] = m_consignes
                            st.session_state.db_apprenants.at[idx, "Outils_Dispo"] = m_outils
                            st.session_state.db_apprenants.at[idx, "Impact_Comprehension"] = m_impact
                            st.session_state.db_apprenants.at[idx, "Utilite_Citoyenne"] = m_citoyennete
                            
                            st.session_state.id_a_modifier = None
                            st.success("Données mises à jour avec succès.")
                            st.rerun()
                    with btn_maj2:
                        if st.form_submit_button(" Annuler"):
                            st.session_state.id_a_modifier = None
                            st.rerun()

        st.markdown("---")
        st.subheader("📥 Téléchargement du Rapport Global")
        try:
            pdf_output = generer_pdf_statistique(st.session_state.db_apprenants)
            st.download_button(
                label="📄 Télécharger le Rapport Analytique (PDF)",
                data=bytes(pdf_output),
                file_name="Rapport_Analytique.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erreur d'assemblage PDF : {e}")

        st.markdown("---")
        
        axe_vue = st.selectbox("Sélectionner l'axe didactique à inspecter :", 
                               ["Comprehension_Consignes", "Outils_Dispo", "Impact_Comprehension", "Utilite_Citoyenne"])
        
        df_stats = df_app[axe_vue].value_counts().reset_index()
        df_stats.columns = ["Modalité / Réponse Élève", "Effectif (Nbr)"]
        df_stats["Pourcentage (%)"] = (df_stats["Effectif (Nbr)"] / len(df_app)) * 100
        
        st.write("#### 📋 Répartition Documentaire")
        st.dataframe(df_stats.style.format({'Pourcentage (%)': '{:.1f} %'}), use_container_width=True)
        
        synthese_web = generer_synthese_axe(axe_vue, df_app)
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 5px solid #2e7d32; margin-top: 15px; margin-bottom: 25px;">
            <p><b>📝 CRITIQUE & DIAGNOSTIC :</b><br>{synthese_web['Critique']}</p>
            <p><b>🔍 INTERPRÉTATION EXÉCUTIVE :</b><br>{synthese_web['Interpretation']}</p>
            <p style="color: #1b5e20;"><b>💡 PROPOSITION DE REMÉDIATION :</b><br><i>{synthese_web['Solution']}</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        fig = px.pie(
            df_stats, 
            names="Modalité / Réponse Élève", 
            values="Effectif (Nbr)", 
            hole=0.3, 
            color_discrete_sequence=['#2e7d32', '#ffb300', '#c62828', '#1565c0']
        )
        st.plotly_chart(fig)
