import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import io
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="EduAnalyse Pro - Histoire-Géo & Éducation à la Citoyenneté",
    page_icon="🎓",
    layout="wide"
)

DB_FILE = "data_collecte.csv"

# --- INTERACTION GOOGLE WORKSPACE ---
try:
    from gemkick_corpus import create_document
    HAS_WORKSPACE = True
except ImportError:
    HAS_WORKSPACE = False

# --- FONCTION DE SAUVEGARDE DES DONNÉES ---
def sauvegarder_donnees(dict_data):
    df_new = pd.DataFrame([dict_data])
    if not os.path.isfile(DB_FILE):
        df_new.to_csv(DB_FILE, index=False, encoding='utf-8')
    else:
        df_new.to_csv(DB_FILE, mode='a', header=False, index=False, encoding='utf-8')

# --- CHARGEMENT DES DONNÉES ---
def charger_donnees():
    if os.path.isfile(DB_FILE):
        return pd.read_csv(DB_FILE, encoding='utf-8')
    return pd.DataFrame()

# =========================================================
# MOTEUR DE GÉNÉRATION DU RAPPORT PDF PROFESSIONNEL (FPDF)
# =========================================================
class PDFRapportMemoire(FPDF):
    def header(self):
        # En-tête uniquement sur les pages normales (pas la garde)
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
    pdf.set_text_color(26, 54, 93)  # Bleu nuit
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
    
    # Structure de tableau FPDF
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
    
    # Remplissage dynamique des lignes brutes enregistrées
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(15, 6, "Genre", border=1, fill=True)
    pdf.cell(15, 6, "Classe", border=1, fill=True)
    pdf.cell(35, 6, "Etablissement", border=1, fill=True)
    pdf.cell(25, 6, "Freq. Ex", border=1, fill=True)
    pdf.cell(20, 6, "Compreh.", border=1, fill=True)
    pdf.cell(15, 6, "Outils", border=1, fill=True)
    pdf.cell(30, 6, "Aide Lecon", border=1, fill=True)
    pdf.cell(35, 6, "Utilite Civ.", border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 7.5)
    for _, row in df.iterrows():
        # Troncature propre pour eviter les debordements de cellules FPDF
        etab = str(row.get('Etablissement', ''))[:20]
        freq = str(row.get('Frequence_Ex', ''))
        comp = str(row.get('Comprehension', ''))
        out = str(row.get('Outils', ''))
        aide = str(row.get('Aide_Lecon', ''))
        cit = str(row.get('Utilite_Citoyen', ''))
        
        pdf.cell(15, 6, str(row.get('Sexe', '')), border=1)
        pdf.cell(15, 6, str(row.get('Classe', '')), border=1)
        pdf.cell(35, 6, etab, border=1)
        pdf.cell(25, 6, freq, border=1)
        pdf.cell(20, 6, comp, border=1)
        pdf.cell(15, 6, out, border=1)
        pdf.cell(30, 6, aide, border=1)
        pdf.cell(35, 6, cit, border=1)
        pdf.ln()
        
    # --- AJUSTEMENT POUR COMPATIBILITÉ FPDF2 & EVITER L'ERREUR DE TYPE 'BYTEARRAY' ---
    pdf_bytes = pdf.output()
    if isinstance(pdf_bytes, (bytes, bytearray)):
        return bytes(pdf_bytes)
    return pdf_bytes.encode('latin1', errors='replace')

# --- BARRE LATÉRALE DE NAVIGATION ---
st.sidebar.title("🎓 EduAnalyse Mémoire Pro")
menu = st.sidebar.radio("Navigation", ["📝 Enregistrement des Données (Fiche)", "📊 Dashboard & Recommandations IA"])

# ==========================================
# 1. OPTION : ENREGISTREMENT FIDÈLE DU TEXTE DE LA FICHE APPRENANT
# ==========================================
if menu == "📝 Enregistrement des Données (Fiche)":
    st.title("📋 Questionnaire Détaillé destiné aux Apprenants")
    st.markdown("**Introduction** : Cher(e) apprenant. Ce questionnaire vise à recueillir ton avis sur les exercices pratiques réalisés pendant les cours d'Histoire-Géographie et Éducation à la Citoyenneté. Tes réponses aideront à comprendre les difficultés rencontrées et à améliorer les méthodes d'enseignement. Merci de répondre avec sincérité.")
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
        
        exemple_ex = st.text_area("2. Donne un exemple d'exercice pratique que tu as aimé ou pas aluse, et pourquoi")
        
        st.write("---")
        st.subheader("IV. Amélioration et suggestions")
        suggestions = st.multiselect("1. Qu'aimerais-tu que ton professeur fasse pour améliorer ces exercious ?",
                                     ["Plus de matériel", "Plus d'explications", "Plus ce temps", "Sorties pédagogiques"])
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
            sauvegarder_donnees(data)
            st.success("🎉 Les informations textuelles de la fiche ont été correctement archivées.")

