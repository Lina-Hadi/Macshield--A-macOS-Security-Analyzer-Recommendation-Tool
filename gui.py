import streamlit as st
import subprocess
import json
from datetime import datetime
import pandas as pd

# Import modules
from app.sip_analyzer import check_sip_status
from app.firewall_checker import check_firewall
from app.update_checker import check_software_updates
from app.lynis_scanner import run_lynis_scan
from app.security_dashboard import render_security_dashboard

# Configuration de la page
st.set_page_config(
    page_title="MacSecure",
    page_icon="🛡️",
    layout="wide"
)

# CSS improved
st.markdown("""
<style>
    .header {
        color: #0066cc;
        text-align: center;
        padding-bottom: 20px;
    }
    .secure {
        color: #34c759;
        font-weight: bold;
    }
    .warning {
        color: #ff9500;
        font-weight: bold;
    }
    .critical {
        color: #ff3b30;
        font-weight: bold;
    }
    .card {
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-card {
        text-align: center;
        padding: 15px 10px;
        border-radius: 5px;
        margin: 5px;
    }
    .recommendation {
        background-color: #f0f8ff;
        border-left: 4px solid #0066cc;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with app info
with st.sidebar:
    st.image("https://via.placeholder.com/150x150.png?text=MacSecure", width=150)
    st.markdown("### About MacSecure")
    st.markdown("""
    MacSecure is a comprehensive security scanner for macOS systems that:
    
    * Detects vulnerabilities
    * Checks security configurations
    * Monitors for suspicious activity
    * Provides remediation guidance
    
    **Version:** 1.0.0
    """)
    
    # Add scan history (mock data)
    st.markdown("### Scan History")
    scan_history = {
        "Date": ["2025-05-01", "2025-04-15", "2025-04-01"],
        "Score": [85, 76, 62]
    }
    history_df = pd.DataFrame(scan_history)
    st.dataframe(history_df, hide_index=True)

# Main content
st.markdown("<h1 class='header'>🛡️ MacSecure</h1>", unsafe_allow_html=True)
st.markdown("### Comprehensive Security Analysis for macOS")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Security Dashboard", "Quick Scan", "Advanced Tools", "Recommendations"])

with tab1:
    st.markdown("### System Security Dashboard")
    
    if st.button("Load Security Dashboard", key="dashboard_button"):
        with st.spinner("Analyzing your system security status..."):
            # Run security checks
            sip_result = check_sip_status()
            firewall_result = check_firewall()
            update_result = check_software_updates()
            permissions_result = check_tcc_permissions()
            
            # Render security dashboard
            render_security_dashboard(sip_result, firewall_result, update_result, permissions_result)

with tab2:
    st.markdown("### Quick Security Scan")
    st.write("Run a rapid scan to verify essential security settings on your Mac.")
    
    if st.button("Start Quick Scan"):
        with st.spinner("Scanning your system..."):
            # Run security checks
            sip_result = check_sip_status()
            firewall_result = check_firewall()
            update_result = check_software_updates()
            permissions_result = check_tcc_permissions()
            
            # Display results in an organized layout
            col1, col2 = st.columns(2)
            
            # SIP Status
            with col1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### System Integrity Protection")
                if "error" in sip_result:
                    st.error(f"Error checking SIP: {sip_result['error']}")
                else:
                    if sip_result.get("secure", False):
                        st.markdown("<p>Status: <span class='secure'>ENABLED ✓</span></p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p>Status: <span class='critical'>DISABLED ⚠️</span></p>", unsafe_allow_html=True)
                        st.markdown("<div class='recommendation'>", unsafe_allow_html=True)
                        st.markdown(f"**Recommendation:** {sip_result.get('recommendation', 'Enable System Integrity Protection')}")
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Firewall Status
            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### Firewall")
                if "error" in firewall_result:
                    st.error(f"Error checking firewall: {firewall_result['error']}")
                else:
                    if firewall_result.get("secure", False):
                        st.markdown("<p>Status: <span class='secure'>ENABLED ✓</span></p>", unsafe_allow_html=True)
                        st.markdown(f"Security Score: {firewall_result.get('security_score', 0)}/100")
                    else:
                        st.markdown("<p>Status: <span class='critical'>DISABLED ⚠️</span></p>", unsafe_allow_html=True)
                        st.markdown("<div class='recommendation'>", unsafe_allow_html=True)
                        if "recommendations" in firewall_result:
                            for rec in firewall_result["recommendations"]:
                                st.markdown(f"**Recommendation:** {rec}")
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Software Updates
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Software Updates")
            if "error" in update_result:
                st.error(f"Error checking for updates: {update_result['error']}")
            else:
                if update_result.get("secure", False):
                    st.markdown("<p>Status: <span class='secure'>UP TO DATE ✓</span></p>", unsafe_allow_html=True)
                else:
                    update_count = update_result.get("total_updates", 0)
                    security_count = update_result.get("security_update_count", 0)
                    st.markdown(f"<p>Status: <span class='warning'>{update_count} UPDATES AVAILABLE</span> ({security_count} security updates)</p>", unsafe_allow_html=True)
                    
                    if "update_list" in update_result and update_result["update_list"]:
                        with st.expander("View available updates"):
                            for update in update_result["update_list"]:
                                st.write(f"- {update}")
                    
                    st.markdown("<div class='recommendation'>", unsafe_allow_html=True)
                    st.markdown(f"**Recommendation:** {update_result.get('recommendation', 'Install pending security updates')}")
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Privacy Permissions
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Privacy Permissions")
            if "error" in permissions_result:
                st.error(f"Error checking privacy permissions: {permissions_result['error']}")
            else:
                high_risk = len(permissions_result.get("high_risk_permissions", []))
                suspicious = len(permissions_result.get("suspicious_launch_agents", []))
                
                if high_risk == 0 and suspicious == 0:
                    st.markdown("<p>Status: <span class='secure'>SECURE ✓</span></p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p>Status: <span class='warning'>ATTENTION NEEDED</span></p>", unsafe_allow_html=True)
                    st.markdown(f"- {high_risk} high-risk permissions granted")
                    st.markdown(f"- {suspicious} suspicious launch agents detected")
                    
                    # Show high risk permissions
                    if high_risk > 0:
                        with st.expander("View high-risk permissions"):
                            for perm in permissions_result["high_risk_permissions"]:
                                st.write(f"- {perm['application']} has access to {perm['service']}")
                    
                    # Show suspicious launch agents
                    if suspicious > 0:
                        with st.expander("View suspicious launch agents"):
                            for agent in permissions_result["suspicious_launch_agents"]:
                                st.write(f"- {agent['name']} ({agent['program']})")
                    
                    st.markdown("<div class='recommendation'>", unsafe_allow_html=True)
                    for rec in permissions_result.get("recommendations", []):
                        st.markdown(f"**Recommendation:** {rec}")
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("### Advanced Security Tools")
    
    tool_option = st.selectbox(
        "Choose a security tool to run:",
        [
            "Select a tool",
            "Lynis System Audit",
            "Malwarebytes Scan",
            "Login Items Analysis",
            "Network Connections Analysis"
        ]
    )
    
    if tool_option != "Select a tool" and st.button(f"Run {tool_option}"):
        with st.spinner(f"Running {tool_option}. This may take several minutes..."):
            if tool_option == "Lynis System Audit":
                output = run_lynis_scan()
                st.markdown("#### Lynis Audit Results")
                st.text_area("Output", output, height=300)
                
                # Add a more user-friendly summary
                st.markdown("#### Summary of Key Findings")
                # This is a mock implementation - in a real app, you'd parse the Lynis output
                st.markdown("""
                * **Hardening Level**: 65/100
                * **Tests Performed**: 231
                * **Warnings Found**: 12
                * **Suggestions**: 8
                """)
                
            elif tool_option == "Malwarebytes Scan":
                output = run_malwarebytes_scan()
                st.markdown("#### Malwarebytes")
                st.info(output)
                
            elif tool_option == "Login Items Analysis":
                st.markdown("#### Login Items Analysis")
                # Mock implementation
                login_items = [
                    {"name": "Dropbox", "path": "/Applications/Dropbox.app", "suspicious": False},
                    {"name": "iTerm2", "path": "/Applications/iTerm.app", "suspicious": False},
                    {"name": "GoogleDriveFS", "path": "/Applications/Google Drive.app", "suspicious": False}
                ]
                
                for item in login_items:
                    if item["suspicious"]:
                        st.warning(f"{item['name']} - {item['path']} - SUSPICIOUS")
                    else:
                        st.success(f"{item['name']} - {item['path']} - OK")
                
            elif tool_option == "Network Connections Analysis":
                st.markdown("#### Network Connections")
                # Mock implementation - in a real app, you'd run netstat or lsof
                connections = [
                    {"process": "Safari", "local": "127.0.0.1:50010", "remote": "17.253.144.10:443", "state": "ESTABLISHED"},
                    {"process": "Dropbox", "local": "127.0.0.1:50011", "remote": "162.125.6.7:443", "state": "ESTABLISHED"},
                    {"process": "Spotify", "local": "127.0.0.1:50012", "remote": "35.186.224.25:443", "state": "ESTABLISHED"}
                ]
                
                # Create a dataframe for display
                conn_df = pd.DataFrame(connections)
                st.dataframe(conn_df, hide_index=True)

with tab4:
    st.markdown("### Security Recommendations")
    
    # Mock recommendations based on common issues
    recommendations = [
        {"category": "System", "title": "Enable System Integrity Protection", 
         "description": "SIP prevents malware from modifying system files and directories.",
         "difficulty": "Medium",
         "impact": "High"},
        {"category": "Firewall", "title": "Enable Stealth Mode in Firewall", 
         "description": "Prevents your Mac from responding to network discovery probes.",
         "difficulty": "Easy",
         "impact": "Medium"},
        {"category": "Updates", "title": "Enable Automatic Security Updates", 
         "description": "Ensures your Mac always has the latest security patches.",}]