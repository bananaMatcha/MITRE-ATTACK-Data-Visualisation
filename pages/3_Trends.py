import pandas as pd
import streamlit as st
import plotly.express as px

# Set the page configuration
st.set_page_config(
    page_title="MITRE ATT&CK",
    layout="wide",
)

# Title of the app
st.title("MITRE ATT&CK DATA")

# Access the relationship data from session_state
if 'relationship_df' in st.session_state and 'campaigns_df' in st.session_state and 'techniques_df' in st.session_state and 'software_df' in st.session_state:
    df = st.session_state['relationship_df']
    
    df_techniques = df[(df['mapping type'] == 'uses') & (df['target type'] == 'technique')]
    df_software = df[(df['mapping type'] == 'uses') & (df['target type'] == 'software')]
    df_detection = df[(df['mapping type'] == 'detects') & (df['target type'] == 'technique')]
    df_mitigation = df[(df['mapping type'] == 'mitigates') & (df['target type'] == 'technique')]
    df_attribute_to =df[(df['mapping type'] == 'attributed-to') & (df['target type'] == 'group')]

    df_campaigns = st.session_state['campaigns_df']
    df_techniques_sheet = st.session_state['techniques_df']
    df_software_sheet = st.session_state['software_df']
    # combined_campaigns_ = pd.concat(df_techniques.value(), ignore_index=True)
else:
    st.info("Please upload an excel file in the Data Filter page to see visualisations")
    st.stop()



    # Function to display visualizations for techniques
def display_techniques_visualization(df):
    # Allow dynamic filtering based on the usage count
    
    
    # Data Preview
    with st.expander("Data Preview"):
        st.dataframe(df)

    if 'target name' in df.columns:
        min_count = st.slider('Minimum Usage Count:', 0, 200, 100)
        technique_counts = df['target name'].value_counts().reset_index()
        technique_counts.columns = ['Technique', 'Usage Count']
        technique_counts = technique_counts[technique_counts['Usage Count'] >= min_count]

        if not technique_counts.empty:
            fig = px.bar(technique_counts, x='Technique', y='Usage Count',
                         title=f'Most Used Techniques in MITRE ATT&CK ({min_count}+ Uses)',
                         labels={'Usage Count': 'Number of Uses', 'Technique': 'Techniques'},
                         color='Usage Count', color_continuous_scale=px.colors.sequential.Viridis)

            fig.update_layout(width=1000, height=800)
            st.plotly_chart(fig)
        else:
            st.warning(f"No techniques with {min_count} or more uses found.")

def display_mitigation_visualization(df):
    with st.expander("Data Preview"):
        st.dataframe(df)

# Function to display visualizations for software
def display_software_visualization(df):
   
    with st.expander("Data Preview"):
        st.dataframe(df)

    if 'target name' in df.columns:
        min_count = st.slider('Minimum Usage Count:', 0, 100, 10)
        software_counts = df['target name'].value_counts().reset_index()
        software_counts.columns = ['Software', 'Usage Count']
        software_counts = software_counts[software_counts['Usage Count'] > min_count]

        if not software_counts.empty:
            fig = px.pie(software_counts, names='Software', values='Usage Count',
                         title='Most Used Software in MITRE ATT&CK ({min_count}+)',
                         color='Software', color_discrete_sequence=px.colors.sequential.Viridis)

            fig.update_layout(width=800, height=800)
            st.plotly_chart(fig)
             # Step 1: Merge with software sheet to get platforms
            merged_data = software_counts.merge(df_software_sheet[['name', 'platforms']],
                                                 left_on='Software', right_on='name', how='left')

            # Step 2: Explode platforms to separate rows if multiple platforms are listed
            merged_data['platforms'] = merged_data['platforms'].str.split(', ')
            merged_data = merged_data.explode('platforms')

            # Step 3: Group by platform and sum usage counts
            platform_usage = merged_data.groupby('platforms')['Usage Count'].sum().reset_index()


            # Step 5: Create a bar chart to visualize the same data
            if not platform_usage.empty:
                bar_fig = px.bar(platform_usage, x='platforms', y='Usage Count',
                                 title='Total Software Usage per Platform',
                                 labels={'platforms': 'Platform', 'Usage Count': 'Total Usage Count'},
                                 color='Usage Count', color_continuous_scale=px.colors.sequential.Viridis)

                bar_fig.update_layout(width=800, height=600)
                st.plotly_chart(bar_fig)
            else:
                st.warning("No platforms found for the software.")
        else:
            st.warning("No software with {min_count} or more uses found.")



