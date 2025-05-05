import streamlit as st
import subprocess
import json
import pandas as pd
import os
from datetime import datetime
import pandas as pd

# Import des modules de scan
from app.lynis_scanner import run_lynis_scan

# Set page configuration
st.set_page_config(
    page_title="MacSecure Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Simple CSS to improve appearance slightly
st.markdown("""
<style>
    .header {
        color: #0066cc;
        text-align: center;
    }
    .tool-header {
        color: #34c759;
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
</style>
""", unsafe_allow_html=True)

# Title and intro
st.markdown("<h1 class='header'>🛡️ MacSecure Dashboard</h1>", unsafe_allow_html=True)
st.markdown("### Simple security analysis and recommendations for macOS")

# Functions to run your custom scripts
def run_sip_analyzer():
    try:
        result = subprocess.run(['python3', 'sip_analyzer.py'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "secure": False}

def run_firewall_checker():
    try:
        result = subprocess.run(['python3', 'firewall_check.py'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "secure": False}

def run_permission_analyzer():
    try:
        result = subprocess.run(['python3', 'permission_analyzer.py'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "secure": False}

def run_update_checker():
    try:
        result = subprocess.run(['python3', 'update_checker.py'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "secure": False}

def run_malwarebytes_scan():
    try:
        apple_script = '''
        tell application "Malwarebytes" to activate
        '''
        subprocess.run(["osascript", "-e", apple_script])
        return "Malwarebytes is now running. Please check the application for results."
    except Exception as e:
        return f"Error: {e}"

# Create tabs for different scanning options
tab1, tab2, tab3, tab4 = st.tabs(["Quick Scan", "System Security", "External Tools", "Reports"])

with tab1:
    st.markdown("### Quick Security Scan")
    st.write("Run a quick scan to check the most important security settings on your Mac.")
    
    if st.button("Run Quick Scan"):
        with st.spinner("Scanning your system..."):
            # Create columns for results
            col1, col2 = st.columns(2)
            
            # SIP Check
            with col1:
                st.markdown("#### System Integrity Protection")
                sip_result = run_sip_analyzer()
                if "error" in sip_result:
                    st.error(f"Error checking SIP: {sip_result['error']}")
                else:
                    if sip_result.get("secure", False):
                        st.markdown("<p>Status: <span class='secure'>ENABLED ✓</span></p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p>Status: <span class='critical'>DISABLED ⚠️</span></p>", unsafe_allow_html=True)
                        st.markdown(f"Recommendation: {sip_result.get('recommendation', 'Enable System Integrity Protection')}")
            
            # Firewall Check
            with col2:
                st.markdown("#### Firewall")
                firewall_result = run_firewall_checker()
                if "error" in firewall_result:
                    st.error(f"Error checking firewall: {firewall_result['error']}")
                else:
                    if firewall_result.get("secure", False):
                        st.markdown("<p>Status: <span class='secure'>ENABLED ✓</span></p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p>Status: <span class='critical'>DISABLED ⚠️</span></p>", unsafe_allow_html=True)
                        if "recommendations" in firewall_result:
                            for rec in firewall_result["recommendations"]:
                                st.markdown(f"**Recommendation:** {rec}")
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Updates Check
            st.markdown("#### Software Updates")
            update_result = run_update_checker()
            if "error" in update_result:
                st.error(f"Error checking updates: {update_result['error']}")
            else:
                if update_result.get("secure", False):
                    st.markdown("<p>Status: <span class='secure'>UP TO DATE ✓</span></p>", unsafe_allow_html=True)
                else:
                    update_count = update_result.get("total_updates", 0)
                    security_count = update_result.get("security_update_count", 0)
                    st.markdown(f"<p>Status: <span class='warning'>{update_count} UPDATES AVAILABLE</span> ({security_count} security updates)</p>", unsafe_allow_html=True)
                    st.markdown(f"Recommendation: {update_result.get('recommendation', 'Install pending security updates')}")
            
            st.markdown("---")
            
            # Permission Check
            st.markdown("#### Critical File Permissions")
            permission_result = run_permission_analyzer()
            if "error" in permission_result:
                st.error(f"Error checking permissions: {permission_result['error']}")
            else:
                if "results" in permission_result:
                    # Find insecure permissions
                    insecure_count = 0
                    for item in permission_result["results"]:
                        if not item.get("secure", True):
                            insecure_count += 1
                    
                    if insecure_count == 0:
                        st.markdown("<p>Status: <span class='secure'>SECURE ✓</span></p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p>Status: <span class='warning'>{insecure_count} INSECURE FILES FOUND</span></p>", unsafe_allow_html=True)
                        
                        # Display insecure files in a table
                        insecure_files = [
                            {"Path": item["path"], "Owner": item.get("owner", "Unknown"), 
                             "Permissions": item.get("permissions", "Unknown"), 
                             "Recommendation": item.get("recommendation", "Fix permissions")}
                            for item in permission_result["results"] if not item.get("secure", True)
                        ]
                        
                        if insecure_files:
                            st.dataframe(pd.DataFrame(insecure_files))

with tab2:
    st.markdown("### System Security Tools")
    st.write("Use these custom tools to analyze specific aspects of your Mac's security.")
    
    tool_option = st.selectbox(
        "Choose a security tool to run:",
        [
            "Select a tool",
            "System Integrity Protection (SIP) Analyzer",
            "Firewall Configuration Checker",
            "Permission Analyzer",
            "Software Update Checker"
        ]
    )
    
    if tool_option != "Select a tool" and st.button(f"Run {tool_option}"):
        with st.spinner(f"Running {tool_option}..."):
            if tool_option == "System Integrity Protection (SIP) Analyzer":
                result = run_sip_analyzer()
                st.json(result)
                


                # Show recommendation if needed
                if not result.get("secure", True) and "recommendation" in result:
                    st.markdown(f"**Recommendation:** {result['recommendation']}")
                    
            elif tool_option == "Firewall Configuration Checker":
                result = run_firewall_checker()
                st.json(result)
                
                # Show recommendations if needed
                if "recommendations" in result and result["recommendations"]:
                    st.markdown("**Recommendations:**")
                    for rec in result["recommendations"]:
                        st.markdown(f"- {rec}")
                    
            elif tool_option == "Permission Analyzer":
                result = run_permission_analyzer()
                st.json(result)
                
                # Create a table view of the results if available
                if "results" in result:
                    data = []
                    for item in result["results"]:
                        data.append({
                            "Path": item.get("path", ""),
                            "Owner": item.get("owner", ""),
                            "Permissions": item.get("permissions", ""),
                            "Secure": "✓" if item.get("secure", False) else "✗",
                            "Recommendation": item.get("recommendation", "")
                        })
                        
                    st.dataframe(pd.DataFrame(data))
                    
            elif tool_option == "Software Update Checker":
                result = run_update_checker()
                st.json(result)
                
                # Display updates if available
                if "update_list" in result and result["update_list"]:
                    st.markdown("**Available Updates:**")
                    for update in result["update_list"]:
                        st.markdown(f"- {update}")

with tab3:
    st.markdown("### External Security Tools")
    st.write("Run industry-standard security tools to perform more comprehensive security analysis.")
    
    tool_option = st.selectbox(
        "Choose an external tool to run:",
        [
            "Select a tool",
            "Lynis Security Scan",
            "Chkrootkit Scan", 
            "Malwarebytes Scan"
        ]
    )
    
    if tool_option != "Select a tool" and st.button(f"Run {tool_option}"):
        with st.spinner(f"Running {tool_option}. This may take several minutes..."):
            if tool_option == "Lynis Security Scan":
                output = run_lynis_scan()
                st.markdown("#### Lynis Scan Results")
                st.text_area("Output", output, height=400)
                
            elif tool_option == "Chkrootkit Scan":
                output = run_chkrootkit_scan()
                st.markdown("#### Chkrootkit Scan Results")
                st.text_area("Output", output, height=400)
                
>>>>>>> parent of fdfca1d (everything is fixeddddddd ,meryumii)
            elif tool_option == "Malwarebytes Scan":
                output = run_malwarebytes_scan()
                st.markdown("#### Malwarebytes")
                st.info(output)

with tab4:
    st.markdown("### Security Reports")
    st.write("View and save security reports from your scans.")
    
    # Button to generate a comprehensive report
    if st.button("Generate Comprehensive Security Report"):
        with st.spinner("Generating comprehensive security report..."):
            # Run all security checks
            sip_result = run_sip_analyzer()
            firewall_result = run_firewall_checker()
            permission_result = run_permission_analyzer()
            update_result = run_update_checker()
            
            # Display report
            st.markdown("## MacSecure Comprehensive Security Report")
            st.markdown(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # System security status
            st.markdown("### System Security Status")
            
            # Count secure and insecure items
            checks = [
                {"name": "System Integrity Protection", "secure": sip_result.get("secure", False)},
                {"name": "Firewall Configuration", "secure": firewall_result.get("secure", False)},
                {"name": "Software Updates", "secure": update_result.get("secure", False)}
            ]
            
            # Add permission results
            if "results" in permission_result:
                for item in permission_result["results"]:
                    checks.append({
                        "name": f"File Permissions: {item.get('path', 'Unknown path')}",
                        "secure": item.get("secure", False)
                    })
            
            # Calculate security score
            secure_count = sum(1 for check in checks if check["secure"])
            total_count = len(checks)
            security_score = (secure_count / total_count) * 100 if total_count > 0 else 0
            
            # Display security score
            st.markdown(f"#### Overall Security Score: {security_score:.1f}%")
            
            # Create a dataframe for check results
            check_data = [
                {"Check": check["name"], 
                 "Status": "✅ Secure" if check["secure"] else "❌ Insecure"}
                for check in checks
            ]
            
            st.dataframe(pd.DataFrame(check_data))
            
            # Security recommendations
            st.markdown("### Security Recommendations")
            
            recommendations = []
            
            # Add SIP recommendation if needed
            if "recommendation" in sip_result and not sip_result.get("secure", True):
                recommendations.append(sip_result["recommendation"])
                
            # Add firewall recommendations if needed
            if "recommendations" in firewall_result:
                recommendations.extend(firewall_result["recommendations"])
                
            # Add update recommendation if needed
            if "recommendation" in update_result and not update_result.get("secure", True):
                recommendations.append(update_result["recommendation"])
                
            # Add permission recommendations if needed
            if "results" in permission_result:
                for item in permission_result["results"]:
                    if "recommendation" in item and not item.get("secure", True):
                        recommendations.append(item["recommendation"])
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"{i}. {rec}")
            else:
                st.markdown("No security recommendations at this time. Your system appears secure!")
            
            # Option to save report
            st.markdown("### Save Report")
            st.download_button(
                label="Download Report as TXT",
                data=f"""MacSecure Comprehensive Security Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SECURITY SCORE: {security_score:.1f}%

SECURITY CHECKS:
{chr(10).join(f"- {check['Check']}: {check['Status']}" for check in check_data)}

RECOMMENDATIONS:
{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations) if recommendations)}
""",
                file_name=f"macsecure_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("MacSecure Dashboard - Made with ❤️ for Mac security")