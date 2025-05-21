import streamlit as st
import uuid
import datetime

# --- Third-Party Imports ---
from st_supabase_connection import SupabaseConnection

# --- Local Imports (assuming these files are in the same directory) ---
from data import categorized_student_interests_raw, programs, interest_to_related_skills, format_ontology_name
from descriptions import interest_descriptions

st.set_page_config(page_title="CICS Program Suggester", layout="wide")

# --- Supabase Initialization ---
# It automatically reads [connections.supabase] from .streamlit/secrets.toml
conn = st.connection("supabase", type=SupabaseConnection)

# --- Custom CSS for Layout Adjustments (kept as is) ---
st.markdown(
    """
    <style>
    .st-emotion-cache-z5fcl4 { /* Main content area padding */
        padding-top: 1rem;
        padding-right: 3rem;
        padding-bottom: 1rem;
        padding-left: 3rem;
    }
    
    /* Column spacing for checkboxes */
    .st-emotion-cache-1jmve30 {
        gap: 0.75rem;
    }
    .st-emotion-cache-1jmve30 > div {
        margin-bottom: 0.5rem;
    }

    /* Responsive adjustments for smaller screens */
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

    /* Styles for checkbox and tooltip */
    /* Container for a single checkbox + custom label/tooltip */
    .checkbox-with-tooltip-container {
        display: flex; /* Use flexbox to align checkbox and custom label text */
        align-items: center; /* Vertically center them */
        margin-bottom: 0.5rem; /* Space between each item */
    }

    /* Hide the default Streamlit checkbox label (the text "hidden") */
    div.stCheckbox > label > div[data-testid="stCheckbox"] > span {
        display: none;
    }

    /* Style the actual checkbox input itself to align it */
    div.stCheckbox > label > div[data-testid="stCheckbox"] > input[type="checkbox"] {
        margin-right: 8px; /* Space between checkbox and custom label */
        margin-top: 0; /* Align perfectly */
        flex-shrink: 0; /* Prevent the checkbox from shrinking */
    }

    /* Style for the custom text that acts as the label and has the tooltip */
    .custom-label-text {
        position: relative; /* Essential for tooltip positioning */
        cursor: pointer; /* Indicates it's interactive */
        line-height: 1.4; /* Improve readability */
        user-select: none; /* Prevent text selection on click/hover */
    }

    /* Tooltip Styles - The pop-up box with descriptions */
    .tooltip-box {
        visibility: hidden; /* Hidden by default */
        opacity: 0; /* Start fully transparent */
        transition: opacity 0.3s ease-in-out, visibility 0.3s ease-in-out; /* Smooth fade-in/out */
        
        width: 250px; /* Width of the tooltip box */
        background-color: #333; /* Dark background */
        color: #fff; /* White text */
        text-align: left; /* Align text to the left */
        border-radius: 8px; /* Rounded corners */
        padding: 10px 15px; /* Internal padding */
        position: absolute; /* Position relative to .custom-label-text */
        z-index: 1000; /* Ensure it appears on top of other elements */
        bottom: 125%; /* Position above the text */
        left: 50%;
        transform: translateX(-50%); /* Center the tooltip horizontally */
        font-size: 0.95em; /* Slightly larger font than default */
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3); /* Subtle shadow for depth */
    }

    /* Tooltip arrow - little triangle pointing down from the box */
    .tooltip-box::after {
        content: "";
        position: absolute;
        top: 100%; /* At the bottom of the tooltip box */
        left: 50%;
        margin-left: -8px; /* Center the arrow */
        border-width: 8px; /* Size of the arrow */
        border-style: solid;
        border-color: #333 transparent transparent transparent; /* Arrow color matching background */
    }

    /* Show the tooltip box when hovering over the custom label text */
    .custom-label-text:hover .tooltip-box {
        visibility: visible;
        opacity: 1;
    }
    
    /* Hide the default Streamlit tooltip icon (?) if it appears anywhere */
    [data-testid="stTooltipIcon"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎓 CICS Program Recommender for Grade 12 Students")
st.markdown("---")

# --- Initialize Session State for User/Session Management ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4()) # Unique ID for each session
if 'profile_complete' not in st.session_state:
    st.session_state.profile_complete = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_strand' not in st.session_state:
    st.session_state.user_strand = ""
# NEW: Store the actual profile_id from Supabase
if 'supabase_profile_id' not in st.session_state:
    st.session_state.supabase_profile_id = None # Will store the UUID from Supabase

# --- Profile Collection (Required before proceeding) ---
# This block runs ONLY if profile_complete is False
if not st.session_state.profile_complete:
    st.header("👋 Welcome! Please tell us about yourself.")
    st.markdown("We need a little information to personalize your recommendations.")

    with st.form(key="user_profile_form"):
        user_name_input = st.text_input("Your Name", value=st.session_state.user_name, key="name_input")
        strand_options = ['STEM', 'ABM', 'HUMSS', 'GAS', 'TVL', 'Arts and Design', 'Sports', 'Other']
        user_strand_input = st.selectbox(
            "Which SHS strand are you currently taking?",
            options=[''] + strand_options,
            index=strand_options.index(st.session_state.user_strand) + 1 if st.session_state.user_strand else 0,
            key="strand_input"
        )
        
        submit_button = st.form_submit_button(label="Continue to Recommendations")

        if submit_button:
            if not user_name_input.strip():
                st.error("Please enter your name.")
            elif not user_strand_input:
                st.error("Please select your SHS strand.")
            else:
                st.session_state.user_name = user_name_input.strip()
                st.session_state.user_strand = user_strand_input

                try:
                    # MODIFIED: Use upsert() to prevent duplicates and capture the 'id'
                    response = conn.table("user_profiles").upsert({
                        "session_id": st.session_state.session_id,
                        "name": st.session_state.user_name,
                        "strand": st.session_state.user_strand
                    }, on_conflict="session_id").execute() # Upsert based on session_id

                    # NEW: Extract the ID of the inserted/updated profile
                    if response.data and len(response.data) > 0:
                        st.session_state.supabase_profile_id = response.data[0]['id']
                        print(f"Supabase Profile ID: {st.session_state.supabase_profile_id}")
                    else:
                        raise Exception("Failed to retrieve profile ID after upsert.")

                    st.success("Thank kindness! Your information has been saved.")
                    st.session_state.profile_complete = True
                    
                    st.rerun() # Rerun to hide the form and show the recommender
                except Exception as e:
                    st.error(f"Error saving your profile: {e}")
                    # With RLS disabled, this error suggests a schema mismatch or connectivity issue
                    st.warning("Please ensure your Supabase 'user_profiles' table is correctly set up.")
    
    st.stop() # Stop further execution until profile is complete

# Display user info once profile is complete (optional, in sidebar)
if st.session_state.profile_complete:
    st.sidebar.markdown(f"Welcome, **{st.session_state.user_name}**!")
    st.sidebar.info(f"Your Strand: **{st.session_state.user_strand}**")
    # NEW: Optionally display the Supabase profile ID for debugging
    # st.sidebar.caption(f"Profile ID: {st.session_state.supabase_profile_id}")

# --- Initialize Session State for User Selections (Interests) ---
if 'selected_interests' not in st.session_state:
    st.session_state.selected_interests = set() # Using a set for efficient adds/removes

# --- Interest Selection Logic ---
def update_interest_selection(interest_raw_key):
    is_checked = st.session_state[f"interest_{interest_raw_key}"]

    # NEW: Save selection to Supabase (user_selections table) using profile_id
    if st.session_state.supabase_profile_id: # Only attempt to save if profile ID is known
        try:
            if is_checked:
                # Add to session state set
                if interest_raw_key not in st.session_state.selected_interests:
                    st.session_state.selected_interests.add(interest_raw_key)

                # Insert into Supabase user_selections
                conn.table("user_selections").insert({
                    "profile_id": st.session_state.supabase_profile_id, # <-- Using profile_id here
                    "interest_raw": interest_raw_key,
                    "selected_at": datetime.datetime.now().isoformat() # ISO format for timestamp
                }).execute()
                # st.toast(f"Selected: {format_ontology_name(interest_raw_key)}") # Optional toast
            else:
                # Remove from session state set
                if interest_raw_key in st.session_state.selected_interests:
                    st.session_state.selected_interests.remove(interest_raw_key)
                
                # Delete from Supabase user_selections
                conn.table("user_selections").delete()\
                    .eq("profile_id", st.session_state.supabase_profile_id)\
                    .eq("interest_raw", interest_raw_key)\
                    .execute()
                # st.toast(f"Deselected: {format_ontology_name(interest_raw_key)}") # Optional toast

        except Exception as e:
            print(f"Error saving/deleting interest {interest_raw_key}: {e}")
            # st.warning(f"Could not save selection for {format_ontology_name(interest_raw_key)}")
    else:
        print(f"Attempted to save interest {interest_raw_key} without profile_id. Profile not yet saved?")


st.header("1. Tell Us About Your Interests:")
st.markdown("Select all the areas that you are curious about and passionate about. The more you select, the better we can tailor the recommendations!")

# NEW: Load previous selections from Supabase on first run (optional but good UX)
if st.session_state.profile_complete and st.session_state.supabase_profile_id and not st.session_state.selected_interests:
    try:
        # Fetch previous selections for the current profile
        response = conn.table("user_selections").select("interest_raw").eq("profile_id", st.session_state.supabase_profile_id).execute()
        if response.data:
            for item in response.data:
                st.session_state.selected_interests.add(item['interest_raw'])
        print(f"Loaded {len(st.session_state.selected_interests)} interests from Supabase.")
    except Exception as e:
        print(f"Error loading previous interests: {e}")
        st.warning("Could not load your previous interest selections.")


for category, interests in categorized_student_interests_raw.items():
    st.subheader(f"🌐 {category}")
    
    num_cols_for_category = min(5, len(interests))
    cols = st.columns(num_cols_for_category)

    for i, interest_raw in enumerate(interests):
        display_interest = format_ontology_name(interest_raw)
        description = interest_descriptions.get(interest_raw, "No description available.")
        
        with cols[i % num_cols_for_category]:
            st.markdown(f'<div class="checkbox-with-tooltip-container">', unsafe_allow_html=True)
            
            initial_checkbox_state = interest_raw in st.session_state.selected_interests
            st.checkbox(
                "",
                key=f"interest_{interest_raw}", # Use a unique key for each checkbox
                value=initial_checkbox_state,
                on_change=update_interest_selection,
                args=(interest_raw,),
                label_visibility="hidden"
            )
            
            st.markdown(
                f"""
                <span class="custom-label-text">
                    {display_interest}
                    <span class="tooltip-box">{description}</span>
                </span>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(f'</div>', unsafe_allow_html=True)

st.markdown("---")

selected_interests_raw = list(st.session_state.selected_interests) # Convert set back to list for processing

# --- Calculate student_derived_skills (Always defined and calculated here) ---
student_derived_skills = set()
for interest_raw in selected_interests_raw:
    if interest_raw in interest_to_related_skills:
        student_derived_skills.update(interest_to_related_skills[interest_raw])

# --- 2. Personalized Program Recommendations ---
if selected_interests_raw:
    st.header("2. Your Personalized Program Recommendations:")

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
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.subheader(f"✨ {program_name}")
                    st.write(f"**{program_name}**: {programs[program_name]['description']}")
                with col2:
                    st.metric(label="Match Score", value=data['score'])

                if data['matching_skills']:
                    formatted_matching_skills = [format_ontology_name(skill) for skill in data['matching_skills']]
                    st.write(f"This program is a good fit because it develops skills like:  \n\n •  " + "\n •  ".join(formatted_matching_skills) + ".")
                else:
                    st.write("This program aligns with your general interests.")

                formatted_careers = [format_ontology_name(career) for career in programs[program_name]['careers']]
                st.write(f"**Possible Careers**: {', '.join(formatted_careers)}")
                st.markdown("---")
else:
    st.header("2. Your Personalized Program Recommendations:")
    st.info("Select interests above to see your personalized program recommendations!")

# --- 3. Skills You Might Enjoy Developing ---
st.header("3. Skills You Might Enjoy Developing:")
if student_derived_skills:
    formatted_derived_skills = [format_ontology_name(skill) for skill in sorted(list(student_derived_skills))]
    st.info(f"Based on your interests, you might enjoy developing these skills:\n\n •  " + "\n •  ".join(formatted_derived_skills))
else:
    st.info("Select some interests to see the related skills.")

st.markdown("---")
st.caption("This program provides suggestions based on your interests and the CICS curriculum.")