# ==========================================
# 2. OPTION FUSIONNÉE : DASHBOARD & EXPORT PDF COMPLET
# ==========================================
elif menu == "📊 Dashboard & Recommandations IA":
    st.title("📊 Laboratoire Empirique : Tableau de Bord & Recommandations IA")
    st.caption("Espace unifié combinant l'analyse statistique, la critique interprétative et l'option d'exportation pour le mémoire.")
    st.write("---")
    
    df = charger_donnees()
    
    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Veuillez enregistrer une fiche d'évaluation pour activer les analyses.")
    else:
        # Calculs Universitaires Globaux
        total_fiches = len(df)
        sans_outils_pct = (df["Outils"] == "Non").sum() / total_fiches * 100
        mauvaise_comp_pct = (df["Comprehension"] == "Non pas vraiment").sum() / total_fiches * 100
        toujours_frequence_pct = (df["Frequence_Ex"] == "Toujours").sum() / total_fiches * 100
        
        # --- BLOC DE TÉLÉCHARGEMENT PDF VALIDE ---
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
        
        # --- BLOC VISUALISATION, INTERPRÉTATION ET CRITIQUE ACADÉMIQUE ---
        st.subheader("🔬 Analyse Graphique Descriptive et Discussion Critique")
        
        col_gauche, col_droite = st.columns(2)
        
        with col_gauche:
            st.markdown("#### Figure 1 : Répartition des apprenants selon la possession des outils nécessaires")
            fig1 = px.pie(df, names="Outils", color="Outils", color_discrete_map={"Oui": "#3182CE", "Non": "#E53E3E"}, hole=0.3)
            st.plotly_chart(fig1, use_container_width=True)
            
            st.markdown(f"""
            <div style="background-color:#F7FAFC; padding:15px; border-left:4px solid #3182CE; margin-bottom:20px; line-height:1.25;">
                <b style="color:#2B6CB0;">📊 INTERPRÉTATION :</b> L'analyse descriptive indique que <b>{sans_outils_pct:.1f}%</b> des apprenants déclarent évoluer sans les outils nécessaires pour bien participer.<br><br>
                <b style="color:#2B6CB0;">🧠 CRITIQUE ACADÉMIQUE :</b> Ce déficit matériel structurel induit un biais important dans l'acquisition des compétences de terrain. En sciences de l'éducation, enseigner l'Histoire-Géographie sans atlas ni cartes limite l'ancrage visuel et spatial.
            </div>
            """, unsafe_allow_html=True)
            
        with col_droite:
            st.markdown("#### Figure 2 : Fréquence du sentiment d'incompréhension face aux consignes données")
            couleurs_ardoise = {"Oui toujours": "#A0AEC0", "Oui parfois": "#718096", "Non pas vraiment": "#4A5568"}
            fig2 = px.histogram(df, x="Comprehension", color="Comprehension", color_discrete_map=couleurs_ardoise)
            st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown(f"""
            <div style="background-color:#F7FAFC; padding:15px; border-left:4px solid #4A5568; margin-bottom:20px; line-height:1.25;">
                <b style="color:#4A5568;">📊 INTERPRÉTATION :</b> Les résultats statistiques mettent en évidence que <b>{mauvaise_comp_pct:.1f}%</b> de l'échantillon exprime une incompréhension claire des énoncés.<br><br>
                <b style="color:#4A5568;">🧠 CRITIQUE ACADÉMIQUE :</b> Cette donnée révèle une faille dans la formulation de la consigne pédagogique. L'activité pratique perd son efficacité cognitive si les prérequis de vocabulaire ne sont pas assurés par l'enseignant.
            </div>
            """, unsafe_allow_html=True)

        st.write("---")
        
        # --- SOLUTIONS PROPOSÉES POUR LES ENSEIGNANTS ET APPRENANTS ---
        st.subheader("💡 Solutions Pratiques IA pour Valoriser l'Enseignement")
        
        solutions_html = """
        <table style="width:100%; border:none; background-color:#EDF2F7; padding:20px; border-radius:10px;">
            <tr>
                <td style="padding:10px; vertical-align:top; width:50%;">
                    <h5 style="color:#2C5282; margin-top:0; font-size:16px;">👨‍🏫 Recommandations pour les Enseignants</h5>
                    <ul style="line-height:1.25;">
                        <li><b>Régulation des consignes :</b> Reformuler systématiquement les questions complexes de lecture de cartes ou de textes.</li>
                        <li><b>Stratégie de groupe compensatoire :</b> Organiser des ateliers mixtes mettant en commun un atlas ou un livre.</li>
                    </ul>
                </td>
                <td style="padding:10px; vertical-align:top; width:50%;">
                    <h5 style="color:#22543D; margin-top:0; font-size:16px;">🎓 Conseils pour les Apprenants</h5>
                    <ul style="line-height:1.25;">
                        <li><b>Développement de l'écoute active :</b> Demander immédiatement des explications complémentaires si une consigne paraît floue.</li>
                        <li><b>Solidarité et partage :</b> Partager activement les supports de cours disponibles au sein des cercles d'études.</li>
                    </ul>
                </td>
            </tr>
        </table>
        """
        st.markdown(solutions_html, unsafe_allow_html=True)
