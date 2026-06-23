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
    # Population initiale témoin anonymisée (sans Nom ni Prénom)
    st.session_state.db_apprenants = pd.DataFrame([
        {"ID": 1, "Sexe": "Masculin", "Classe": "1ère", "Etablissement": "LES PINTALKS", "Frequence_Ex": "Souvent", "Types_Ex": "Analyse d'un texte ou d'une image", "Comprehension_Consignes": "Oui, parfois", "Outils_Dispo": "Oui", "Impact_Comprehension": "Oui, beaucoup", "Difficultes": "Le professeur ne donne pas assez d'explications", "Attentes_Prof": "Plus d'explications", "Utilite_Citoyenne": "Je ne sais pas"},
        {"ID": 2, "Sexe": "Masculin", "Classe": "1ère", "Etablissement": "LES PINTALKS", "Frequence_Ex": "Souvent", "Types_Ex": "Analyse d'un texte ou d'une image", "Comprehension_Consignes": "Non, pas vraiment", "Outils_Dispo": "Non", "Impact_Comprehension": "Oui, un peu", "Difficultes": "Pas assez de matériel", "Attentes_Prof": "Plus de matériel", "Utilite_Citoyenne": "Oui"},
        {"ID": 3, "Sexe": "Féminin", "Classe": "1ère", "Etablissement": "LES PINTALKS", "Frequence_Ex": "Parfois", "Types_Ex": "Lecture de cartes", "Comprehension_Consignes": "Oui, parfois", "Outils_Dispo": "Oui", "Impact_Comprehension": "Oui, beaucoup", "Difficultes": "Le professeur ne donne pas assez d'explications", "Attentes_Prof": "Plus d'explications", "Utilite_Citoyenne": "Je ne sais pas"},
        {"ID": 4, "Sexe": "Masculin", "Classe": "Tle", "Etablissement": "LES PINTALKS", "Frequence_Ex": "Rarement", "Types_Ex": "Travail en groupe", "Comprehension_Consignes": "Non, pas vraiment", "Outils_Dispo": "Non", "Impact_Comprehension": "Pas du tout", "Difficultes": "Pas assez de matériel", "Attentes_Prof": "Plus de matériel", "Utilite_Citoyenne": "Non"}
    ])

if 'id_a_modifier' not in st.session_state:
    st.session_state.id_a_modifier = None

# =========================================================
# MOTEUR INTERPRÉTATIF GLOBAL INTELLIGENT
# =========================================================
def generer_synthese_axe(axe_colonne, df):
    total = len(df)
    counts = df[axe_colonne].value_counts()
    
    critique, interpretation, solution = "", "", ""
    
    if axe_colonne == "Comprehension_Consignes":
        mal_compris = counts.get("Non, pas vraiment", 0) + counts.get("Oui, parfois", 0)
        pct = (mal_compris / total) * 100 if total > 0 else 0
        critique = f"Il apparait que {pct:.1f}% des apprenants eprouvent des difficultes regulieres ou permanentes a assimiler les consignes des exercices pratiques."
        interpretation = "Cela traduit un decalage entre la formulation technico-pedagogique des consignes et le niveau d'autonomie cognitive reelle des eleves."
        solution = "Recommandation : Mettre en oeuvre une reformulation systematique a l'oral par un apprenant temoin et concevoir des fiches guides simplifiees pas-a-pas."
        
    elif axe_colonne == "Outils_Dispo":
        sans_outils = counts.get("Non", 0)
        pct = (sans_outils / total) * 100 if total > 0 else 0
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
        pct = (positif / total) * 100 if total > 0 else 0
        critique = f"Pour {pct:.1f}% des eleves, l'apport des exercices pratiques sur l'assimilation des cours theoriques reste indeniable."
        interpretation = "L'activite concrete ancre la memoire a long terme et donne du sens aux lecons theoriques d'Histoire-Geographie."
        solution = "Recommandation : Systematiser ces ateliers tout en ajustant le timing pour ne pas deborder sur les horaires de cours."

    elif axe_colonne == "Utilite_Citoyenne":
        flou = counts.get("Je ne sais pas", 0) + counts.get("Non", 0)
        pct = (flou / total) * 100 if total > 0 else 0
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
# NAVIGATION ET MENU PRINCIPAL (SIMPLIFIÉ)
# ==========================================
st.sidebar.title("📌 Menu de Navigation")
page = st.sidebar.radio("Aller vers :", ["📝 Formulaire Questionnaire", "📊 Espace Analyse & Rapports"])

