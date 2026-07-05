import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import os
import uuid
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="EduAnalyse Pro - Histoire-Géo & Éducation à la Citoyenneté",
    page_icon="🎓",
    layout="wide"
)

DB_FILE = "data_collecte.csv"

# --- FONCTIONS DE GESTION DE LA BASE DE DONNÉES ---
def charger_donnees():
    if os.path.isfile(DB_FILE):
        df = pd.read_csv(DB_FILE, encoding='utf-8')
        # S'assurer que la colonne ID existe pour les anciens enregistrements
        if "ID" not in df.columns:
            df.insert(0, "ID", [str(uuid.uuid4())[:8] for _ in range(len(df))])
            df.to_csv(DB_FILE, index=False, encoding='utf-8')
        return df
    return pd.DataFrame()

def sauvegarder_toutes_donnees(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8')

def sauvegarder_nouvel_apprenant(dict_data):
    dict_data["ID"] = str(uuid.uuid4())[:8]  # Génère un identifiant court unique
    dict_data["Date_Enregistrement"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_new = pd.DataFrame([dict_data])
    
    if not os.path.isfile(DB_FILE):
        df_new.to_csv(DB_FILE, index=False, encoding='utf-8')
    else:
        # Réorganiser les colonnes pour correspondre si le fichier existe déjà
        df_existing = pd.read_csv(DB_FILE, encoding='utf-8')
        df_new = df_new.reindex(columns=df_existing.columns)
        df_new.to_csv(DB_FILE, mode='a', header=False, index=False, encoding='utf-8')

# =========================================================
# MOTEUR DE GÉNÉRATION DU RAPPORT PDF PROFESSIONNEL (FPDF)
# =========================================================
class PDFRapportMemoire(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, "Rapport d'Analyse Statistique et Critique - Memoire Universitaire", ln=True, align="R")
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def generer_pdf_academique(df, total_fiches, sans_outils_pct, mauvaise_comp_pct, toujours_frequence_pct):
    pdf = PDFRapportMemoire()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PAGE DE GARDE INSTITUTIONNELLE ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 20, "RAPPORT D'ANALYSE SCIENTIFIQUE ET DIAGNOSTIC PÉDAGOGIQUE", ln=True, align="C")
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 10, "Valorisation de l'Enseignement de l'Histoire-Geographie et Education a la Citoyennete", ln=True, align="C")
    
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, "Document de recherche appliquee pour memoire de fin d'etudes universitaire", ln=True, align="R")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # 1. Introduction
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, "1. INTRODUCTION ET CADRE METHODOLOGIQUE", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    intro_txt = (
        f"Ce rapport compile, traite et analyse scientifiquement les donnees brutes issues des fiches d'evaluation "
        f"completees anonymement par les apprenants. L'objectif de cette demarche empirique est de mesurer avec precision "
        f"l'impact des exercices pratiques sur la transposition didactique et l'assimilation cognitive des notions de cours.\n\n"
        f"Taille de l'echantillon d'etude actuel : {total_fiches} fiches apprenants valides et enregistrees en base de donnees."
    )
    pdf.multi_cell(0, 5, intro_txt)
    pdf.ln(10)
    
    # 2. Tableau Statistique
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, "2. TABLEAU SYNTHETIQUE DES VARIABLES CLES DE L'APPRENTISSAGE", ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(237, 242, 247)
    pdf.cell(100, 8, " Indicateur Pedagogique Evalue", border=1, fill=True)
    pdf.cell(40, 8, " Proportion (%)", border=1, fill=True, align="C")
    pdf.cell(50, 8, " Seuil de Vigilance", border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(100, 8, " Manque d'outils necessaires (livres, atlas, cartes...)", border=1)
    pdf.cell(40, 8, f" {sans_outils_pct:.1f} %", border=1, align="C")
    pdf.cell(50, 8, " Alerte critique si > 30%", border=1, align="C")
    pdf.ln()
    
    pdf.cell(100, 8, " Difficulte severe a decoder les consignes", border=1)
    pdf.cell(40, 8, f" {mauvaise_comp_pct:.1f} %", border=1, align="C")
    pdf.cell(50, 8, " Alerte critique si > 25%", border=1, align="C")
    pdf.ln()
    
    pdf.cell(100, 8, " Pratique continue des ateliers (Toujours)", border=1)
    pdf.cell(40, 8, f" {toujours_frequence_pct:.1f} %", border=1, align="C")
    pdf.cell(50, 8, " Objectif Valorisation > 50%", border=1, align="C")
    pdf.ln()
    
    pdf.ln(10)
    
    # 3. Interprétation et critique
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, "3. INTERPRETATION ANALYTIQUE ET DISCUSSIONS CRITIQUES", ln=True)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 6, "A. Analyse descriptive des variables materielles :", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    interp_mat = (
        f"L'analyse statistique met en exergue que {sans_outils_pct:.1f}% des apprenants declarent evoluer "
        f"sans supports de travail individuels. En sciences de l'education, l'absence d'outils cartographiques et textuels "
        f"cree une rupture epistemologique majeure. L'enseignement se rigidifie sous une forme passive et exclusivement "
        f"theorique, restreignant la construction de reperes spatio-temporels autonomes chez l'eleve."
    )
    pdf.multi_cell(0, 5, interp_mat)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(43, 108, 176)
    pdf.cell(0, 6, "B. Critique didactique des pratiques d'evaluation :", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    interp_ped = (
        f"L'indice d'incomprehension s'etablit a {mauvaise_comp_pct:.1f}%. Ce resultat atteste d'un ecart lexical significatif "
        f"entre le niveau d'encodage des consignes de l'enseignant et les structures cognitives de decodage de l'apprenant. "
        f"Une consigne opaque neutralise l'efficacite de la situation-probleme, devie l'exercice de son but formatif "
        f"et entraine un decrochage progressif de l'apprenant vis-a-vis de la matiere."
    )
    pdf.multi_cell(0, 5, interp_ped)
    pdf.ln(10)
    
    # 4. Recommandations
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, "4. STRATEGIES ACADEMIQUES DE RECONVERSION ET REMEDIATION", ln=True)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(34, 84, 61)
    pdf.cell(0, 6, "[Pour le Corps Enseignant]", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, "- Sequençage systematique : Fragmenter les enonces d'exercices complexes en sous-taches explicites.\n- Mutualisation Logistique : Initier des ateliers a supports partages (binomes solidaires avec atlas central).")
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(34, 84, 61)
    pdf.cell(0, 6, "[Pour les Apprenants]", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, "- Pratique active du questionnement : Solliciter une verbalisation alternative de la part du professeur des le debut de l'exercice.\n- Entraide intra-muros : Partager activement les manuels disponibles dans les groupes d'etude.")
    
    # --- PAGE SUIVANTE : ANNEXE DES DONNÉES BRUTES ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, "5. ANNEXE ACADEMIQUE : REGISTRE INTEGRAL DES DONNEES BRUTES", ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "Liste exhaustive des fiches traitees et comptabilisees dans l'etude :", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(12, 6, "ID", border=1, fill=True)
    pdf.cell(15, 6, "Genre", border=1, fill=True)
    pdf.cell(15, 6, "Classe", border=1, fill=True)
    pdf.cell(35, 6, "Etablissement", border=1, fill=True)
    pdf.cell(25, 6, "Freq. Ex", border=1, fill=True)
    pdf.cell(20, 6, "Compreh.", border=1, fill=True)
    pdf.cell(15, 6, "Outils", border=1, fill=True)
    pdf.cell(30, 6, "Aide Lecon", border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 7.5)
    for _, row in df.iterrows():
        id_app = str(row.get('ID', ''))
        etab = str(row.get('Etablissement', ''))[:20]
        freq = str(row.get('Frequence_Ex', ''))
        comp = str(row.get('Comprehension', ''))
        out = str(row.get('Outils', ''))
        aide = str(row.get('Aide_Lecon', ''))
        
        pdf.cell(12, 6, id_app, border=1)
        pdf.cell(15, 6, str(row.get('Sexe', '')), border=1)
        pdf.cell(15, 6, str(row.get('Classe', '')), border=1)
        pdf.cell(35, 6, etab, border=1)
        pdf.cell(25, 6, freq, border=1)
        pdf.cell(20, 6, comp, border=1)
        pdf.cell(15, 6, out, border=1)
        pdf.cell(30, 6, aide, border=1)
        pdf.ln()
        
    pdf_bytes = pdf.output()
    if isinstance(pdf_bytes, (bytes, bytearray)):
        return bytes(pdf_bytes)
    return pdf_bytes.encode('latin1', errors='replace')

