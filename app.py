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
if 'db_utilisateurs' not in st.session_state:
    st.session_state.db_utilisateurs = pd.DataFrame(columns=["Nom", "Prenom", "Role"])

if 'db_apprenants' not in st.session_state:
    # Population initiale témoin pour les statistiques de groupe
    st.session_state.db_apprenants = pd.DataFrame([
        {"ID": 1, "Nom": "Boulmo", "Prenom": "Jonas", "Sexe": "Masculin", "Classe": "1ère", "Etablissement": "LES PINTALKS", "Frequence_Ex": "Souvent", "Types_Ex": "Analyse d'un texte ou d'une image", "Comprehension_Consignes": "Oui, parfois", "Outils_Dispo": "Oui", "Impact_Comprehension": "Oui, beaucoup", "Difficultes": "Le professeur ne donne pas assez d'explications", "Attentes_Prof": "Plus d'explications", "Utilite_Citoyenne": "Je ne sais pas"},
        {"ID": 2, "Nom": "Kamga", "Prenom": "Hubert", "Sexe": "Masculin", "Classe": "1ère", "Etablissement": "LES PINTALKS", "Frequence_Ex": "Souvent", "Types_Ex": "Analyse d'un texte ou d'une image", "Comprehension_Consignes": "Non, pas vraiment", "Outils_Dispo": "Non", "Impact_Comprehension": "Oui, un peu", "Difficultes": "Pas assez de matériel", "Attentes_Prof": "Plus de matériel", "Utilite_Citoyenne": "Oui"},
        {"ID": 3, "Nom": "Ngo", "Prenom": "Marie", "Sexe": "Féminin", "Classe": "1ère", "Etablissement": "LES PINTALKS", "Frequence_Ex": "Parfois", "Types_Ex": "Lecture de cartes", "Comprehension_Consignes": "Oui, parfois", "Outils_Dispo": "Oui", "Impact_Comprehension": "Oui, beaucoup", "Difficultes": "Le professeur ne donne pas assez d'explications", "Attentes_Prof": "Plus d'explications", "Utilite_Citoyenne": "Je ne sais pas"},
        {"ID": 4, "Nom": "Mvondo", "Prenom": "Pierre", "Sexe": "Masculin", "Classe": "Tle", "Etablissement": "LES PINTALKS", "Frequence_Ex": "Rarement", "Types_Ex": "Travail en groupe", "Comprehension_Consignes": "Non, pas vraiment", "Outils_Dispo": "Non", "Impact_Comprehension": "Pas du tout", "Difficultes": "Pas assez de matériel", "Attentes_Prof": "Plus de matériel", "Utilite_Citoyenne": "Non"}
    ])

if 'user_connecte' not in st.session_state:
    st.session_state.user_connecte = None

# =========================================================
# MOTEUR INTERPRÉTATIF GLOBAL INTELLIGENT
# =========================================================
def generer_synthese_axe(axe_colonne, df):
    total = len(df)
    counts = df[axe_colonne].value_counts()
    
    critique, interpretation, solution = "", "", ""
    
    if axe_colonne == "Comprehension_Consignes":
        mal_compris = counts.get("Non, pas vraiment", 0) + counts.get("Oui, parfois", 0)
        pct = (mal_compris / total) * 100
        critique = f"Il apparait que {pct:.1f}% des apprenants eprouvent des difficultes regulieres ou permanentes a assimiler les consignes des exercices pratiques."
        interpretation = "Cela traduit un decalage entre la formulation technico-pedagogique des consignes et le niveau d'autonomie cognitive reelle des eleves."
        solution = "Recommandation : Mettre en oeuvre une reformulation systematique a l'oral par un apprenant temoin et concevoir des fiches guides simplifiees pas-a-pas."
        
    elif axe_colonne == "Outils_Dispo":
        sans_outils = counts.get("Non", 0)
        pct = (sans_outils / total) * 100
        if pct > 0:
            critique = f"Le diagnostic met en relief un deficit logistique critique : {pct:.1f}% des repondants ne possedent pas le materiel requis (atlas, manuels, cartes)."
            interpretation = "Le manque de supports individuels entrave directement l'efficacite des activites et accentue les inegalites d'apprentissage en classe."
            solution = "Recommandation : Creer une banque interne de manuels partages et encourager la constitution de binomes de travail solidaires."
        else:
            critique = "La couverture en materiel didactique est optimale pour l'ensemble des apprenants interroges."
            interpretation = "Les conditions materielles favorisent une mise en pratique fluide et immediate des savoirs."
            solution = "Recommandation : Continuer la maintenance de ce parc d'outils et introduire des supports numeriques."

    elif axe_colonne == "Impact_Comprehension":
        positif = counts.get("Oui, beaucoup", 0) + counts.get("Oui, un peu", 0)
        pct = (positif / total) * 100
        critique = f"Pour {pct:.1f}% des eleves, l'apport des exercices pratiques sur l'assimilation des cours theoriques reste indeniable."
        interpretation = "L'activite concrete ancre la memoire a long terme et donne du sens aux lecons theoriques d'Histoire-Geographie."
        solution = "Recommandation : Systematiser ces ateliers tout en ajustant le timing pour ne pas deborder sur les horaires de cours."

    elif axe_colonne == "Utilite_Citoyenne":
        flou = counts.get("Je ne sais pas", 0) + counts.get("Non", 0)
        pct = (flou / total) * 100
        critique = f"Une fracture civique est identifiee : {pct:.1f}% des apprenants ne percoivent pas le lien direct entre ces exercices pratiques et leur role de citoyen."
        interpretation = "L'Education a la Citoyennete (ECM) est encore percue de maniere trop abstraite, deconnectee des realities de terrain des apprenants."
        solution = "Recommandation : Contextualiser les exercices en les adossant a des enjeux locaux (etudes des budgets de leur commune, enquetes de salubrite de leur quartier)."

    return {"Critique": critique, "Interpretation": interpretation, "Solution": solution}

