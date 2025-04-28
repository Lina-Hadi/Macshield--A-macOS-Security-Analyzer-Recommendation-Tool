import streamlit as st
import subprocess
import json
from datetime import datetime

# Import des modules de scan
from app.lynis_scanner import run_lynis_scan


# Configuration de la page
st.set_page_config(
    page_title="MacSecure",
    page_icon="🛡️"
)

# CSS simplifié
st.markdown("""
<style>
    .header { color: #0066cc; text-align: center; }
    .secure { color: #34c759; font-weight: bold; }
    .warning { color: #ff9500; font-weight: bold; }
    .critical { color: #ff3b30; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Titre
st.markdown("<h1 class='header'>🛡️ MacSecure</h1>", unsafe_allow_html=True)
st.markdown("### Analyse de sécurité simple pour macOS")

# Fonctions pour exécuter les scripts
def run_sip_analyzer():
    try:
        result = subprocess.run(['python', 'app/sip_analyzer.py'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "secure": False}

def run_firewall_checker():
    try:
        result = subprocess.run(['python', 'app/firewall_checker.py'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "secure": False}

def run_update_checker():
    try:
        result = subprocess.run(['python', 'app/update_checker.py'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "secure": False}

def run_malwarebytes_scan():
    try:
        apple_script = 'tell application "Malwarebytes" to activate'
        subprocess.run(["osascript", "-e", apple_script])
        return "Malwarebytes est en cours d'exécution. Veuillez vérifier l'application pour les résultats."
    except Exception as e:
        return f"Erreur: {e}"

# Création des onglets
tab1, tab2 = st.tabs(["Analyse Rapide", "Outils Avancés"])

with tab1:
    st.markdown("### Analyse Rapide de Sécurité")
    st.write("Exécutez une analyse rapide pour vérifier les paramètres de sécurité essentiels de votre Mac.")
    
    if st.button("Lancer l'Analyse Rapide"):
        with st.spinner("Analyse de votre système en cours..."):
            # Création de colonnes pour les résultats
            col1, col2 = st.columns(2)
            
            # Vérification SIP
            with col1:
                st.markdown("#### Protection d'Intégrité Système")
                sip_result = run_sip_analyzer()
                if "error" in sip_result:
                    st.error(f"Erreur lors de la vérification du SIP: {sip_result['error']}")
                else:
                    if sip_result.get("secure", False):
                        st.markdown("<p>Statut: <span class='secure'>ACTIVÉ ✓</span></p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p>Statut: <span class='critical'>DÉSACTIVÉ ⚠️</span></p>", unsafe_allow_html=True)
                        # Ligne corrigée ci-dessous
                        st.markdown(f"Recommandation: {sip_result.get('recommendation', 'Activer la Protection d Intégrité Système')}")
            
            # Vérification Firewall
            with col2:
                st.markdown("#### Pare-feu")
                firewall_result = run_firewall_checker()
                if "error" in firewall_result:
                    st.error(f"Erreur lors de la vérification du pare-feu: {firewall_result['error']}")
                else:
                    if firewall_result.get("secure", False):
                        st.markdown("<p>Statut: <span class='secure'>ACTIVÉ ✓</span></p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p>Statut: <span class='critical'>DÉSACTIVÉ ⚠️</span></p>", unsafe_allow_html=True)
                        if "recommendations" in firewall_result:
                            for rec in firewall_result["recommendations"]:
                                st.markdown(f"- {rec}")
            
            st.markdown("---")
            
            # Vérification des mises à jour
            st.markdown("#### Mises à jour logicielles")
            update_result = run_update_checker()
            if "error" in update_result:
                st.error(f"Erreur lors de la vérification des mises à jour: {update_result['error']}")
            else:
                if update_result.get("secure", False):
                    st.markdown("<p>Statut: <span class='secure'>À JOUR ✓</span></p>", unsafe_allow_html=True)
                else:
                    update_count = update_result.get("total_updates", 0)
                    security_count = update_result.get("security_update_count", 0)
                    st.markdown(f"<p>Statut: <span class='warning'>{update_count} MISES À JOUR DISPONIBLES</span> ({security_count} mises à jour de sécurité)</p>", unsafe_allow_html=True)
                    st.markdown(f"Recommandation: {update_result.get('recommendation', 'Installer les mises à jour de sécurité en attente')}")

with tab2:
    st.markdown("### Outils de Sécurité Avancés")
    
    tool_option = st.selectbox(
        "Choisissez un outil de sécurité à exécuter:",
        [
            "Sélectionnez un outil",
            "Analyse Lynis",
            "Scan Malwarebytes"
        ]
    )
    
    if tool_option != "Sélectionnez un outil" and st.button(f"Exécuter {tool_option}"):
        with st.spinner(f"Exécution de {tool_option}. Cela peut prendre plusieurs minutes..."):
            if tool_option == "Analyse Lynis":
                output = run_lynis_scan()
                st.markdown("#### Résultats de l'analyse Lynis")
                st.text_area("Sortie", output, height=300)
                
            elif tool_option == "Scan Malwarebytes":
                output = run_malwarebytes_scan()
                st.markdown("#### Malwarebytes")
                st.info(output)

# Bouton pour générer un rapport
# Bouton pour générer un rapport
if st.button("Générer un rapport de sécurité"):
    with st.spinner("Génération du rapport de sécurité..."):
        # Exécution des analyses de sécurité
        sip_result = run_sip_analyzer()
        firewall_result = run_firewall_checker()
        update_result = run_update_checker()
        lynis_result = run_lynis_scan()
        malwarebytes_result = run_malwarebytes_scan()
        
        # Construction du rapport texte
        report_content = f"""Rapport de Sécurité MacSecure
Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ÉTAT DE LA SÉCURITÉ:
- Protection d'Intégrité Système: {"ACTIVÉ" if sip_result.get("secure", False) else "DÉSACTIVÉ"}
- Configuration du pare-feu: {"ACTIVÉ" if firewall_result.get("secure", False) else "DÉSACTIVÉ"}
- Mises à jour logicielles: {"À JOUR" if update_result.get("secure", False) else f"{update_result.get('total_updates', 0)} MISES À JOUR DISPONIBLES"}

ANALYSE AVANCÉE:
- Résultats de Lynis:
{lynis_result if lynis_result else "Aucun résultat disponible"}

- Malwarebytes:
{malwarebytes_result if malwarebytes_result else "Aucun résultat disponible"}
"""
        
        # Affichage du rapport
        st.markdown("## Rapport de Sécurité MacSecure")
        st.markdown(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Téléchargement du rapport
        st.download_button(
            label="Télécharger le rapport (TXT)",
            data=report_content,
            file_name=f"macsecure_rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Pied de page
st.markdown("---")
st.markdown("MacSecure - Protection pour votre Mac")