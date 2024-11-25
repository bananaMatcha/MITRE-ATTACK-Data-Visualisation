import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Download stopwords if not already available
nltk.download('punkt')
nltk.download('stopwords')

st.set_page_config(
    page_title="Data Filtration",
    layout="wide",
)
st.title("Multi-Sheet Data Analysis")

# Function to clear the session state
def clear_session_state():
    st.session_state.pop('relationship_df', None)
    st.session_state.pop('campaigns_df', None)
    st.session_state.pop('techniques_df', None)
    st.session_state.pop('software_df', None)
    st.session_state.pop('upload', None)

# Access the relationship data from session_state
if 'relationship_df' in st.session_state and 'campaigns_df' in st.session_state and 'techniques_df' in st.session_state and 'software_df' in st.session_state:
    df = st.session_state['relationship_df']
    
    df_techniques = df[(df['mapping type'] == 'uses') & (df['target type'] == 'technique')]
    df_software = df[(df['mapping type'] == 'uses') & (df['target type'] == 'software')]
    df_detection = df[(df['mapping type'] == 'detects') & (df['target type'] == 'technique')]
    df_mitigation = df[(df['mapping type'] == 'mitigates') & (df['target type'] == 'technique')]
    df_attribute_to = df[(df['mapping type'] == 'attributed-to') & (df['target type'] == 'group')]

    df_campaigns = st.session_state['campaigns_df']
    df_techniques_sheet = st.session_state['techniques_df']
    df_software_sheet = st.session_state['software_df']


@st.cache_data
def load_data(file):
    return pd.read_excel(file, sheet_name=None)

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")

    # Provide a button to clear the current file upload
    if 'upload' in st.session_state:
        if st.button("Remove Uploaded File"):
            clear_session_state()

    # File uploader (resets after clearing the session state)
    if 'upload' not in st.session_state:
        upload = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
        if upload is not None:
            st.session_state['upload'] = upload  # Save the uploaded file in session state

    if 'upload' in st.session_state:
        data_sheets = load_data(st.session_state['upload'])
        sheet_names = list(data_sheets.keys())

        # Store the relationship sheet in session_state
        if 'techniques' in data_sheets:
            st.session_state['techniques_df'] = data_sheets['techniques']
        if 'software' in data_sheets:
            st.session_state['software_df'] = data_sheets['software']
        if 'relationships' in data_sheets:
            st.session_state['relationship_df'] = data_sheets['relationships']
        if 'campaigns' in data_sheets:
            st.session_state['campaigns_df'] = data_sheets['campaigns']

        # Allow user to select a sheet
        selected_sheet = st.selectbox("Select a Sheet to Analyze", options=sheet_names)
        df = data_sheets[selected_sheet]
        st.subheader(f"Filters for {selected_sheet}")
        # Dynamically generate filter options based on available columns
        available_columns = df.columns.tolist()

        # Define possible filters based on common columns
        name_filter = st.text_input("Name contains", "") if 'name' in available_columns else None
        domain_filter = st.multiselect("Domain", options=df["domain"].dropna().unique()) if 'domain' in available_columns else None
        
        # Platforms Filter
        if 'platforms' in available_columns:
            all_platforms = df['platforms'].dropna().apply(lambda x: [p.strip() for p in x.split(',')] if isinstance(x, str) else x).explode()
            unique_platforms = all_platforms.drop_duplicates()
            platforms_filter = st.multiselect("Platforms", options=sorted(unique_platforms))
        else:
            platforms_filter = None

        # Tactics Filter
        if 'tactics' in available_columns:
            all_tactics = df['tactics'].dropna().apply(lambda x: [p.strip() for p in x.split(',')] if isinstance(x, str) else x).explode()
            tactics_filter = st.multiselect("Tactics", options=sorted(all_tactics.drop_duplicates()))
        else:
            tactics_filter = None

# Handle case when no file is uploaded
if 'upload' not in st.session_state:
    st.info("Upload an Excel file through the sidebar to begin.")
    st.stop()