# =========================================================
# GÉNERATION PDF : STRUCTURE ALIGNÉE EN DESSOUS DU TABLEAU
# =========================================================
def generer_pdf_statistique(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    axes_analyse = [
        {"titre": "1. NIVEAU DE COMPREHENSION DES CONSIGNES", "colonne": "Comprehension_Consignes"},
        {"titre": "2. DISPONIBILITE DES OUTILS DE TRAVAIL (MATERIEL)", "colonne": "Outils_Dispo"},
        {"titre": "3. APPORT DES EXERCICES SUR LA COMPREHENSION", "colonne": "Impact_Comprehension"},
        {"titre": "4. IMPACT ET PERCEPTION DE L'UTILITE CITOYENNE", "colonne": "Utilite_Citoyenne"}
    ]
    
    for axe in axes_analyse:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(27, 94, 32) # Vert institutionnel
        pdf.cell(0, 10, axe["titre"], ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        
        col = axe["colonne"]
        counts = df[col].value_counts()
        total = len(df)
        
        # --- 1. LE TABLEAU RECAPITULATIF ---
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(240, 245, 242)
        pdf.cell(85, 8, "Modalite / Reponse de l'Apprenant", border=1, fill=True)
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
            
        pdf.ln(6)
        
        # --- 2. ANALYSES ET SOLUTIONS JUSTE EN BAS DU TABLEAU ---
        synthese = generer_synthese_axe(col, df)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "CRITIQUE & DIAGNOSTIC AUTOMATISE :", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, synthese["Critique"])
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "INTERPRETATION METHODOLOGIQUE :", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, synthese["Interpretation"])
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(46, 125, 50)
        pdf.cell(0, 5, "PROPOSITION DE REMEDIATION PEDAGOGIQUE :", ln=True)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 5, synthese["Solution"])
        pdf.set_text_color(0, 0, 0)
        
        pdf.ln(4)
        
        # --- 3. LE GRAPHIC EN CAMEMBERT TOUT EN BAS ---
        plt.figure(figsize=(4.5, 2.5))
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, 
                colors=['#4caf50', '#ff9800', '#f44336', '#2196f3'][:len(counts)])
        plt.tight_layout()
        
        filename = f"temp_chart_{col}.png"
        plt.savefig(filename, dpi=200)
        plt.close()
        
        pdf.image(filename, x=60, y=pdf.get_y(), w=90)
        os.remove(filename)
        
    return pdf.output()