# --- BARRE LATÉRALE DE NAVIGATION ---
st.sidebar.title("🎓 EduAnalyse Mémoire Pro")
menu = st.sidebar.radio("Navigation", [
    "📝 Enregistrement des Données (Fiche)", 
    "📊 Dashboard & Recommandations IA",
    "⚙️ Gestion des Fiches (Modifier/Supprimer)"
])

# ==========================================
# 1. OPTION : ENREGISTREMENT D'UNE FICHE APPRENANT
# ==========================================
if menu == "📝 Enregistrement des Données (Fiche)":
    st.title("📋 Questionnaire Détaillé destiné aux Apprenants")
    st.markdown("**Introduction** : Cher(e) apprenant. Ce questionnaire vise à recueillir ton avis sur les exercices pratiques réalisés pendant les cours d'Histoire-Géographie et Éducation à la Citoyenneté.")
    st.write("---")
    
    with st.form("form_strict", clear_on_submit=True):
        st.subheader("I. Informations personnelles")
        col1, col2 = st.columns(2)
        with col1:
            sexe = st.radio("1. Sexe :", ["Masculin", "Féminin"])
            classe = st.radio("2. Classe :", ["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"])
        with col2:
            etablissement = st.text_input("3. Établissement fréquenté :", value="LES PINTALKS")
            
        st.write("---")
        st.subheader("II. Expérience des exercices pratiques")
        frequence_ex = st.radio("1. Ton professeur fait-il souvent des exercices pratiques pendant les cours ?", 
                                ["Toujours", "Souvent", "Parfois", "Rarement", "Jamais"])
        
        genres_ex = st.multiselect("2. Quels genres d'exercices pratiques réalisez-vous ?",
                                   ["Lecture de cartes", "Analyse d'un texte ou d'une image", "Travail en groupe", "Sorties ou enquêtes", "Jeux de rôle"])
        autre_genre = st.text_input("Autre :")
        
        comprehension = st.radio("3. Comprends-tu bien les consignes données lors de ces exercices ?", ["Oui toujours", "Oui parfois", "Non pas vraiment"])
        outils = st.radio("4. As-tu les outils nécessaires pour bien participer (livres, atlas, cahier, carte, etc.) ?", ["Oui", "Non"])
        aide_lecon = st.radio("5. Ces exercices t'aident-ils à mieux comprendre les leçons ?", ["Oui beaucoup", "Oui un peu", "Non vraiment", "Pas du tout"])
        
        st.write("---")
        st.subheader("III. Difficultés et obstacles")
        difficultes = st.multiselect("1. Quelles difficultés rencontres-tu pendant ces exercices ?",
                                     ["Pas assez de matériel", "Pas assez de temps", "Le professeur ne donne pas assez d'explications", "Difficulté à travailler en groupe", "Bruit/désordre en classe"])
        autre_diff = st.text_input("Autres :")
        exemple_ex = st.text_area("2. Donne un exemple d'exercice pratique que tu as aimé ou pas aimé, et pourquoi")
        
        st.write("---")
        st.subheader("IV. Amélioration et suggestions")
        suggestions = st.multiselect("1. Qu'aimerais-tu que ton professeur fasse pour améliorer ces exercices ?",
                                     ["Plus de matériel", "Plus d'explications", "Plus de temps", "Sorties pédagogiques"])
        autre_sug = st.text_input("Autre")
        utilite_citoyen = st.radio("2. Selon toi, les exercices pratiques sont-ils utiles pour devenir un bon citoyen ?", ["Oui", "Non", "Je ne sais pas"])
        
        submit = st.form_submit_button("💾 Enregistrer les informations")
        
        if submit:
            data = {
                "Sexe": sexe, "Classe": classe, "Etablissement": etablissement.upper(),
                "Frequence_Ex": frequence_ex, "Genres_Ex": ", ".join(genres_ex), "Autre_Genre": autre_genre,
                "Comprehension": comprehension, "Outils": outils, "Aide_Lecon": aide_lecon,
                "Difficultes": ", ".join(difficultes), "Autre_Diff": autre_diff, "Exemple_Texte": exemple_ex,
                "Suggestions": ", ".join(suggestions), "Autre_Sug": autre_sug, "Utilite_Citoyen": utilite_citoyen
            }
            sauvegarder_nouvel_apprenant(data)
            st.success("🎉 Les informations de la fiche ont été correctement archivées.")