def display_detection_visualization(df, source_name, source_type, mapping_type, chart_title):
     # Data Preview
    with st.expander("Data Preview"):
        st.dataframe(df)

    if 'target name' in df.columns and 'source name' in df.columns:
        component_counts = df['source name'].value_counts().reset_index()
        component_counts.columns = [f'{source_name}', f'{chart_title} Count']
        component_counts = component_counts[component_counts[f'{chart_title} Count'] > 20]

        if not component_counts.empty:
            fig = px.bar(component_counts, x=f'{source_name}', y=f'{chart_title} Count',
                          title=f'Most Used {source_type} to {mapping_type} Techniques (20+ usage)',
                          labels={f'{chart_title} Count': f'{chart_title} Count',f'{source_name}':f'{source_name}'},
                          color=f'{chart_title} Count', color_continuous_scale=px.colors.sequential.Plasma)

            st.plotly_chart(fig)
        else:
            st.warning("No f'{source_name}'s found.")

        technique_counts = df['target name'].value_counts().reset_index()
        technique_counts.columns = ['Technique', 'Technique Count']
        component_counts = component_counts.merge(technique_counts, how='left', left_on=f'{source_name}', right_on='Technique')
        component_counts['Technique Count'] = component_counts['Technique Count'].fillna(0)

        if not component_counts.empty:
            fig = px.scatter(component_counts, x=f'{chart_title} Count', y='Technique Count',
                              size=f'{chart_title} Count', color=f'{source_name}',
                              hover_name=f'{source_name}', title=f'Bubble Chart of {source_type} Components',
                              labels={f'{chart_title} Count': f'{chart_title} Count', 'Technique Count': 'Number of Associated Techniques'},
                              size_max=60, template='plotly')

            st.plotly_chart(fig)
        else:
            st.warning("Not enough data to create a meaningful bubble chart.")
    else:
        st.warning("CSV must contain 'target name' and 'source name' columns.")



def display_campaign_techniques(df):
    # Filter only campaigns
    campaigns = df[df['source type'] == 'campaign']['source name'].unique()
    
    # Allow the user to select two campaigns for comparison
    selected_campaigns = st.multiselect("Select up to 2 Campaigns", campaigns, max_selections=2)
    
    if len(selected_campaigns) == 1 or len(selected_campaigns) == 2:
        # Create two columns for side-by-side comparison if two campaigns are selected
        if len(selected_campaigns) == 2:
            col1, col2 = st.columns(2)
        else:
            col1, col2 = st.columns([1, 0.1])  # Single column for one campaign, second column hidden
            
        for idx, campaign in enumerate(selected_campaigns):
            # Filter data for the selected campaign
            filtered_data = df[df['source name'] == campaign]

            if 'target name' in filtered_data.columns:
                technique_counts = filtered_data['target name'].value_counts().reset_index()
                technique_counts.columns = ['Technique', 'Usage Count']

                if not technique_counts.empty:
                    fig = px.pie(technique_counts, names='Technique', values='Usage Count',
                                 title=f'Techniques Used by {campaign}',
                                 color='Technique', color_discrete_sequence=px.colors.sequential.Plasma)

                    fig.update_layout(width=500, height=500)

                    # Display pie charts in separate columns
                    if idx == 0:
                        with col1:
                            st.subheader(f"Techniques used by {campaign}")
                            st.plotly_chart(fig)
                    elif idx == 1:
                        with col2:
                            st.subheader(f"Techniques used by {campaign}")
                            st.plotly_chart(fig)
                else:
                    st.warning(f"No techniques found for the campaign: {campaign}")
            else:
                st.warning("Target name column not found in the dataset.")
    else:
        st.warning("Please select one or two campaigns to display data.")