df_clean = df.replace(np.nan, 0)

# Apply Filters
df_filtered = df.copy()

if name_filter:
    df_filtered = df_filtered[df_filtered["name"].str.contains(name_filter, case=False, na=False)]
if domain_filter:
    df_filtered = df_filtered[df_filtered["domain"].isin(domain_filter)]
if platforms_filter:
    df_filtered = df_filtered[df_filtered["platforms"].isin(platforms_filter)]
if tactics_filter:
    df_filtered = df_filtered[df_filtered["tactics"].isin(tactics_filter)]

# Data Preview
with st.expander("Raw Data Preview"):
    st.dataframe(df_filtered)

# Visualization Section
with st.expander("Interactive Visualizations"):
    st.header("Interactive Visualizations")
    if 'tactics' in df_filtered.columns:
        # Group the data by tactics and platforms for the sunburst chart
        tactics_platforms = df_filtered.groupby(['tactics', 'platforms']).size().reset_index(name='count')

        # Sunburst used to show the percentage of tactics used by each platforms 
        fig_sunburst = px.sunburst(
            tactics_platforms,
            path=['platforms', 'tactics'],  
            values='count',  #
            title="Tactics Distribution by Platform",
            color='count',  
            color_continuous_scale=px.colors.sequential.RdBu,  
            hover_data=['count']  
        )
        fig_sunburst.update_traces(textinfo='label+percent entry')  # Show both labels and percentages
        st.plotly_chart(fig_sunburst)
        # Heatmap of Tactics and Occurrences
        st.subheader("Tactic Heatmap")
        tactic_matrix = df_filtered.pivot_table(index="tactics", values="name", aggfunc='count', fill_value=0)
        fig_heatmap = px.imshow(
            tactic_matrix,
            title="Tactic Occurrence Heatmap",
            labels={"x": "Names", "y": "Tactics", "color": "Count"},
            aspect="auto"
        )
        st.plotly_chart(fig_heatmap)
        
    else:
        st.info("The selected sheet does not contain a 'tactics' column for visualization.")

with st.expander("TF-IDF Preview"):
    # TF-IDF Processing and Word Cloud
    if 'name' in df_filtered.columns:
        st.subheader("TF-IDF Word Cloud")

        def remove_stopwords(text):
            if not isinstance(text, str):
                return ""
            words = word_tokenize(text)
            return ' '.join([word for word in words if word.lower() not in set(stopwords.words('english'))])

        df_filtered['name_no_stopwords'] = df_filtered['name'].apply(remove_stopwords)

        if df_filtered['name_no_stopwords'].str.strip().any():
            tfidf_vectorizer = TfidfVectorizer()
            tfidf_matrix = tfidf_vectorizer.fit_transform(df_filtered['name_no_stopwords'])

            tfidf_totals = np.array(tfidf_matrix.sum(axis=0)).flatten()
            feature_names = tfidf_vectorizer.get_feature_names_out()

            word_weights = {feature_names[i]: tfidf_totals[i] for i in range(len(feature_names))}

            wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_weights)

            fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis('off')
            st.pyplot(fig_wc)
        else:
            st.info("No text available in the 'name' column after removing stopwords.")
    else:
        st.info("The selected sheet does not contain a 'name' column for TF-IDF processing.")