# ==========================================
# 2. OPTION : DASHBOARD & EXPORT PDF
# ==========================================
elif menu == "📊 Dashboard & Recommandations IA":
    st.title("📊 Laboratoire Empirique : Tableau de Bord & Recommandations IA")
    st.caption("Espace unifié combinant l'analyse statistique, la critique interprétative et l'option d'exportation pour le mémoire.")
    st.write("---")
    
    df = charger_donnees()
    
    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Veuillez enregistrer une fiche d'évaluation pour activer les analyses.")
    else:
        total_fiches = len(df)
        sans_outils_pct = (df["Outils"] == "Non").sum() / total_fiches * 100
        mauvaise_comp_pct = (df["Comprehension"] == "Non pas vraiment").sum() / total_fiches * 100
        toujours_frequence_pct = (df["Frequence_Ex"] == "Toujours").sum() / total_fiches * 100
        
        st.subheader("📥 Génération du Rapport Officiel de Mémoire")
        try:
            pdf_data = generer_pdf_academique(df, total_fiches, sans_outils_pct, mauvaise_comp_pct, toujours_frequence_pct)
            st.download_button(
                label="📄 Télécharger le Rapport d'Analyse Exhaustif (PDF)",
                data=pdf_data,
                file_name="Rapport_Academique_Histoire_Geo_Apprenants.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF : {e}")
            
        st.write("---")
        st.subheader("🔬 Analyse Graphique Descriptive et Discussion Critique")
        
        col_gauche, col_droite = st.columns(2)
        with col_gauche:
            st.markdown("#### Figure 1 : Répartition selon la possession des outils")
            fig1 = px.pie(df, names="Outils", color="Outils", color_discrete_map={"Oui": "#3182CE", "Non": "#E53E3E"}, hole=0.3)
            st.plotly_chart(fig1, use_container_width=True)
        with col_droite:
            st.markdown("#### Figure 2 : Sentiment d'incompréhension des consignes")
            fig2 = px.histogram(df, x="Comprehension", color="Comprehension", color_discrete_map={"Oui toujours": "#A0AEC0", "Oui parfois": "#718096", "Non pas vraiment": "#4A5568"})
            st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 3. NOUVELLE OPTION : GESTION DES FICHES (MODIFIER / SUPPRIMER)
