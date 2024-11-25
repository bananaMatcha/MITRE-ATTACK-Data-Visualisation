import streamlit as st
import pandas as pd

# Set page config at the very beginning
st.set_page_config(page_title="MITRE ATT&CK Visualization Tool", layout="wide")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }

    .reportview-container {
        background: linear-gradient(to right, #f0f4f8, #e2e8f0);
    }

    .main {
        background: #ffffff;
        padding: 3rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    h1 {
        color: #2c3e50;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    h2 {
        color: #34495e;
        font-weight: 600;
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }

    h3 {
        color: #2980b9;
        font-weight: 500;
        font-size: 1.4rem;
    }

    .overview-card, .feature-card {
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: #ffffff;
        height: 100%;
    }

    .overview-card:hover, .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }

    .overview-card h3, .feature-card h3 {
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .overview-card p, .feature-card p {
        font-size: 0.9rem;
    }

    .challenge-card { background-color: #e74c3c; }
    .mission-card { background-color: #3498db; }
    .objectives-card { background-color: #2ecc71; }
    .impact-card { background-color: #f39c12; }

    .feature-card {
        background-color: #2c3e50;
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .emoji-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .team-table {
        font-size: 0.9rem;
    }

    .team-table th {
        background-color: #3498db;
        color: white;
    }

    .team-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }

    footer {
        text-align: center;
        padding: 1rem;
        background-color: #34495e;
        color: #ecf0f1;
        border-radius: 0 0 10px 10px;
    }

    /* Hexagonal Technical Approach styles */
    .hex-container {
        display: flex;
        flex-wrap: wrap;
        margin-top: 20px;
        justify-content: center;
    }

    .hex-item {
        width: 250px;
        height: 280px;
        margin: 0 15px 30px;
        position: relative;
    }

    .hex-content {
        width: 100%;
        height: 100%;
        background-color: #3498db;
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        color: white;
        transition: transform 0.3s ease, background-color 0.3s ease;
        padding: 20px;
        box-sizing: border-box;
    }

    .hex-content:hover {
        transform: scale(1.05);
        background-color: #2980b9;
    }

    .hex-content::before {
        content: '';
        position: absolute;
        top: 3px;
        left: 3px;
        right: 3px;
        bottom: 3px;
        background-color: rgba(255, 255, 255, 0.1);
        clip-path: polygon(50% 2%, 98% 26%, 98% 74%, 50% 98%, 2% 74%, 2% 26%);
        z-index: 1;
    }

    .hex-inner {
        position: relative;
        z-index: 2;
    }

    .hex-icon {
        font-size: 3rem;
        margin-bottom: 15px;
    }

    .hex-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .hex-list {
        font-size: 0.9rem;
        list-style-type: none;
        padding: 0;
        margin: 0;
    }

    .hex-list li {
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

def colored_card(title, content, emoji, card_class):
    st.markdown(f"""
    <div class="{card_class}">
        <div class="emoji-icon">{emoji}</div>
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def feature_card(title, content, emoji):
    st.markdown(f"""
    <div class="feature-card">
        <div>
            <div class="emoji-icon">{emoji}</div>
            <h3>{title}</h3>
        </div>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def hex_tech_card(icon, title, technologies):
    tech_list = "".join([f"<li>{tech}</li>" for tech in technologies])
    return f"""
    <div class="hex-item">
        <div class="hex-content">
            <div class="hex-inner">
                <div class="hex-icon">{icon}</div>
                <div class="hex-title">{title}</div>
                <ul class="hex-list">
                    {tech_list}
                </ul>
            </div>
        </div>
    </div>
    """

def main():
    # Header
    st.title("MITRE ATT&CK Visualization Tool")

    # Welcome Section
    st.header("Welcome to Our MITRE ATT&CK Visualization Project")
    st.write("""
    We're developing an interactive desktop application to visualize and analyze the MITRE ATT&CK framework, 
    aiming to enhance cybersecurity readiness for organizations of all sizes in an era of increasing cyber threats.
    """)

    # Project Overview
    st.header("Project Overview")
    col1, col2 = st.columns(2)

    with col1:
        colored_card("The Challenge", 
                     "Cybercrime is on the rise, with FBI reports showing a 49% increase in losses from 2021 to 2022, totaling $10.3 billion. Organizations struggle to interpret and utilize the complex MITRE ATT&CK framework effectively.",
                     "🚨", "overview-card challenge-card")
        
        colored_card("Our Mission", 
                     "To simplify the MITRE ATT&CK framework, making it accessible and actionable for cybersecurity professionals. We aim to bridge the gap between comprehensive threat intelligence and practical, actionable insights.",
                     "🎯", "overview-card mission-card")

    with col2:
        colored_card("Key Objectives", 
                     """
                     • Reshape the MITRE ATT&CK dataset for easier analysis
                     • Develop robust data analysis methods
                     • Create an interactive application for visualizing cyber threat insights
                     """,
                     "🔑", "overview-card objectives-card")
        
        colored_card("Impact", 
                     "By providing clear, data-driven insights, we're empowering organizations to better understand, anticipate, and respond to potential security risks, ultimately improving their strategic and tactical readiness against cyber threats.",
                     "💡", "overview-card impact-card")

    # Key Features
    st.header("Key Features")
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)
    
    with feature_col1:
        feature_card("Advanced Search", 
                     "Quickly navigate the extensive MITRE ATT&CK dataset with powerful search functionality.",
                     "🔍")

    with feature_col2:
        feature_card("Interactive Visualizations", 
                     "Bring MITRE ATT&CK data to life with dynamic charts and graphs revealing patterns and trends.",
                     "📊")

    with feature_col3:
        feature_card("Customizable Filters", 
                     "Tailor your view of the data with advanced filtering options for in-depth analysis.",
                     "🔧")

    with feature_col4:
        feature_card("Export Capabilities", 
                     "Generate and download high-quality visualizations and reports for strategic planning.",
                     "📤")

    # Technical Approach
    st.header("Technical Approach")
    st.markdown("""
    <div class="hex-container">
        {0}
        {1}
        {2}
    </div>
    """.format(
        hex_tech_card("📊", "Data Processing", ["Python", "Pandas", "NumPy"]),
        hex_tech_card("🖥️", "Visualization", ["Streamlit", "Plotly", "Matplotlib"]),
        hex_tech_card("🧠", "Analysis", ["Scikit-learn", "NLTK", "NetworkX"])
    ), unsafe_allow_html=True)

    # Team Section
    st.header("Our Team")
    team_data = [
        {"name": "Henry Hua Rong Wang Hong", "id": "104792738"},
        {"name": "Rubie Stannard", "id": "103982732"},
        {"name": "Tan Dat Do", "id": "103498255"},
        {"name": "Jun Yao Lim", "id": "104219839"},
        {"name": "Han Nguyen", "id": "104101431"},
        {"name": "Arvan Talaska", "id": "103952502"}
    ]
    df = pd.DataFrame(team_data)
    st.markdown('<div class="team-table">', unsafe_allow_html=True)
    st.table(df)
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <footer>
        © 2024 MITRE ATT&CK Visualization Project Team. All rights reserved.
    </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
