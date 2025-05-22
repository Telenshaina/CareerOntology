import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime, timedelta
import pytz # Still need pytz to get timezone-aware current time

def format_ontology_name(name):
    """Formats an ontology name for display by replacing underscores with spaces."""
    return name.replace('_', ' ').replace('(broader, includes non-programming aspects)', '').replace('(FinTech)', '').strip()

st.set_page_config(page_title="CICS Analytics Dashboard", layout="wide")
st.title("📊 CICS Program Recommender Analytics")

password = st.text_input("Enter password to view analytics:", type="password")
if password != "mylittlepony": # Replace with your actual password
    st.stop()

st.markdown("---")

conn = st.connection("supabase", type=SupabaseConnection)

ONTOLOGY_MAP = {
    "Web_Development": "Programming & Software Development",
    "Mobile_App_Development": "Programming & Software Development",
    "Game_Programming": "Programming & Software Development",
    "Artificial_Intelligence_Machine_Learning": "Programming & Software Development",
    "Data_Science_Analytics_Programming": "Programming & Software Development",
    "Backend_Development": "Programming & Software Development",
    "Frontend_Development": "Programming & Software Development",

    "UX_UI_Design": "Creative & Multimedia Arts",
    "Graphic_Design": "Creative & Multimedia Arts",
    "Video_Editing_Production": "Creative & Multimedia Arts",
    "3D_Modeling_Animation": "Creative & Multimedia Arts",
    "Motion_Graphics": "Creative & Multimedia Arts",
    "Illustration": "Creative & Multimedia Arts",
    "Digital_Art": "Creative & Multimedia Arts",

    "Network_Administration": "IT Infrastructure & Cybersecurity",
    "Cybersecurity": "IT Infrastructure & Cybersecurity",
    "Cloud_Computing": "IT Infrastructure & Cybersecurity",
    "Database_Management": "IT Infrastructure & Cybersecurity",
    "Operating_Systems": "IT Infrastructure & Cybersecurity",
    "IT_Infrastructure": "IT Infrastructure & Cybersecurity",
    "Problem_Solving_Logic": "Foundational & Research Skills",

    "Project_Management": "Business, Management & Analytics",
    "Business_Analysis": "Business, Management & Analytics",
    "Entrepreneurship": "Business, Management & Analytics",
    "Digital_Marketing": "Business, Management & Analytics",
    "Financial_Technology (FinTech)": "Business, Management & Analytics",
    "Operations_Management": "Business, Management & Analytics",
    "Strategy_Planning": "Business, Management & Analytics",

    "Game_Design": "Game Design & Interactive Media",
    "Game_Development (broader, includes non-programming aspects)": "Game Design & Interactive Media",
    "Interactive_Storytelling": "Game Design & Interactive Media",
    "Virtual_Reality_Augmented_Reality": "Game Design & Interactive Media",
    "Esports_Management": "Game Design & Interactive Media",

    "Computer_Hardware": "Hardware, Robotics & IoT",
    "Embedded_Systems": "Hardware, Robotics & IoT",
    "Robotics": "Hardware, Robotics & IoT",
    "IoT (Internet_of_Things)": "Hardware, Robotics & IoT",
    "Electronics": "Hardware, Robotics & IoT",

    "Academic_Research": "Foundational & Research Skills",
    "New_Technologies": "Foundational & Research Skills",
    "Solving_Complex_Problems": "Foundational & Research Skills",
}

def get_parent_class(interest_name_raw):
    return ONTOLOGY_MAP.get(interest_name_raw, "Uncategorized")

@st.cache_data(ttl=600)
def get_analytics_data():
    try:
        selections_response = conn.table("user_selections").select("*").execute()
        selections_df = pd.DataFrame(selections_response.data)

        # Order by created_at for recency
        profiles_response = conn.table("user_profiles").select("*").order("created_at", desc=True).execute()
        profiles_df = pd.DataFrame(profiles_response.data)

        if selections_df.empty:
            return None, None, None
        else:
            merged_df = pd.merge(selections_df, profiles_df,
                                 left_on='profile_id',
                                 right_on='id',
                                 how='left',
                                 suffixes=('_selection', '_profile'))
            return merged_df, selections_df, profiles_df

    except Exception as e:
        st.error(f"Error fetching data from Supabase: {e}")
        return None, None, None

merged_data, selections_df, profiles_df = get_analytics_data()

if merged_data is None or merged_data.empty:
    st.info("No user selection data collected yet.")