# ==========================================
elif menu == "⚙️ Gestion des Fiches (Modifier/Supprimer)":
    st.title("⚙️ Administration et Modération des Données")
    st.caption("Sélectionne la fiche d'un apprenant à l'aide de son identifiant unique pour appliquer des modifications ou la supprimer définitivement.")
    st.write("---")
    
    df = charger_donnees()
    
    if df.empty:
        st.warning("⚠️ La base de données est actuellement vide. Aucun profil apprenant disponible pour modification ou suppression.")
    else:
        # Affichage du tableau global pour repérer les ID
        st.subheader("📋 Liste complète des fiches enregistrées")
        st.dataframe(df[["ID", "Sexe", "Classe", "Etablissement", "Frequence_Ex", "Comprehension", "Outils"]])
        
        st.write("---")
        st.subheader("🛠️ Action sur une fiche")
        
        # Sélection de l'apprenant cible par son ID
        liste_ids = df["ID"].tolist()
        id_selectionne = st.selectbox("Choisir l'identifiant (ID) de l'apprenant à traiter :", liste_ids)
        
        # Récupération de la ligne correspondante
        index_ligne = df[df["ID"] == id_selectionne].index[0]
        row_data = df.loc[index_ligne]
        
        # Choix de l'action
        action = st.radio("Action requise :", ["Modifier les informations", "Supprimer la fiche"], horizontal=True)
        
        if action == "Modifier les informations":
            st.info(f"Formulaire d'édition pour la fiche ID : **{id_selectionne}**")
            
            # Reconstruction du formulaire pré-rempli avec les valeurs actuelles
            with st.form("form_edition"):
                col1, col2 = st.columns(2)
                with col1:
                    nouveau_sexe = st.radio("Sexe :", ["Masculin", "Féminin"], index=["Masculin", "Féminin"].index(row_data["Sexe"]))
                    nouveau_classe = st.radio("Classe :", ["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"], index=["6e", "5e", "4e", "3e", "2nde", "1ère", "Tle"].index(row_data["Classe"]))
                with col2:
                    nouveau_etab = st.text_input("Établissement :", value=row_data["Etablissement"])
                
                st.write("---")
                nouveau_freq = st.radio("Fréquence exercices :", ["Toujours", "Souvent", "Parfois", "Rarement", "Jamais"], index=["Toujours", "Souvent", "Parfois", "Rarement", "Jamais"].index(row_data["Frequence_Ex"]))
                nouveau_comp = st.radio("Compréhension des consignes :", ["Oui toujours", "Oui parfois", "Non pas vraiment"], index=["Oui toujours", "Oui parfois", "Non pas vraiment"].index(row_data["Comprehension"]))
                nouveau_outils = st.radio("Outils nécessaires disponibles :", ["Oui", "Non"], index=["Oui", "Non"].index(row_data["Outils"]))
                nouveau_aide = st.radio("Aide apportée par la leçon :", ["Oui beaucoup", "Oui un peu", "Non vraiment", "Pas du tout"], index=["Oui beaucoup", "Oui un peu", "Non vraiment", "Pas du tout"].index(row_data["Aide_Lecon"]))
                
                nouveau_exemple = st.text_area("Exemple d'exercice aimé/pas aimé :", value=str(row_data["Exemple_Texte"]))
                nouveau_citoyen = st.radio("Utilité citoyenne :", ["Oui", "Non", "Je ne sais pas"], index=["Oui", "Non", "Je ne sais pas"].index(row_data["Utilite_Citoyen"]))
                
                bouton_maj = st.form_submit_button("🔄 Appliquer et mettre à jour la fiche")
                
                if bouton_maj:
                    # Application des modifications directes dans le DataFrame
                    df.loc[index_ligne, "Sexe"] = nouveau_sexe
                    df.loc[index_ligne, "Classe"] = nouveau_classe
                    df.loc[index_ligne, "Etablissement"] = nouveau_etab.upper()
                    df.loc[index_ligne, "Frequence_Ex"] = nouveau_freq
                    df.loc[index_ligne, "Comprehension"] = nouveau_comp
                    df.loc[index_ligne, "Outils"] = nouveau_outils
                    df.loc[index_ligne, "Aide_Lecon"] = nouveau_aide
                    df.loc[index_ligne, "Exemple_Texte"] = nouveau_exemple
                    df.loc[index_ligne, "Utilite_Citoyen"] = nouveau_citoyen
                    
                    sauvegarder_toutes_donnees(df)
                    st.success(f"✅ Les modifications appliquées sur la fiche apprenant **{id_selectionne}** ont été sauvegardées avec succès. Rechargez la page si nécessaire.")
                    st.rerun()

        elif action == "Supprimer la fiche":
            st.warning(f"⚠️ Attention : La suppression de la fiche apprenant **{id_selectionne}** est irréversible.")
            
            # Double validation par case à cocher de sécurité
            confirmation = st.checkbox("Je confirme vouloir supprimer définitivement cette ligne de données.")
            bouton_supprimer = st.button("❌ Supprimer définitivement")
            
            if bouton_supprimer:
                if confirmation:
                    # Suppression de la ligne ciblée par son ID
                    df = df[df["ID"] != id_selectionne]
                    sauvegarder_toutes_donnees(df)
                    st.success(f"🗑️ La fiche apprenant **{id_selectionne}** a été retirée définitivement de la base de données CSV.")
                    st.rerun()
                else:
                    st.error("Veuillez cocher la case de confirmation avant de cliquer sur le bouton de suppression.")
