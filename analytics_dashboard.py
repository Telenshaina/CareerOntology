import streamlit as st # Keep this at the very top!
import pandas as pd
from supabase import create_client, Client

# --- Streamlit Page Configuration (MUST BE FIRST Streamlit command) ---
st.set_page_config(page_title="CICS Analytics Dashboard", layout="wide")

# --- Supabase Initialization (same as main app) ---
# Retrieve credentials from Streamlit secrets
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase_client():
    return create_client(supabase_url, supabase_key)

supabase: Client = init_supabase_client()

# --- Your existing data utilities (for format_ontology_name) ---
# Make sure data.py is accessible or copy the format_ontology_name function here
from data import format_ontology_name # Assuming data.py is in the same directory

# --- Analytics Dashboard App ---
st.title("📊 CICS Program Recommender Analytics")

# Simple password protection for the dashboard
password = st.text_input("Enter password to view analytics:", type="password")
if password != "mylittlepony": # REPLACE THIS WITH A STRONG PASSWORD!
    st.stop() # Stop execution if password is incorrect

st.markdown("---")

@st.cache_data(ttl=600) # Cache data for 10 minutes to reduce Supabase reads
def get_user_selections():
    try:
        response = supabase.table("user_selections").select("*").execute()
        return response.data # response.data contains the list of dictionaries
    except Exception as e:
        st.error(f"Error fetching data from Supabase: {e}")
        return []

data = get_user_selections()

if not data:
    st.info("No user selection data collected yet.")
else:
    df = pd.DataFrame(data)

    st.header("Overall Statistics")
    total_unique_sessions = df['session_id'].nunique()
    total_interest_selections = len(df)
    # Ensure timestamp is datetime for min/max
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    earliest_record = df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S')
    latest_record = df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Unique Sessions", total_unique_sessions)
    with col2:
        st.metric("Total Interest Selections", total_interest_selections)
    with col3:
        st.metric("First Record", earliest_record)
    with col4:
        st.metric("Last Record", latest_record)

    st.markdown("---")

    st.header("Most Popular Interests Selected")
    interest_counts = df['interest'].value_counts().reset_index()
    interest_counts.columns = ['Interest', 'Selections']
    interest_counts['Interest'] = interest_counts['Interest'].apply(format_ontology_name)

    st.dataframe(interest_counts)
    st.bar_chart(interest_counts.set_index('Interest'))

    st.markdown("---")

    st.header("Activity Over Time")
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_activity = df['date'].value_counts().sort_index().reset_index()
    daily_activity.columns = ['Date', 'Selections']
    st.line_chart(daily_activity.set_index('Date'))

    # You can add more detailed analytics here, for example:
    # - Top combinations of interests
    # - How many interests are selected per session (average, distribution)
    # - Analyze the recommended programs (if you store program recommendations too)