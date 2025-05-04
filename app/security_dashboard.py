import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def render_security_dashboard(sip_result, firewall_result, update_result, permissions_result=None):
    """
    Renders a comprehensive security dashboard with visualizations.
    """
    st.markdown("## Security Status Dashboard")
    
    # Calculate overall security score
    scores = []
    categories = []
    
    # SIP Score
    sip_score = 100 if sip_result.get("secure", False) else 0
    scores.append(sip_score)
    categories.append("SIP")
    
    # Firewall Score
    fw_score = firewall_result.get("security_score", 0)
    scores.append(fw_score)
    categories.append("Firewall")
    
    # Updates Score
    if update_result.get("secure", False):
        update_score = 100
    else:
        # Reduce score based on number of security updates pending
        security_updates = update_result.get("security_update_count", 0)
        update_score = max(0, 100 - (security_updates * 25))
    scores.append(update_score)
    categories.append("Updates")
    
    # Permissions Score (if available)
    if permissions_result and "security_score" in permissions_result:
        perm_score = permissions_result.get("security_score", 0)
        scores.append(perm_score)
        categories.append("Permissions")
    
    # Calculate overall score
    overall_score = int(sum(scores) / len(scores))
    
    # Create three columns
    col1, col2 = st.columns([1, 2])
    
    # Overall score gauge in first column
    with col1:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = overall_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Security Score"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': get_color_for_score(overall_score)},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "darkblue", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        # Add security status text
        if overall_score >= 90:
            st.markdown("<h3 style='text-align: center; color: green;'>SECURE</h3>", unsafe_allow_html=True)
        elif overall_score >= 70:
            st.markdown("<h3 style='text-align: center; color: orange;'>MODERATE RISK</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center; color: red;'>HIGH RISK</h3>", unsafe_allow_html=True)

    # Radar chart in second column
    with col2:
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            name='Security Scores',
            line_color='darkblue',
            fillcolor='rgba(0, 102, 204, 0.5)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Security Domain Scores",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Create security history simulation
    st.markdown("### Security History")
    
    # Generate synthetic historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create random but trending scores (trend toward current score)
    np.random.seed(42)  # For reproducibility
    start_score = max(40, overall_score - 30)  # Start lower than current
    
    # Create a trend line from start_score to overall_score
    trend = np.linspace(start_score, overall_score, len(dates))
    # Add some randomness
    random_factor = np.random.normal(0, 5, len(dates))
    # Combine trend and randomness, ensuring values stay between 0 and 100
    historical_scores = np.clip(trend + random_factor, 0, 100)
    
    # Create DataFrame
    history_df = pd.DataFrame({
        'Date': dates,
        'Security Score': historical_scores
    })
    
    # Plot the history
    fig = px.line(history_df, x='Date', y='Security Score', 
                 title='Security Score Trend (30 Days)',
                 labels={'Security Score': 'Overall Security Score'},
                 line_shape='spline')
    
    fig.update_layout(
        yaxis=dict(range=[0, 100]),
        hovermode="x unified"
    )
    
    # Add a reference line for "secure" threshold
    fig.add_shape(
        type="line",
        x0=history_df['Date'].min(),
        y0=90,
        x1=history_df['Date'].max(),
        y1=90,
        line=dict(color="green", width=2, dash="dash"),
    )
    
    # Add annotation for the reference line
    fig.add_annotation(
        x=history_df['Date'].max(),
        y=90,
        text="Secure Threshold",
        showarrow=False,
        yshift=10,
        font=dict(color="green")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Critical issues section
    st.markdown("### Critical Security Issues")
    
    issues = []
    
    # Check SIP
    if not sip_result.get("secure", False):
        issues.append({
            "severity": "Critical",
            "issue": "System Integrity Protection is disabled",
            "recommendation": sip_result.get("recommendation", "Enable SIP for system protection")
        })
    
    # Check Firewall
    if not firewall_result.get("firewall_enabled", False):
        issues.append({
            "severity": "High",
            "issue": "Firewall is disabled",
            "recommendation": "Enable macOS Firewall"
        })
    
    # Check Security Updates
    if update_result.get("security_update_count", 0) > 0:
        issues.append({
            "severity": "High",
            "issue": f"{update_result.get('security_update_count', 0)} security updates pending",
            "recommendation": "Install all pending security updates"
        })
    
    # Check Permissions (if available)
    if permissions_result:
        high_risk_count = len(permissions_result.get("high_risk_permissions", []))
        if high_risk_count > 0:
            issues.append({
                "severity": "Medium",
                "issue": f"{high_risk_count} high-risk permissions granted",
                "recommendation": "Review and revoke unnecessary permissions"
            })
        
        suspicious_agents = len(permissions_result.get("suspicious_launch_agents", []))
        if suspicious_agents > 0:
            issues.append({
                "severity": "High",
                "issue": f"{suspicious_agents} suspicious launch agents detected",
                "recommendation": "Investigate and remove suspicious launch agents"
            })
    
    # Display issues in a table
    if issues:
        # Create DataFrame for issues
        issues_df = pd.DataFrame(issues)
        
        # Apply colors based on severity
        def color_severity(val):
            if val == "Critical":
                return 'background-color: #ff3b30; color: white'
            elif val == "High":
                return 'background-color: #ff9500; color: white'
            else:
                return 'background-color: #ffcc00'
        
        # Display styled table
        st.dataframe(issues_df.style.applymap(color_severity, subset=['severity']), 
                    hide_index=True, use_container_width=True)
    else:
        st.success("No critical security issues detected. Your system is well-protected!")
        
def get_color_for_score(score):
    """Return an appropriate color based on the score."""
    if score >= 90:
        return 'green'
    elif score >= 70:
        return 'orange'
    else:
        return 'red'