else:
    st.header("Overall Statistics")
    total_unique_users = merged_data['id_profile'].nunique() if 'id_profile' in merged_data.columns else merged_data['id'].nunique()
    total_interest_selections = len(merged_data)
    
    merged_data['selected_at'] = pd.to_datetime(merged_data['selected_at'])
    earliest_record = merged_data['selected_at'].min().strftime('%Y-%m-%d %H:%M:%S')
    latest_record = merged_data['selected_at'].max().strftime('%Y-%m-%d %H:%M:%S')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Unique Users", total_unique_users)
    with col2:
        st.metric("Total Interest Selections", total_interest_selections)
    with col3:
        st.metric("First Record", earliest_record)
    with col4:
        st.metric("Last Record", latest_record)

    st.markdown("---")

    # --- Display Recently Answered Users ---
    st.subheader("Recently Answered Users")
    if profiles_df is not None and not profiles_df.empty:
        # Convert 'created_at' to datetime. It should already be timezone-aware if from Supabase `timestampz`.
        profiles_df['created_at'] = pd.to_datetime(profiles_df['created_at'])
        
        # Get current time in UTC using pytz
        utc_now = datetime.now(pytz.utc)
        
        # Define a time window for "recently" (e.g., last 7 days)
        time_threshold = utc_now - timedelta(days=7) 
        
        recent_users_df = profiles_df[profiles_df['created_at'] >= time_threshold]
        recent_users_df = recent_users_df.sort_values(by='created_at', ascending=False)

        if not recent_users_df.empty:
            recent_users_display = recent_users_df[['name', 'strand', 'created_at']].copy()
            # Format the display for created_at. You can choose to display in UTC
            # or convert to a local timezone (e.g., 'Asia/Manila') if preferred.
            # Example for Manila timezone:
            # manila_tz = pytz.timezone('Asia/Manila')
            # recent_users_display['created_at'] = recent_users_display['created_at'].dt.tz_convert(manila_tz).dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')
            recent_users_display['created_at'] = recent_users_display['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            recent_users_display.columns = ['Name', 'Strand', 'Answered At']
            st.dataframe(recent_users_display, hide_index=True)
        else:
            st.info("No users have answered in the last 7 days.")
    else:
        st.info("No user profile data available.")
    
    st.markdown("---")

    st.header("Most Popular Interests Selected (Overall)")
    interest_counts_overall = merged_data['interest_raw'].value_counts().reset_index()
    interest_counts_overall.columns = ['InterestRaw', 'Selections']

    interest_counts_overall['Main Classification'] = interest_counts_overall['InterestRaw'].apply(get_parent_class)
    
    interest_counts_overall['Interest'] = interest_counts_overall['InterestRaw'].apply(format_ontology_name)
    interest_counts_overall['Main Classification Display'] = interest_counts_overall['Main Classification'].str.replace('_', ' ')

    interest_counts_overall_sorted = interest_counts_overall.sort_values(
        by=['Main Classification Display', 'Selections'],
        ascending=[True, False]
    ).reset_index(drop=True)
    
    for main_class in interest_counts_overall_sorted['Main Classification Display'].unique():
        st.subheader(f"{main_class}")
        filtered_interests = interest_counts_overall_sorted[
            interest_counts_overall_sorted['Main Classification Display'] == main_class
        ]
        st.dataframe(filtered_interests[['Interest', 'Selections']], hide_index=True)

    st.markdown("---")

    st.header("Interest Selections by Strand")
    if 'strand' in merged_data.columns and not merged_data['strand'].isnull().all():
        strand_data = merged_data.dropna(subset=['strand'])
        if not strand_data.empty:
            interest_by_strand_pivot = strand_data.groupby('interest_raw')['strand'].value_counts().unstack(fill_value=0)
            
            interest_by_strand_pivot.index = interest_by_strand_pivot.index.map(format_ontology_name)
            
            interest_by_strand_pivot.columns = [col.replace('_', ' ') for col in interest_by_strand_pivot.columns]

            st.dataframe(interest_by_strand_pivot)

            for strand_name in interest_by_strand_pivot.columns:
                st.subheader(f"Top Interests for {strand_name} Strand")
                
                strand_interests_raw = interest_by_strand_pivot[strand_name].sort_values(ascending=False)
                
                if not strand_interests_raw.empty and strand_interests_raw.sum() > 0:
                    plot_df = pd.DataFrame(strand_interests_raw).reset_index()
                    plot_df.columns = ['Interest', 'Selections']
                    
                    formatted_to_raw_map = {format_ontology_name(k): k for k in ONTOLOGY_MAP.keys()}

                    plot_df['Parent Class'] = plot_df['Interest'].apply(
                        lambda formatted_interest: get_parent_class(formatted_to_raw_map.get(formatted_interest, formatted_interest.replace(' ', '_')))
                    )
                    
                    plot_df['Display Name'] = plot_df.apply(
                        lambda row: f"{row['Interest']} ({row['Parent Class']})" if row['Parent Class'] != "Uncategorized" else row['Interest'],
                        axis=1
                    )

                    top_5_interests = plot_df.head(5)
                    
                    if not top_5_interests.empty:
                        st.bar_chart(top_5_interests.set_index('Display Name')['Selections'])
                    else:
                        st.info(f"No top interests to display for {strand_name} Strand.")
                else:
                    st.info(f"No interest data yet for {strand_name} strand.")
        else:
            st.info("No strand data available yet.")
    else:
        st.info("No strand data collected or 'strand' column not found.")