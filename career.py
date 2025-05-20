import streamlit as st # Keep this at the very top!

# --- Streamlit Page Configuration (MUST BE FIRST Streamlit command) ---
st.set_page_config(page_title="CICS Program Suggester", layout="wide")

# --- Standard Library Imports ---
import uuid
import datetime

# --- Third-Party Imports ---
from supabase import create_client, Client

# --- Local Imports (assuming these files are in the same directory) ---
from data import categorized_student_interests_raw, programs, interest_to_related_skills, format_ontology_name
from descriptions import interest_descriptions

# --- Supabase Initialization ---
# Retrieve credentials from Streamlit secrets
# Make sure you have a .streamlit/secrets.toml file with SUPABASE_URL and SUPABASE_KEY
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

# Create a Supabase client instance and cache it
# This ensures the client is initialized only once for performance
@st.cache_resource
def init_supabase_client():
    return create_client(supabase_url, supabase_key)

supabase: Client = init_supabase_client()

# --- Custom CSS for Layout Adjustments ---
st.markdown(
    """
    <style>
    .st-emotion-cache-z5fcl4 {
        padding-top: 1rem;
        padding-right: 3rem;
        padding-bottom: 1rem;
        padding-left: 3rem;
    }

    .st-emotion-cache-1jmve30 {
        gap: 0.75rem;
    }
    .st-emotion-cache-1jmve30 > div {
        margin-bottom: 0.5rem;
    }

    @media (max-width: 768px) {
        .st-emotion-cache-z5fcl4 {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .st-emotion-cache-1jmve30 {
            flex-direction: column;
            gap: 0.5rem;
        }
        .st-emotion-cache-1jmve30 > div {
            width: 100% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Application Title and Introduction ---
st.title("🎓 CICS Program Recommender for Grade 12 Students")
st.markdown("---")

# --- Initialize Session State for User Selections and Session ID ---
# Use a set for selected_interests for efficient lookups and to store unique values
if 'selected_interests' not in st.session_state:
    st.session_state.selected_interests = set()
# Generate a unique session ID for the current user if one doesn't exist
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.header("1. Tell Us About Your Interests:")
st.markdown("Select all the areas that you are curious about and passionate about. The more you select, the better we can tailor the recommendations!")

# --- Interest Selection Loop ---
for category, interests in categorized_student_interests_raw.items():
    st.subheader(f"🌐 {category}")

    # Determine number of columns for better layout, up to 5
    num_cols_for_category = min(5, len(interests))
    cols = st.columns(num_cols_for_category)

    for i, interest_raw in enumerate(interests):
        display_interest = format_ontology_name(interest_raw)
        description = interest_descriptions.get(interest_raw, "No description available.")

        # Set the initial state of the checkbox based on st.session_state
        initial_checkbox_state = interest_raw in st.session_state.selected_interests
        checkbox_state = cols[i % num_cols_for_category].checkbox(
            display_interest,
            key=interest_raw, # Unique key for each checkbox
            help=description,
            value=initial_checkbox_state # Crucial for persistent checkbox state within the session
        )

        # Logic to update session_state and record selections to Supabase
        if checkbox_state and interest_raw not in st.session_state.selected_interests:
            # Add interest to session state if it was just checked
            st.session_state.selected_interests.add(interest_raw)
            try:
                # Insert the selection into the Supabase table
                supabase.table("user_selections").insert(
                    {"session_id": st.session_state.session_id, "interest": interest_raw}
                ).execute()
            except Exception as e:
                # Display an error if Supabase write fails
                st.error(f"Error saving interest to Supabase: {e}")

        elif not checkbox_state and interest_raw in st.session_state.selected_interests:
            # Remove interest from session state if it was just unchecked
            st.session_state.selected_interests.remove(interest_raw)
            # You could also implement logic here to "undo" the selection in Supabase
            # For simple analytics, often just recording selections is enough.
            pass # No Supabase removal for now for simplicity of analytics tracking

    st.markdown("---") # Separator after each category

# Convert the set of selected interests back to a list for compatibility with existing logic
selected_interests_raw = list(st.session_state.selected_interests)


# --- IMPORTANT FIX: Calculate student_derived_skills here, always ---
# Initialize it before populating
student_derived_skills = set()
for interest_raw in selected_interests_raw:
    if interest_raw in interest_to_related_skills:
        student_derived_skills.update(interest_to_related_skills[interest_raw])
# --- END IMPORTANT FIX ---


# --- 2. Personalized Program Recommendations ---
if selected_interests_raw: # This condition now primarily controls the display of program recommendations
    st.header("2. Your Personalized Program Recommendations:")

    # student_derived_skills is now already populated or remains empty, correctly
    if not student_derived_skills:
        st.warning("Please select interests that have associated skills to get recommendations. Try selecting a wider range of interests.")
    else:
        program_scores = {}
        for program_name, details in programs.items():
            score = 0
            matching_skills = []
            for skill_developed_by_program in details["skills_developed"]:
                if skill_developed_by_program in student_derived_skills:
                    score += 1
                    matching_skills.append(skill_developed_by_program)
            program_scores[program_name] = {"score": score, "matching_skills": matching_skills}

        # Filter out programs with no matching skills and sort them by score
        ranked_programs = sorted(
            [item for item in program_scores.items() if item[1]["score"] > 0],
            key=lambda item: item[1]["score"],
            reverse=True
        )

        if not ranked_programs:
            st.info("No programs strongly match your interests. Here's a summary of all CICS programs:")
            for program_name, details in programs.items():
                st.subheader(f"✨ {program_name}")
                st.write(f"**{program_name}**:  {details['description']}")
                formatted_careers = [format_ontology_name(career) for career in details['careers']]
                st.write(f"**Possible Careers**: {', '.join(formatted_careers)}")
                st.markdown("---")
        else:
            for i, (program_name, data) in enumerate(ranked_programs):
                col1, col2 = st.columns([0.7, 0.3]) # Two columns for program info and score
                with col1:
                    st.subheader(f"✨ {program_name}")
                    st.write(f"**{program_name}**: {programs[program_name]['description']}")
                with col2:
                    st.metric(label="Match Score", value=data['score']) # Display match score

                if data['matching_skills']:
                    formatted_matching_skills = [format_ontology_name(skill) for skill in data['matching_skills']]
                    st.write(f"This program is a good fit because it develops skills like:  \n\n •  " + "\n •  ".join(formatted_matching_skills) + ".")
                else:
                    st.write("This program aligns with your general interests.")

                formatted_careers = [format_ontology_name(career) for career in programs[program_name]['careers']]
                st.write(f"**Possible Careers**: {', '.join(formatted_careers)}")
                st.markdown("---")
else: # If no interests selected, just display a message for the recommendation section
    st.header("2. Your Personalized Program Recommendations:")
    st.info("Select interests above to see your personalized program recommendations!")


# --- 3. Skills You Might Enjoy Developing ---
st.header("3. Skills You Might Enjoy Developing:")
# This check now safely operates on the student_derived_skills set, which is always defined.
if student_derived_skills:
    formatted_derived_skills = [format_ontology_name(skill) for skill in sorted(list(student_derived_skills))]
    st.info(f"Based on your interests, you might enjoy developing these skills:\n\n •  " + "\n •  ".join(formatted_derived_skills))
else:
    st.info("Select some interests to see the related skills.")

st.markdown("---")
st.caption("This program provides suggestions based on your interests and the CICS curriculum.")