with st.expander("Group Techniques Comparison"):
    # Load the relationship data
    df_relationship = data_sheets['relationships']
    
    # Filter for group and technique relationships
    group_tech_relationships = df_relationship[
        ((df_relationship['source type'] == 'group') & (df_relationship['target type'] == 'technique')) |
        ((df_relationship['target type'] == 'group') & (df_relationship['source type'] == 'technique'))
    ]

    # Function to display combined binary heatmap for two selected groups
    def display_combined_group_techniques():
        st.header("Techniques Used by Group 1 and Group 2")

        # Extract unique group names
        groups = group_tech_relationships['source name'].unique()

        # Select two groups for comparison
        selected_group_1 = st.selectbox("Select Group 1", groups, key="group_1")
        selected_group_2 = st.selectbox("Select Group 2", groups, key="group_2")

        if selected_group_1 and selected_group_2:
            # Filter data for both selected groups
            group_df_1 = group_tech_relationships[group_tech_relationships['source name'] == selected_group_1]
            group_df_2 = group_tech_relationships[group_tech_relationships['source name'] == selected_group_2]

            # Prepare binary data for both groups (1 if technique exists, otherwise 0)
            group_technique_binary_1 = group_df_1[['source name', 'target name']].drop_duplicates()
            group_technique_binary_1['used'] = 1

            group_technique_binary_2 = group_df_2[['source name', 'target name']].drop_duplicates()
            group_technique_binary_2['used'] = 1

            # Pivot to get binary technique existence for both groups
            group_technique_pivot_1 = group_technique_binary_1.pivot(index='target name', columns='source name', values='used').fillna(0)
            group_technique_pivot_2 = group_technique_binary_2.pivot(index='target name', columns='source name', values='used').fillna(0)

            # Combine the two group dataframes on top of each other for easier comparison
            combined_techniques = group_technique_pivot_1.join(group_technique_pivot_2, how='outer', lsuffix='_1', rsuffix='_2').fillna(0)

            # Create the combined heatmap
            fig = px.imshow(
                combined_techniques.T,  
                title=f"Techniques Used by {selected_group_1} and {selected_group_2}",
                color_continuous_scale=["black", "blue"],  # Black for 0 (not used), blue for 1 (used)
                labels=dict(x="Techniques", y="Groups", color="Used"),
                text_auto=True  # Adds 1 and 0 inside the heatmap cells
            )
            
            fig.update_layout(
                xaxis_title="Techniques", 
                yaxis_title="Groups", 
            )

            st.plotly_chart(fig)
        else:
            st.error("Please select both Group 1 and Group 2 to view the comparison.")

    # Call the function to display the combined heatmap
    display_combined_group_techniques()

with st.expander("Attack Frequency"):
    # Error check
    df_relationship = data_sheets.get('relationships', None)

    if df_relationship is not None and 'target name' in df_relationship.columns and 'target type' in df_relationship.columns:
        st.subheader("Frequency of Target Names")

        # Sort by target type selection
        target_types = df_relationship["target type"].unique()
        selected_target_type = st.selectbox("Filter by Target Type:", options=target_types)

        # Filter the dataframe based on selected target type
        filtered_df = df_relationship[df_relationship["target type"] == selected_target_type]

        # Count the frequency of each target name
        target_name_count = filtered_df["target name"].value_counts().reset_index()
        target_name_count.columns = ["Target Name", "Count"]

        # Pie chart for target name frequencies
        fig_target_pie = px.pie(
            target_name_count,
            values="Count",
            names="Target Name",
            title=f"Frequency of Target Names in Attacks (Filtered by {selected_target_type})",
            hover_data=["Count"],
            color_discrete_sequence=px.colors.sequential.Blues,  # Custom color scheme
            hole=0.3  # Donut chart style for better clarity
        )

        fig_target_pie.update_traces(textinfo="percent+label", showlegend=True)
        st.plotly_chart(fig_target_pie)

        # Display the most frequent targets below the pie chart
        st.subheader("Top Targeted Entities")
        st.write(f"The most frequent attack target in the category **{selected_target_type}** is **{target_name_count.iloc[0]['Target Name']}** with **{target_name_count.iloc[0]['Count']} occurrences**.")
        
        st.write(f"Here are the top 5 most frequent targets for **{selected_target_type}**:")
        for i, row in target_name_count.head(5).iterrows():
            st.write(f"**{i+1}. {row['Target Name']}** - {row['Count']} occurrences")
        
    else:
        st.info("The relationships sheet, 'target name' column, or 'target type' column is missing for visualization.")