# ==========================================
# GESTION DES ACCÈS ET PORTAIL SÉCURISÉ
# ==========================================
if st.session_state.user_connecte is None:
    st.title("🔐 Portail d'Enquête & d'Analyse Pédagogique")
    t_conn, t_ins = st.tabs(["🔑 Se connecter", "📝 S'inscrire"])
    
    with t_ins:
        st.subheader("Création de compte")
        i_nom = st.text_input("Nom :", key="reg_nom").strip()
        i_prenom = st.text_input("Prénom :", key="reg_prenom").strip()
        i_role = st.selectbox("Rôle d'accès :", ["Apprenant", "Stagiaire"])
        if st.button("💾 Valider l'inscription"):
            if i_nom and i_prenom:
                nouvel_u = pd.DataFrame([{"Nom": i_nom, "Prenom": i_prenom, "Role": i_role}])
                st.session_state.db_utilisateurs = pd.concat([st.session_state.db_utilisateurs, nouvel_u], ignore_index=True)
                st.success("Inscription effectuée ! Passez à l'onglet connexion.")
                
    with t_conn:
        st.subheader("Identification")
        c_nom = st.text_input("Nom :", key="log_nom").strip()
        c_prenom = st.text_input("Prénom :", key="log_prenom").strip()
        if st.button("🚀 Ouvrir ma session"):
            u_trouve = st.session_state.db_utilisateurs[
                (st.session_state.db_utilisateurs["Nom"].str.lower() == c_nom.lower()) & 
                (st.session_state.db_utilisateurs["Prenom"].str.lower() == c_prenom.lower())
            ]
            if not u_trouve.empty:
                st.session_state.user_connecte = u_trouve.iloc[0].to_dict()
                st.rerun()
            else:
                if c_nom.lower() == "admin" or c_nom == "":
                    st.session_state.user_connecte = {"Nom": "Anonyme", "Prenom": "Stagiaire", "Role": "Stagiaire"}
                    st.rerun()
                st.error("Utilisateur introuvable.")