def display_campaign_group(df):
    group_counts = df_attribute_to.groupby('target name')['source name'].count().reset_index()
    group_counts.columns = ['Group', 'Campaign Count']

    # Sort the counts in descending order to see the most active groups first
    group_counts = group_counts.sort_values(by='Campaign Count', ascending=False)

    # Bar chart of most active groups
    fig = px.bar(group_counts, x='Group', y='Campaign Count',
                title='Most Active Groups in MITRE ATT&CK by Campaigns',
                labels={'Campaign Count': 'Number of Campaigns', 'Group': 'Groups'},
                color='Campaign Count', color_continuous_scale=px.colors.sequential.Plasma)

    # Display chart in Streamlit
    st.plotly_chart(fig)

# Function to display line chart of campaigns over time
def display_campaigns_line_chart(df_campaigns):
    # Ensure the 'first seen' and 'last seen' columns are in datetime format
    df_campaigns['first seen'] = pd.to_datetime(df_campaigns['first seen'], errors='coerce')
    df_campaigns['last seen'] = pd.to_datetime(df_campaigns['last seen'], errors='coerce')

    # Create a DataFrame for the number of campaigns per year
    df_campaigns['year'] = df_campaigns['first seen'].dt.year
    campaign_counts = df_campaigns['year'].value_counts().reset_index()
    campaign_counts.columns = ['Year', 'Campaign Count']
    campaign_counts = campaign_counts.sort_values(by='Year')

    # Plotting the line chart
    fig = px.line(campaign_counts, x='Year', y='Campaign Count',
                  title='Number of Campaigns Detected Over Time',
                  labels={'Year': 'Year', 'Campaign Count': 'Number of Campaigns'},
                  markers=True)
    st.plotly_chart(fig)
def display_campaigns_by_year(df_campaigns):
    # Ensure the 'first seen' column is in datetime format
    df_campaigns['first seen'] = pd.to_datetime(df_campaigns['first seen'], errors='coerce')

    # Extract the year from 'first seen'
    df_campaigns['year'] = df_campaigns['first seen'].dt.year

    # Remove any rows where 'year' is NaN (invalid 'first seen' values)
    df_campaigns = df_campaigns.dropna(subset=['year'])

    # Group by year and aggregate campaigns, and count the campaigns per year
    campaigns_by_year = df_campaigns.groupby('year').agg(
        Campaigns=('name', list),  # Aggregating campaigns into a list
        Count=('name', 'count')    # Counting the number of campaigns per year
    ).reset_index()

    # Sort the data by year for a better chronological view
    campaigns_by_year = campaigns_by_year.sort_values('year', ascending=False)

    # Displaying the campaigns in a table format with campaign count and list of campaigns
    st.subheader("Campaigns by Year")
    
    # Display styled dataframe with some enhancements (e.g., highlight max count)
    styled_table = campaigns_by_year.style.highlight_max(subset=['Count'], color='red', axis=0)
     # Display the table with a specific width and height
    st.dataframe(styled_table, use_container_width=500, height=500)
def display_campaign_scatter_plot(df_campaigns, df_techniques):
    # Ensure 'first seen' and 'last seen' are in datetime format
    df_campaigns['first seen'] = pd.to_datetime(df_campaigns['first seen'], errors='coerce')
    df_campaigns['last seen'] = pd.to_datetime(df_campaigns['last seen'], errors='coerce')

    # Calculate duration in days
    df_campaigns['duration'] = (df_campaigns['last seen'] - df_campaigns['first seen']).dt.days

    # Count techniques per campaign
    techniques_count = df_techniques.groupby('source name')['target name'].nunique().reset_index()
    techniques_count.columns = ['Campaign Name', 'Techniques Count']

    # Merge campaign duration and techniques count
    campaign_data = df_campaigns.merge(techniques_count, left_on='name', right_on='Campaign Name', how='left')

    # Fill NaN values in 'Techniques Count' with 0 for sizing
    campaign_data['Techniques Count'] = campaign_data['Techniques Count'].fillna(0)

    # Create scatter plot
    fig = px.scatter(campaign_data, x='Techniques Count', y='duration',
                     title='Campaign Duration vs. Techniques Count',
                     labels={'duration': 'Duration (days)', 'Techniques Count': 'Number of Techniques'},
                     hover_name='name', size='duration', color='name', size_max= 25,
                     template='plotly')

    st.plotly_chart(fig)
