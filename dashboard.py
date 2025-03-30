import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Page configuration - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="TalentNexus | Bioptimus",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bioptimus color scheme
BIOPTIMUS_PURPLE = "#6345FF"  # Primary purple color
BIOPTIMUS_LIGHT_PURPLE = "#9F8AFF"  # Lighter shade for accents
BIOPTIMUS_DARK = "#0A0A0A"  # Near black for text
BIOPTIMUS_WHITE = "#FFFFFF"  # White for backgrounds
BIOPTIMUS_SUCCESS = "#3CB371"  # Success green
BIOPTIMUS_WARNING = "#FF9F45"  # Warning orange
BIOPTIMUS_DANGER = "#FF4545"  # Danger red

# Custom CSS to match Bioptimus visual identity - with white background and visible text
st.markdown("""
<style>
    /* Add Theme overrides for Streamlit's theming system */
    .css-1qrvfrg {
        background-color: white !important;
    }
    
    /* Force light theme regardless of user preferences */
    html {
        color-scheme: light !important;
    }
    
    /* Force light theme on all Streamlit elements */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        color-scheme: light !important;
        background-color: white !important;
        color: #333333 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #EEEEEE;
        color: #333333;
    }
    
    /* Set basic colors and fonts */
    :root {
        --bioptimus-purple: #6345FF;
        --bioptimus-light-purple: #9F8AFF;
        --bioptimus-dark: #333333;
        --bioptimus-white: #FFFFFF;
    }
    
    /* Main title styling */
    .main-title {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 2.5rem;
        letter-spacing: 0.1em;
        color: var(--bioptimus-dark);
        margin-bottom: 2rem;
        text-transform: uppercase;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-family: 'Arial', sans-serif;
        font-size: 1.2rem;
        color: var(--bioptimus-dark);
        margin-bottom: 1.5rem;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        letter-spacing: 0.05em;
        color: #333333;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: var(--bioptimus-purple);
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: var(--bioptimus-light-purple);
    }
    
    /* Status colors */
    .status-interview {
        color: #3CB371;
        font-weight: bold;
    }
    .status-review {
        color: #FF9F45;
        font-weight: bold;
    }
    .status-reject {
        color: #FF4545;
        font-weight: bold;
    }
    
    /* Metrics styling */
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #EEEEEE;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: var(--bioptimus-purple);
    }
    .metric-label {
        font-size: 0.9rem;
        color: #555555;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #555555;
        padding: 1rem;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
    
    /* Fix selectbox styling */
    .stSelectbox > div > div {
        background-color: white !important;
        color: #333333 !important;
        border: 1px solid #ddd !important;
    }
    
    /* Fix dropdown options */
    div[data-baseweb="select"] > div {
        color: #333333 !important;
        background-color: white !important;
    }
    
    /* Ensure dropdown menus are white with dark text */
    div[data-baseweb="popover"] {
        background-color: white !important;
    }
    
    div[data-baseweb="select"] ul {
        background-color: white !important;
    }
    
    div[data-baseweb="select"] ul li {
        color: #333333 !important;
        background-color: white !important;
    }
    
    /* Fix the dropdown menu container */
    div[role="listbox"] {
        background-color: white !important;
    }
    
    /* Fix individual dropdown items */
    div[role="option"] {
        background-color: white !important;
        color: #333333 !important;
    }
    
    /* Hide Streamlit button elements */
    div[data-testid="stHorizontalBlock"] > div > div[data-testid="element-container"] > div > div > div > button {
        display: none !important;
    }
    
    /* Make sure hidden buttons stay hidden */
    div[id^="button_"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        position: absolute !important;
    }
    
    /* Make sure the dropdown panel itself is white */
    div[data-baseweb="select-dropdown"] {
        background-color: white !important;
    }
    
    /* Fix any popover content */
    div[data-baseweb="popover"] div {
        background-color: white !important;
    }
    
    /* Override dark theme for select dropdown completely */
    @media (prefers-color-scheme: dark) {
        div[data-baseweb="select"] ul, 
        div[data-baseweb="select"] ul li,
        div[role="listbox"],
        div[role="option"],
        div[data-baseweb="select-dropdown"],
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] div,
        div[data-testid="stSelectbox"] ul,
        div[data-testid="stSelectbox"] li {
            background-color: white !important;
            color: #333333 !important;
        }
        
        /* Ensure the highlighted item has a light purple background instead of dark */
        div[role="option"]:hover,
        div[role="option"][aria-selected="true"],
        div[role="option"][data-highlighted="true"],
        div[role="option"].highlighted,
        ul[role="listbox"] li[aria-selected="true"],
        [data-highlighted="true"], 
        [aria-selected="true"] {
            background-color: rgba(99, 69, 255, 0.1) !important;
            color: #333333 !important;
        }
    }
    
    /* Fix expander styling */
    .streamlit-expanderHeader {
        background-color: #F8F8F8;
        border-radius: 4px;
        color: #333333;
    }
    
    /* Fix widget labels */
    .stWidgetLabel, .stWidgetLabel p, label {
        color: #333333 !important;
    }
    
    /* Fix date input */
    .stDateInput > div > div {
        background-color: white !important;
        color: #333333 !important;
    }
    
    /* Fix date picker calendar */
    input[type="date"] {
        color: #333333 !important;
        background-color: white !important;
    }
    
    /* Date range inputs */
    .stDateInput input {
        background-color: white !important;
        color: #333333 !important;
        border: 1px solid #ddd !important;
    }
    
    /* Fix slider values */
    .stSlider {
        color: #333333;
    }
    
    /* Fix text elements */
    .element-container, p, span, div {
        color: #333333;
    }
    
    /* Fix dropdown text */
    .stSelectbox label {
        color: #333333 !important;
    }
    
    /* Fix tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        white-space: pre-wrap;
        background-color: #F0F0F5;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding: 0.5rem 1rem;
        color: #333333;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #6345FF;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Custom title
st.markdown('<div class="main-title">TALENTNEXUS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered Talent Screening System</div>', unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect('db/talentnexus.db', check_same_thread=False)

conn = get_connection()

# Sidebar for filtering
st.sidebar.markdown(f'<h2 style="color:{BIOPTIMUS_PURPLE};">Filters</h2>', unsafe_allow_html=True)

# Get list of roles
roles_df = pd.read_sql("SELECT id, title FROM roles", conn)
selected_role_id = st.sidebar.selectbox(
    "Select Role", 
    roles_df['id'].tolist(), 
    format_func=lambda x: roles_df[roles_df['id'] == x]['title'].iloc[0]
)

# Status filter
status_options = ["All", "Move to Interview", "Further Review", "Do Not Proceed"]
selected_status = st.sidebar.selectbox("Candidate Status", status_options)

# Build the query based on filters
query = """
SELECT 
    c.id, c.first_name, c.last_name, c.email, c.submission_date, c.status,
    e.technical_skills, e.experience_level, e.domain_knowledge, e.culture_fit, 
    e.overall_match, e.analysis_notes, e.recommendation, e.id as evaluation_id
FROM 
    candidates c
JOIN 
    evaluations e ON c.id = e.candidate_id
WHERE 
    e.role_id = ?
"""

params = [selected_role_id]

if selected_status != "All":
    query += " AND c.status = ?"
    params.append(selected_status)

query += " ORDER BY e.overall_match DESC"

# Execute query
candidates_df = pd.read_sql(query, conn, params=params)

# Calculate candidate fullname
candidates_df['full_name'] = candidates_df['first_name'] + ' ' + candidates_df['last_name']

# Get role information
role_info = pd.read_sql("SELECT * FROM roles WHERE id = ?", conn, params=[selected_role_id])
role_title = role_info['title'].iloc[0] if not role_info.empty else "Unknown Role"

# Main dashboard area
st.markdown(f"<h2 style='color:{BIOPTIMUS_PURPLE};'>Candidates for {role_title}</h2>", unsafe_allow_html=True)
st.markdown(f"<p>Showing {len(candidates_df)} candidates</p>", unsafe_allow_html=True)

# Skip summary metrics and go straight to score distribution
st.markdown(f"<h3 style='color:{BIOPTIMUS_PURPLE}; margin-top: 2rem;'>Score Distribution</h3>", unsafe_allow_html=True)

# Custom plotly theme to match Bioptimus
fig = px.histogram(candidates_df, x="overall_match", nbins=10, 
                  title="Distribution of Overall Match Scores",
                  labels={"overall_match": "Overall Match %", "count": "Number of Candidates"})

# Update the figure appearance to match Bioptimus color scheme
fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_family="Arial, sans-serif",
    font_color="#333333",
    title_font_size=18,
    title_font_color="#333333",
    title_x=0.5,
    xaxis=dict(
        title_font_size=14,
        tickfont_size=12,
        tickfont_color="#333333",
        gridcolor='#EEEEEE',
        showgrid=True,
        title_font_color="#333333"
    ),
    yaxis=dict(
        title_font_size=14,
        tickfont_size=12,
        tickfont_color="#333333",
        gridcolor='#EEEEEE',
        showgrid=True,
        title_font_color="#333333"
    ),
    bargap=0.1
)

# Update the bar color to match Bioptimus purple
fig.update_traces(marker_color=BIOPTIMUS_PURPLE, marker_line_color=BIOPTIMUS_LIGHT_PURPLE,
                 marker_line_width=1, opacity=0.8)

st.plotly_chart(fig, use_container_width=True)

# Candidate table with expandable rows
st.markdown(f"<h3 style='color:{BIOPTIMUS_PURPLE};'>Candidate Evaluations</h3>", unsafe_allow_html=True)

# Create a styled table header
st.markdown("""
<div style="display: grid; grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr; background-color: #f5f5f9; padding: 10px; border-radius: 5px; margin-bottom: 10px; font-weight: bold; color: #333333;">
    <div>Candidate</div>
    <div>Technical</div>
    <div>Experience</div>
    <div>Domain</div>
    <div>Culture</div>
    <div>Overall</div>
</div>
""", unsafe_allow_html=True)

# Display each candidate with expandable details
for index, row in candidates_df.iterrows():
    # Create the candidate row - without color styling based on status
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr; padding: 10px; border-bottom: 1px solid #eeeeee; align-items: center; color: #333333;">
        <div>{row['full_name']}</div>
        <div>{row['technical_skills']:.1f}/10</div>
        <div>{row['experience_level']:.1f}/10</div>
        <div>{row['domain_knowledge']:.1f}/10</div>
        <div>{row['culture_fit']:.1f}/10</div>
        <div><strong>{row['overall_match']:.1f}%</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Expandable section for details
    with st.expander(f"View details for {row['full_name']}"):
        detail_cols = st.columns(2)
        
        # Left column: Basic info and analysis notes
        with detail_cols[0]:
            # Display recommendation directly from the database
            recommendation_class = {
                'Move to Interview': 'status-interview',
                'Further Review': 'status-review',
                'Do Not Proceed': 'status-reject'
            }.get(row['recommendation'], '')
            
            st.markdown(f"""
            <div style="margin-bottom: 15px; color: #333333;">
                <p><strong>Email:</strong> {row['email']}</p>
                <p><strong>Applied:</strong> {row['submission_date']}</p>
                <p><strong>Recommendation:</strong> <span class="{recommendation_class}">
                    {row['recommendation']}
                </span></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<strong>Analysis Notes:</strong>", unsafe_allow_html=True)
            st.write(row['analysis_notes'])
            
            # Display Resume directly - not in an expander
            st.markdown(f"### {row['full_name']}'s Resume")
            
            # Fetch resume from candidates table
            resume_query = "SELECT resume FROM candidates WHERE id = ?"
            resume_data = pd.read_sql(resume_query, conn, params=[row['id']])
            
            if not resume_data.empty and resume_data['resume'].iloc[0]:
                st.markdown(resume_data['resume'].iloc[0])
            else:
                # Sample resume if real data not available
                st.markdown(f"""
                ## {row['full_name']}
                **Email:** {row['email']}
                
                ### Summary
                Experienced professional with expertise in {row['technical_skills'] > 7 and 'technical leadership' or 'project management'} 
                and a focus on {row['domain_knowledge'] > 7 and 'domain-specific solutions' or 'cross-functional collaboration'}.
                
                ### Experience
                **Senior Position** | Previous Company | 2021-Present
                - Led teams of {int(row['experience_level'])} members
                - Implemented solutions resulting in {int(row['overall_match'])}% efficiency improvements
                
                **Earlier Role** | Earlier Company | 2018-2021
                - Collaborated across departments
                - Developed expertise in relevant technologies
                
                ### Skills
                - Technical: {'Advanced' if row['technical_skills'] > 7 else 'Intermediate'} programming skills
                - Domain: {'Deep' if row['domain_knowledge'] > 7 else 'Working'} knowledge of industry standards
                - Interpersonal: {'Excellent' if row['culture_fit'] > 7 else 'Strong'} communication and teamwork
                
                This is a placeholder resume generated based on candidate scores.
                """)
        
        # Right column: Radar chart of scores
        with detail_cols[1]:
            categories = ['Technical Skills', 'Experience', 'Domain Knowledge', 'Culture Fit']
            scores = [
                row['technical_skills'], 
                row['experience_level'], 
                row['domain_knowledge'], 
                row['culture_fit']
            ]
            
            # Create a radar chart with Bioptimus colors
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='Candidate Scores',
                line_color=BIOPTIMUS_PURPLE,
                fillcolor=f'rgba(99, 69, 255, 0.3)'
            ))
            
            # Create the radar chart layout with 5% reduced size
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10],
                        linecolor='#EEEEEE'
                    ),
                    bgcolor='white',
                ),
                paper_bgcolor='white',
                plot_bgcolor='white',
                showlegend=False,
                margin=dict(l=45, r=45, t=25, b=45),  # Slightly larger margins to reduce chart size
                font_color="#333333",
                height=380,  # Set explicit height (5% smaller than default 400)
                width=380    # Set explicit width (5% smaller than default 400)
            )
            st.plotly_chart(fig, use_container_width=True)

# Add auto-refresh capability
st.sidebar.markdown(f'<h2 style="color:{BIOPTIMUS_PURPLE}; margin-top: 2rem;">Dashboard Settings</h2>', unsafe_allow_html=True)

refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds)", 0, 300, 0)

if refresh_interval > 0:
    st.sidebar.write(f"Dashboard will auto-refresh every {refresh_interval} seconds")
    st.sidebar.write("Last refreshed: " + datetime.now().strftime("%H:%M:%S"))
    
    # Add JavaScript for auto-refresh
    refresh_js = f"""
    <script>
        var refreshRate = {refresh_interval * 1000};
        function refresh() {{
            setTimeout(function() {{
                window.location.reload();
                refresh();
            }}, refreshRate);
        }}
        refresh();
    </script>
    """
    st.sidebar.markdown(refresh_js, unsafe_allow_html=True)

# Footer with Bioptimus branding
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="color: #555555;">TalentNexus AI-powered Talent Screening System</p>
    <p style="font-weight: bold; letter-spacing: 0.1em; margin-top: 0.5rem; color: #6345FF;">BIOPTIMUS © 2025</p>
</div>
""", unsafe_allow_html=True)