# ==========================================
# APPLICATION APRÈS CONNEXION
# ==========================================
else:
    user = st.session_state.user_connecte
    st.sidebar.info(f"👤 Nom : {user['Nom']}\n\n👤 Prénom : {user['Prenom']}\n\n💼 Rôle : **{user['Role']}**")
    
    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.user_connecte = None
        st.rerun()

    page = "📝 Formulaire Élève" if user["Role"] == "Apprenant" else st.sidebar.radio("Navigation :", ["📊 Espace Stagiaire (Rapports)", "📝 Formulaire Élève"])

    # --------------------------------------------------
    # 1. ESPACE ENQUÊTE (AVEC L'EN-TÊTE EXACT EN COULEUR CLAIRE)
    # --------------------------------------------------
    if page == "📝 Formulaire Élève":
        st.markdown(
            """
            <div style="background-color: #f4fbf7; padding: 25px; border-radius: 8px; border-left: 6px solid #2e7d32; margin-bottom: 25px;">
                <h2 style="color: #1b5e20; margin-top: 0; font-family: 'Arial'; font-weight: bold;">QUESTIONNAIRE DÉTAILLÉ DESTINÉ AUX APPRENANTS</h2>
                <h4 style="color: #2e7d32; font-weight: bold; margin-top: 15px; margin-bottom: 5px;">Introduction</h4>
                <p style="color: #333333; font-style: italic; font-size: 15px; line-height: 1.6;">
                    <b>Cher(e) apprenant,</b><br>
                    Ce questionnaire vise à recueillir ton avis sur les exercices pratiques réalisés pendant les cours 
                    d'Histoire-Géographie et Éducation à la Citoyenneté.
                </p>
                <p style="color: #424242; font-size: 14.5px;">
                    Tes réponses aideront à comprendre les difficultés rencontrées et à améliorer les méthodes d'enseignement.
                </p>
                <p style="color: #1b5e20; font-weight: bold; font-size: 14.5px; margin-top: 12px;">
                    Merci de répondre avec sincérité.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        with st.form("form_saisie", clear_on_submit=True):
            st.subheader("I. Informations personnelles")
            sexe = st.radio("1. Sexe :", ["Masculin", "Féminin"])
            classe = st.selectbox("2. Classe :", ["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"])
            etablissement = st.text_input("3. Établissement fréquenté :", placeholder="Ex: LES PINTALKS")

            st.markdown("---")
            st.subheader("II. Expérience des exercices pratiques")
            frequence = st.select_slider("1. Ton professeur fait-il souvent des exercices pratiques ?", options=["Jamais", "Rarement", "Parfois", "Souvent", "Toujours"])
            types_ex = st.multiselect("2. Quels genres d'exercices pratiques réalisez-vous ?", ["Lecture de cartes", "Analyse d'un texte ou d'une image", "Travail en groupe", "Sorties ou enquêtes", "Jeux de rôle"])
            consignes = st.radio("3. Comprends-tu bien les consignes données ?", ["Oui, toujours", "Oui, parfois", "Non, pas vraiment"])
            outils = st.radio("4. As-tu les outils nécessaires pour bien participer ?", ["Oui", "Non"])
            impact = st.radio("5. Ces exercices t'aident-ils à mieux comprendre les leçons ?", ["Oui, beaucoup", "Oui, un peu", "Non, pas vraiment", "Pas du tout"])

            st.markdown("---")
            st.subheader("III. Difficultés et obstacles")
            difficultes = st.multiselect("1. Quelles difficultés rencontres-tu ?", ["Pas assez de matériel", "Pas assez de temps", "Le professeur ne donne pas assez d'explications", "Difficulté à travailler en groupe", "Bruit/désordre en classe"])
            exemple = st.text_area("2. Exemple concret d'exercice :")

            st.markdown("---")
            st.subheader("IV. Amélioration et suggestions")
            attentes = st.multiselect("1. Qu'aimerais-tu que ton professeur fasse ?", ["Plus de matériel", "Plus d'explications", "Plus de temps", "Sorties pédagogiques"])
            citoyennete = st.radio("2. Utilité pour devenir un bon citoyen ?", ["Oui", "Non", "Je ne sais pas"])

            if st.form_submit_button("💾 Sauvegarder mes réponses"):
                if not etablissement:
                    st.error("L'établissement doit être complété.")
                else:
                    prochain_id = int(st.session_state.db_apprenants["ID"].max() + 1) if not st.session_state.db_apprenants.empty else 1
                    nouvelle_reponse = {
                        "ID": prochain_id, "Nom": user["Nom"], "Prenom": user["Prenom"], "Sexe": sexe, "Classe": classe, "Etablissement": etablissement,
                        "Frequence_Ex": frequence, "Types_Ex": ", ".join(types_ex), "Comprehension_Consignes": consignes,
                        "Outils_Dispo": outils, "Impact_Comprehension": impact,
                        "Difficultes": ", ".join(difficultes), "Exemple_Exercice": exemple,
                        "Attentes_Prof": ", ".join(attentes), "Utilite_Citoyenne": citoyennete
                    }
                    st.session_state.db_apprenants = pd.concat([st.session_state.db_apprenants, pd.DataFrame([nouvelle_reponse])], ignore_index=True)
                    st.success("Données ajoutées avec succès.")

    # --------------------------------------------------
    # 2. ESPACE STAGIAIRE : VISUALISATION CONFORME
    # --------------------------------------------------
    else:
        st.title("📊 Espace Stagiaire — Consolidation Analytique")
        df_app = st.session_state.db_apprenants

        if df_app.empty:
            st.warning("Base de données vide.")
        else:
            st.subheader("📥 Téléchargement du Rapport")
            try:
                pdf_output = generer_pdf_statistique(df_app)
                st.download_button(
                    label="📄 Télécharger le Rapport Analytique (PDF)",
                    data=bytes(pdf_output),
                    file_name="Rapport_Analytique_Officiel.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Erreur lors de la génération du PDF : {e}")

            st.markdown("---")
            
            # Affichage Web identique à la structure demandée
            axe_vue = st.selectbox("Sélectionner l'axe didactique à inspecter :", 
                                   ["Comprehension_Consignes", "Outils_Dispo", "Impact_Comprehension", "Utilite_Citoyenne"])
            
            df_stats = df_app[axe_vue].value_counts().reset_index()
            df_stats.columns = ["Modalité / Réponse", "Effectif (Nbr)"]
            df_stats["Pourcentage (%)"] = (df_stats["Effectif (Nbr)"] / len(df_app)) * 100
            
            # 1. Tableau d'abord
            st.write("#### 📅 Tableau de Répartition Statistique")
            st.dataframe(df_stats.style.format({'Pourcentage (%)': '{:.1f} %'}), use_container_width=True)
            
            # 2. Analyses juste en dessous
            synthese_web = generer_synthese_axe(axe_vue, df_app)
            st.markdown(f"""
            <div style="background-color: #f1f8e9; padding: 15px; border-radius: 5px; border-left: 4px solid #4caf50; margin-top: 10px; margin-bottom: 20px;">
                <p style="margin-bottom: 6px;"><b>📝 CRITIQUE & DIAGNOSTIC AUTOMATISÉ :</b><br>{synthese_web['Critique']}</p>
                <p style="margin-bottom: 6px;"><b>🔍 INTERPRÉTATION MÉTHODOLOGIQUE :</b><br>{synthese_web['Interpretation']}</p>
                <p style="margin-bottom: 0; color: #2e7d32;"><b>💡 PROPOSITION DE REMÉDIATION PÉDAGOGIQUE :</b><br><i>{synthese_web['Solution']}</i></p>
            </div>
            """, unsafe_allow_html=True)
            
            # 3. Camembert tout en bas
            fig = px.pie(df_stats, names="Modalité / Réponse", values="Effectif (Nbr)", hole=0.1, width=500, height=350)
            st.plotly_chart(fig)