def display_campaigns_tactics_visualization(df_techniques, df_techniques_sheet): 
    # Step 1: Map techniques to their tactics
    technique_to_tactic = df_techniques_sheet[['ID', 'tactics']].rename(columns={'ID': 'target ID'})

    # Step 2: Merge techniques with their tactics
    techniques_with_tactics = df_techniques.merge(technique_to_tactic, on='target ID', how='left')

    # Filter only campaigns
    campaigns = df_techniques[df_techniques['source type'] == 'campaign']['source name'].unique()

    # Step 3: Campaign selection
    selected_campaigns = st.multiselect("Select up to 2 Campaigns", campaigns, max_selections=2)

    if len(selected_campaigns) == 1 or len(selected_campaigns) == 2:
        # Create two columns for side-by-side comparison if two campaigns are selected
        if len(selected_campaigns) == 2:
            col1, col2 = st.columns(2)
        else:
            col1, col2 = st.columns([1, 0.1])  # Single column for one campaign, second column hidden

        for idx, campaign in enumerate(selected_campaigns):
            # Step 4: Filter for the selected campaign
            filtered_tactics = techniques_with_tactics[techniques_with_tactics['source name'] == campaign]
            campaigns_tactics = filtered_tactics[['source name', 'tactics']].dropna()

            # Group tactics by the selected campaign
            tactics_per_campaign = campaigns_tactics.groupby('tactics')['source name'].count().reset_index()
            tactics_per_campaign.columns = ['Tactics', 'Campaign Count']

            # Step 5: Create a pie chart to visualize tactics used by the selected campaign
            if not tactics_per_campaign.empty:
                fig = px.pie(tactics_per_campaign, names='Tactics', values='Campaign Count',
                             title=f'Tactics Used by {campaign}',
                             labels={'Tactics': 'Tactics', 'Campaign Count': 'Number of Campaigns'},
                             color='Tactics', color_discrete_sequence=px.colors.sequential.Viridis)

                fig.update_traces(textinfo='percent+label')
                fig.update_layout(width=500, height=500)

                # Display pie charts in separate columns
                if idx == 0:
                    with col1:
                        st.subheader(f"Tactics used by {campaign}")
                        st.plotly_chart(fig)
                elif idx == 1:
                    with col2:
                        st.subheader(f"Tactics used by {campaign}")
                        st.plotly_chart(fig)
            else:
                st.warning(f"No tactics found for the campaign: {campaign}")
    else:
        st.warning("Please select one or two campaigns to display tactics.")

# Session state to track the current page
if 'page' not in st.session_state:  
    st.session_state.page = "Techniques"

# Create buttons for navigation
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("Most Used Techniques"):
        st.session_state.page = "Techniques"

with col2:
    if st.button("Most Used Software"):
        st.session_state.page = "Software" 

with col3:
    if st.button("Detection"):
        st.session_state.page = "Detection" 

with col4:
    if st.button("Mitigation Method"):
        st.session_state.page = "Mitigation" 
with col5:
    if st.button("Campaign"):
        st.session_state.page = "Attribute"

# Display the appropriate page based on the session state
if st.session_state.page == "Techniques":
    st.subheader("Most Used Techniques")
    display_techniques_visualization(df_techniques)
    display_campaign_techniques(df_techniques)  # Updated function for comparing techniques
    
elif st.session_state.page == "Software":
    st.subheader("Most Used Software")
    display_software_visualization(df_software)

elif st.session_state.page == "Detection":
    st.subheader("Detections")
  
    display_detection_visualization(df_detection, source_name="Data Components", source_type="Data Components", mapping_type ="Detect", chart_title="Detection")
 
elif st.session_state.page == "Mitigation":
    st.subheader("Mitigation")
    display_detection_visualization(df_mitigation, source_name="Mitigation Methods", source_type="Mitigation Methods", mapping_type="Mitigate", chart_title="Mitigation")

elif st.session_state.page == "Attribute":
    st.subheader("Campaign Visualisations")

    display_campaign_group(df)                   
    display_campaigns_line_chart(df_campaigns)
    display_campaigns_by_year(df_campaigns)
    display_campaign_scatter_plot(df_campaigns, df_techniques)
    display_campaigns_tactics_visualization( df_techniques, df_techniques_sheet)