# --------------------------------------------------
# 1. ESPACE ENQUÊTE (ANONYME)
# --------------------------------------------------
if page == "📝 Formulaire Questionnaire":
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
                Merci de répondre avec sincérité (Le questionnaire est totalement anonyme).
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    with st.form("form_saisie", clear_on_submit=True):
        st.subheader("I. Informations d'identification")
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
                    "ID": prochain_id, "Sexe": sexe, "Classe": classe, "Etablissement": etablissement,
                    "Frequence_Ex": frequence, "Types_Ex": ", ".join(types_ex), "Comprehension_Consignes": consignes,
                    "Outils_Dispo": outils, "Impact_Comprehension": impact,
                    "Difficultes": ", ".join(difficultes), "Exemple_Exercice": exemple,
                    "Attentes_Prof": ", ".join(attentes), "Utilite_Citoyenne": citoyennete
                }
                st.session_state.db_apprenants = pd.concat([st.session_state.db_apprenants, pd.DataFrame([nouvelle_reponse])], ignore_index=True)
                st.success("Données enregistrées anonymement avec succès.")

# --------------------------------------------------
# 2. ESPACE ANALYSE : GESTION, MODIFICATION ET SUPPRESSION
# --------------------------------------------------
else:
    st.title("📊 Tableau de Bord Consolidation Analytique")
    df_app = st.session_state.db_apprenants

    if df_app.empty:
        st.warning("La base de données est vide pour le moment.")
    else:
        st.write("### ⚙️ Gestion et Modération des réponses")
        
        liste_options = [f"ID: {row['ID']} - Genre: {row['Sexe']} ({row['Classe']} - {row['Etablissement']})" for _, row in df_app.iterrows()]
        choix_apprenant = st.selectbox("Sélectionner une fiche élève à éditer ou supprimer :", liste_options)
        
        if choix_apprenant:
            id_selectionne = int(choix_apprenant.split(" - ")[0].replace("ID: ", ""))
            ligne_apprenant = df_app[df_app["ID"] == id_selectionne].iloc[0]

            col_btn1, col_btn2, _ = st.columns([1, 1, 4])
            
            with col_btn1:
                if st.button("📝 Modifier", key=f"edit_{id_selectionne}"):
                    st.session_state.id_a_modifier = id_selectionne
            
            with col_btn2:
                if st.button("❌ Supprimer", key=f"del_{id_selectionne}"):
                    st.session_state.db_apprenants = df_app[df_app["ID"] != id_selectionne].reset_index(drop=True)
                    st.success(f"La fiche ID {id_selectionne} a été supprimée.")
                    st.rerun()

            if st.session_state.id_a_modifier == id_selectionne:
                st.warning(f"Modification en cours pour la fiche ID {id_selectionne}")
                
                with st.form("form_modification"):
                    m_sexe = st.radio("Sexe :", ["Masculin", "Féminin"], index=["Masculin", "Féminin"].index(ligne_apprenant["Sexe"]))
                    m_classe = st.selectbox("Classe :", ["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"], index=["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"].index(ligne_apprenant["Classe"]))
                    m_etablissement = st.text_input("Établissement :", value=str(ligne_apprenant["Etablissement"]))
                    
                    # Sécurisation des index par défaut
                    opt_consignes = ["Oui, toujours", "Oui, parfois", "Non, pas vraiment"]
                    idx_cons = opt_consignes.index(ligne_apprenant["Comprehension_Consignes"]) if ligne_apprenant["Comprehension_Consignes"] in opt_consignes else 0
                    m_consignes = st.radio("Compréhension consignes :", opt_consignes, index=idx_cons)
                    
                    m_outils = st.radio("Outils disponibles :", ["Oui", "Non"], index=["Oui", "Non"].index(ligne_apprenant["Outils_Dispo"]))
                    m_impact = st.radio("Apport sur la compréhension :", ["Oui, beaucoup", "Oui, un peu", "Non, pas vraiment", "Pas du tout"], index=["Oui, beaucoup", "Oui, un peu", "Non, pas vraiment", "Pas du tout"].index(ligne_apprenant["Impact_Comprehension"]))
                    m_citoyennete = st.radio("Utilité citoyenne :", ["Oui", "Non", "Je ne sais pas"], index=["Oui", "Non", "Je ne sais pas"].index(ligne_apprenant["Utilite_Citoyenne"]))
                    
                    btn_maj1, btn_maj2 = st.columns(2)
                    with btn_maj1:
                        if st.form_submit_button("✅ Sauvegarder les modifications"):
                            idx = st.session_state.db_apprenants[st.session_state.db_apprenants["ID"] == id_selectionne].index[0]
                            st.session_state.db_apprenants.at[idx, "Sexe"] = m_sexe
                            st.session_state.db_apprenants.at[idx, "Classe"] = m_classe
                            st.session_state.db_apprenants.at[idx, "Etablissement"] = m_etablissement
                            st.session_state.db_apprenants.at[idx, "Comprehension_Consignes"] = m_consignes
                            st.session_state.db_apprenants.at[idx, "Outils_Dispo"] = m_outils
                            st.session_state.db_apprenants.at[idx, "Impact_Comprehension"] = m_impact
                            st.session_state.db_apprenants.at[idx, "Utilite_Citoyenne"] = m_citoyennete
                            
                            st.session_state.id_a_modifier = None
                            st.success("Fiche mise à jour !")
                            st.rerun()
                    with btn_maj2:
                        if st.form_submit_button("❌ Annuler"):
                            st.session_state.id_a_modifier = None
                            st.rerun()

        st.markdown("---")

        # =========================================================
        # EXPORT ET RAPPORTS STATISTIQUES
        # =========================================================
        st.subheader("📥 Téléchargement du Rapport Global")
        try:
            pdf_output = generer_pdf_statistique(st.session_state.db_apprenants)
            st.download_button(
                label="📄 Télécharger le Rapport Analytique (PDF)",
                data=bytes(pdf_output),
                file_name="Rapport_Analytique_Anonyme.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erreur PDF : {e}")

        st.markdown("---")
        
        axe_vue = st.selectbox("Sélectionner l'axe didactique à inspecter :", 
                               ["Comprehension_Consignes", "Outils_Dispo", "Impact_Comprehension", "Utilite_Citoyenne"])
        
        df_stats = st.session_state.db_apprenants[axe_vue].value_counts().reset_index()
        df_stats.columns = ["Modalité / Réponse", "Effectif (Nbr)"]
        df_stats["Pourcentage (%)"] = (df_stats["Effectif (Nbr)"] / len(st.session_state.db_apprenants)) * 100
        
        st.write("#### 📅 Tableau de Répartition Statistique")
        st.dataframe(df_stats.style.format({'Pourcentage (%)': '{:.1f} %'}), use_container_width=True)
        
        # Injection sûre de la synthèse textuelle
        synthese_web = generer_synthese_axe(axe_vue, st.session_state.db_apprenants)
        st.markdown(f"""
        <div style="background-color: #f1f8e9; padding: 15px; border-radius: 5px; border-left: 4px solid #4caf50; margin-top: 10px; margin-bottom: 20px;">
            <p style="margin-bottom: 6px;"><b>📝 CRITIQUE & DIAGNOSTIC AUTOMATISÉ :</b><br>{synthese_web['Critique']}</p>
            <p style="margin-bottom: 6px;"><b>🔍 INTERPRÉTATION MÉTHODOLOGIQUE :</b><br>{synthese_web['Interpretation']}</p>
            <p style="margin-bottom: 0; color: #2e7d32;"><b>💡 PROPOSITION DE REMÉDIATION PÉDAGOGIQUE :</b><br><i>{synthese_web['Solution']}</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        fig = px.pie(df_stats, names="Modalité / Réponse", values="Effectif (Nbr)", hole=0.1, width=500, height=350)
        st.plotly_chart(fig)
