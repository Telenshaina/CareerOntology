# analytics_dashboard.py
import streamlit as st
import pandas as pd
# from supabase import create_client, Client # No longer needed if using st.connection
# import supabase # No longer needed if using st.connection
from st_supabase_connection import SupabaseConnection # <-- Import st_supabase_connection

# --- Local Imports ---
from data import format_ontology_name # Assuming data.py is accessible

st.set_page_config(page_title="CICS Analytics Dashboard", layout="wide")
st.title("📊 CICS Program Recommender Analytics")

password = st.text_input("Enter password to view analytics:", type="password")
if password != "mylittlepony":
    st.stop()

st.markdown("---")

# --- Supabase Initialization (Consistent with main.py) ---
# It automatically reads [connections.supabase] from .streamlit/secrets.toml
conn = st.connection("supabase", type=SupabaseConnection) # <-- Use st.connection here

@st.cache_data(ttl=600)
def get_analytics_data():
    try:
        # Fetch selections
        # Use conn.table instead of supabase.table
        selections_response = conn.table("user_selections").select("*").execute()
        selections_df = pd.DataFrame(selections_response.data)

        # Fetch user profiles (including strand)
        # Use conn.table instead of supabase.table
        profiles_response = conn.table("user_profiles").select("*").execute()
        profiles_df = pd.DataFrame(profiles_response.data)

        if selections_df.empty:
            return None, None # No data
        else:
            # MODIFIED: Merge the two dataframes on profile_id and id
            # 'profile_id' is the foreign key in user_selections
            # 'id' is the primary key in user_profiles
            merged_df = pd.merge(selections_df, profiles_df,
                                 left_on='profile_id', # <-- Use profile_id from user_selections
                                 right_on='id',        # <-- Use id from user_profiles
                                 how='left',
                                 suffixes=('_selection', '_profile')) # Add suffixes to distinguish columns with same names like 'id'

            return merged_df, selections_df # Return both merged and original selections

    except Exception as e:
        st.error(f"Error fetching data from Supabase: {e}")
        return None, None

merged_data, selections_df = get_analytics_data()

if merged_data is None or merged_data.empty: # Check for empty merged_data too
    st.info("No user selection data collected yet.")
else:
    st.header("Overall Statistics")
    # MODIFIED: Count unique profiles based on the 'id_profile' or 'id' from the profiles table
    total_unique_users = merged_data['id_profile'].nunique() if 'id_profile' in merged_data.columns else merged_data['id'].nunique() # Use id_profile after merge, or just id if not renamed
    total_interest_selections = len(merged_data)
    
    # Use the timestamp from the selections table, which is 'selected_at'
    merged_data['selected_at'] = pd.to_datetime(merged_data['selected_at']) # <-- Use 'selected_at' from user_selections
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

    st.header("Most Popular Interests Selected (Overall)")
    # Ensure 'interest_raw' is used as the column for interests from user_selections
    interest_counts_overall = merged_data['interest_raw'].value_counts().reset_index() # <-- Use 'interest_raw'
    interest_counts_overall.columns = ['Interest', 'Selections']
    interest_counts_overall['Interest'] = interest_counts_overall['Interest'].apply(format_ontology_name)
    st.dataframe(interest_counts_overall)
    st.bar_chart(interest_counts_overall.set_index('Interest'))

    st.markdown("---")

    st.header("Interest Selections by Strand")
    if 'strand' in merged_data.columns and not merged_data['strand'].isnull().all():
        # Drop rows where strand is None or NaN before grouping for cleaner display
        strand_data = merged_data.dropna(subset=['strand'])
        if not strand_data.empty:
            interest_by_strand = strand_data.groupby('strand')['interest_raw'].value_counts().unstack(fill_value=0)
            # Apply format_ontology_name to the index (interests)
            interest_by_strand.index = interest_by_strand.index.map(format_ontology_name)
            st.dataframe(interest_by_strand)

            # Optional: Visualize top interests per strand
            # MODIFIED LINE: Iterate directly over the columns of interest_by_strand
            for s_col in interest_by_strand.columns: # <--- CHANGED THIS LINE
                st.subheader(f"Top Interests for {s_col} Strand") # <--- Use s_col here
                strand_interests = interest_by_strand[s_col].sort_values(ascending=False).head(5) # Top 5
                if not strand_interests.empty:
                    st.bar_chart(strand_interests)
                else:
                    st.info(f"No interest data yet for {s_col} strand.") # <--- Use s_col here
        else:
            st.info("No strand data available yet.")
    else:
        st.info("No strand data collected or 'strand' column not found.")
