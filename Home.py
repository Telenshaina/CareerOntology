import streamlit as st
import uuid
import datetime
from pyvis.network import Network # Make sure pyvis is in requirements.txt

from st_supabase_connection import SupabaseConnection

# UPDATED: Import ONTOLOGY_MAP_RAW_TO_MAIN_CLASS and other constants from data.py
from data import (
    categorized_student_interests_raw, programs, interest_to_related_skills,
    format_ontology_name, ONTOLOGY_MAP_RAW_TO_MAIN_CLASS, careers_to_required_skills
)
from descriptions import interest_descriptions

# Set Streamlit page configuration
st.set_page_config(page_title="CICS Program Suggester", layout="wide")

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    /* Main content padding adjustment */
    .st-emotion-cache-z5fcl4 { /* This class might change with Streamlit updates, verify with dev tools if padding looks off */
        padding-top: 1rem;
        padding-right: 3rem;
        padding-bottom: 1rem;
        padding-left: 3rem;
    }
    
    /* Columns gap for interest selection */
    .st-emotion-cache-1jmve30 { /* This class might change, verify with dev tools */
        gap: 0.75rem;
    }
    .st-emotion-cache-1jmve30 > div {
        margin-bottom: 0.5rem;
    }

    /* Responsive adjustments */
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

    /* Checkbox with tooltip styling */
    .checkbox-with-tooltip-container {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    /* Hide default Streamlit checkbox icon */
    div.stCheckbox > label > div[data-testid="stCheckbox"] > span {
        display: none;
    }

    /* Adjust checkbox input positioning */
    div.stCheckbox > label > div[data-testid="stCheckbox"] > input[type="checkbox"] {
        margin-right: 8px;
        margin-top: 0;
        flex-shrink: 0;
    }

    .custom-label-text {
        position: relative;
        cursor: pointer;
        line-height: 1.4;
        user-select: none;
    }

    .tooltip-box {
        visibility: hidden;
        opacity: 0;
        transition: opacity 0.3s ease-in-out, visibility 0.3s ease-in-out;
        
        width: 250px;
        background-color: #333;
        color: #fff;
        text-align: left;
        border-radius: 8px;
        padding: 10px 15px;
        position: absolute;
        z-index: 1000;
        bottom: 125%; /* Position above the text */
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.95em;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }

    .tooltip-box::after {
        content: "";
        position: absolute;
        top: 100%; /* Arrow at the bottom of the tooltip */
        left: 50%;
        margin-left: -8px;
        border-width: 8px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
    }

    .custom-label-text:hover .tooltip-box {
        visibility: visible;
        opacity: 1;
    }
    
    /* Hide the default Streamlit tooltip icon */
    [data-testid="stTooltipIcon"] {
        display: none;
    }

    /* Table styling for analytics dashboard (if needed, adjust if not used here) */
    .dimmed { color: #888888; } 
    table { width: 100%; border-collapse: collapse; } 
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; } 
    th { background-color: #f2f2f2; color: black; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎓 CICS Program Recommender for Grade 12 Students")
st.markdown("---")

# --- Session State Management ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'profile_complete' not in st.session_state:
    st.session_state.profile_complete = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_strand' not in st.session_state:
    st.session_state.user_strand = ""
if 'supabase_profile_id' not in st.session_state:
    st.session_state.supabase_profile_id = None

# --- User Profile Form (initial display) ---
if not st.session_state.profile_complete:
    st.header("👋 Welcome! Please tell us about yourself.")
    st.markdown("We need a little information to personalize your recommendations.")

    with st.form(key="user_profile_form"):
        user_name_input = st.text_input("Your Name", value=st.session_state.user_name, key="name_input")
        strand_options = ['STEM', 'ABM', 'HUMSS', 'GAS', 'TVL', 'Arts and Design', 'Sports', 'Other']
        user_strand_input = st.selectbox(
            "Which SHS strand are you currently taking?",
            options=[''] + strand_options, # Add an empty option for initial selection
            index=strand_options.index(st.session_state.user_strand) + 1 if st.session_state.user_strand else 0,
            key="strand_input"
        )
        
        submit_button = st.form_submit_button(label="Continue to Recommendations")

        if submit_button:
            if not user_name_input.strip():
                st.error("Please enter your name.")
            elif not user_strand_input: # Check if an option was selected from dropdown
                st.error("Please select your SHS strand.")
            else:
                st.session_state.user_name = user_name_input.strip()
                st.session_state.user_strand = user_strand_input

                try:
                    # Upsert (insert or update) the user profile
                    response = conn.table("user_profiles").upsert({
                        "session_id": st.session_state.session_id,
                        "name": st.session_state.user_name,
                        "strand": st.session_state.user_strand
                    }, on_conflict="session_id").execute()

                    if response.data and len(response.data) > 0:
                        st.session_state.supabase_profile_id = response.data[0]['id']
                    else:
                        raise Exception("Failed to retrieve profile ID after upsert.")

                    st.success("Thank you! Your information has been saved.")
                    st.session_state.profile_complete = True
                    
                    # Rerun the app to proceed to the next section
                    st.rerun() 
                except Exception as e:
                    st.error(f"Error saving your profile: {e}")
                    st.warning("Please ensure your Supabase 'user_profiles' table is correctly set up with 'session_id' as unique.")
    
    # Stop execution here if profile is not complete, to prevent showing other sections
    st.stop()

# --- Display Sidebar after Profile is Complete ---
if st.session_state.profile_complete:
    st.sidebar.markdown(f"Welcome, **{st.session_state.user_name}**!")
    st.sidebar.info(f"Your Strand: **{st.session_state.user_strand}**")

# --- Interest Selection Section ---
if 'selected_interests' not in st.session_state:
    st.session_state.selected_interests = set()

# Function to update interest selection in Supabase and session state
def update_interest_selection(interest_raw_key):
    is_checked = st.session_state[f"interest_{interest_raw_key}"]

    if st.session_state.supabase_profile_id:
        try:
            if is_checked:
                if interest_raw_key not in st.session_state.selected_interests:
                    st.session_state.selected_interests.add(interest_raw_key)

                conn.table("user_selections").insert({
                    "profile_id": st.session_state.supabase_profile_id,
                    "interest_raw": interest_raw_key,
                    "selected_at": datetime.datetime.now().isoformat() # Use ISO format for Supabase timestamp
                }).execute()
            else:
                if interest_raw_key in st.session_state.selected_interests:
                    st.session_state.selected_interests.remove(interest_raw_key)
                
                # Delete the specific selection record
                conn.table("user_selections").delete()\
                    .eq("profile_id", st.session_state.supabase_profile_id)\
                    .eq("interest_raw", interest_raw_key)\
                    .execute()
        except Exception as e:
            st.error(f"Error saving/deleting interest {format_ontology_name(interest_raw_key)}: {e}")
            print(f"DEBUG: Error saving/deleting interest {interest_raw_key}: {e}")
    else:
        # This case ideally shouldn't happen if profile_complete check works,
        # but good for debugging.
        st.warning(f"Attempted to save interest {format_ontology_name(interest_raw_key)} without profile_id. Profile not yet saved?")
        print(f"DEBUG: Attempted to save interest {interest_raw_key} without profile_id. Profile not yet saved?")


st.header("1. Tell Us About Your Interests:")
st.markdown("Select all the areas that you are curious about and passionate about.")
st.info("**Tip:** Selecting **more interests** will help us provide **more accurate and personalized** recommendations!")

# Load previously selected interests from Supabase on first run after profile is complete
if st.session_state.profile_complete and st.session_state.supabase_profile_id and not st.session_state.selected_interests:
    try:
        response = conn.table("user_selections").select("interest_raw").eq("profile_id", st.session_state.supabase_profile_id).execute()
        if response.data:
            for item in response.data:
                st.session_state.selected_interests.add(item['interest_raw'])
    except Exception as e:
        st.error(f"Error loading previous interests: {e}")
        print(f"DEBUG: Error loading previous interests: {e}")
        st.warning("Could not load your previous interest selections.")

# Display interests by category with checkboxes and tooltips
for category, interests in categorized_student_interests_raw.items():
    st.subheader(f"🌐 {category}")
    
    # Determine number of columns for layout (max 5)
    num_cols_for_category = min(5, len(interests))
    # Create columns dynamically
    cols = st.columns(num_cols_for_category)

    for i, interest_raw in enumerate(interests):
        display_interest = format_ontology_name(interest_raw)
        description = interest_descriptions.get(interest_raw, "No description available.")
        
        with cols[i % num_cols_for_category]: # Cycle through columns
            st.markdown(f'<div class="checkbox-with-tooltip-container">', unsafe_allow_html=True)
            
            # Set initial checkbox state based on session_state
            initial_checkbox_state = interest_raw in st.session_state.selected_interests
            st.checkbox(
                "", # Empty label because we're using a custom HTML label
                key=f"interest_{interest_raw}", # Unique key for each checkbox
                value=initial_checkbox_state,
                on_change=update_interest_selection, # Callback function on change
                args=(interest_raw,), # Arguments to pass to the callback
                label_visibility="hidden" # Hide default Streamlit label
            )
            
            # Custom HTML label with tooltip
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

# --- Program Recommendations Section ---
selected_interests_raw = list(st.session_state.selected_interests)

# Placeholder for smooth scrolling (if needed, useful for long pages)
st.markdown('<div id="program_recommendations_section" style="height: 0px;"></div>', unsafe_allow_html=True)

# Helper function to display pyvis graphs
def display_ontology_subgraph(nodes, edges, graph_title="Ontology Subgraph", output_html_file="graph.html"):
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", cdn_resources='remote', directed=True)
    net.set_edge_smooth('dynamic')

    # Add nodes
    for node_id, node_label, node_type, color in nodes:
        net.add_node(node_id, label=node_label, title=node_label, group=node_type, color=color, physics=True)

    # Add edges
    for source, target, edge_label, color in edges:
        net.add_edge(source, target, title=edge_label, label=edge_label, color=color)

    # Set pyvis options for physics and interaction
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -100,
          "centralGravity": 0.005,
          "springLength": 200,
          "springConstant": 0.18
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      },
      "interaction": {
        "hover": true,
        "zoomView": true
      },
      "nodes": {
        "font": {
          "size": 14,
          "color": "#ffffff"
        },
        "scaling": {
          "min": 10,
          "max": 30
        },
        "borderWidth": 2
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 0.8
          }
        },
        "font": {
            "size": 10,
            "color": "#ffffff",
            "strokeWidth": 0
        },
        "width": 1.5
      }
    }
    """)

    try:
        # Save graph to a temporary HTML file
        net.save_graph(output_html_file)
        
        # Read the HTML file and embed it
        HtmlFile = open(output_html_file, 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        st.components.v1.html(source_code, height=650, scrolling=True)
        HtmlFile.close()
    except Exception as e:
        st.error(f"Error displaying graph: {e}")
        st.info("Ensure Pyvis is installed and has write permissions to create graph.html in the deployment environment.")

# Derive skills from selected interests
student_derived_skills = set()
for interest_raw in selected_interests_raw:
    if interest_raw in interest_to_related_skills:
        student_derived_skills.update(interest_to_related_skills[interest_raw])

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

        # Filter out programs with 0 score and sort
        ranked_programs = sorted(
            [item for item in program_scores.items() if item[1]["score"] > 0],
            key=lambda item: item[1]["score"],
            reverse=True
        )

        if not ranked_programs:
            st.info("No programs strongly match your selected interests. Here's a summary of all CICS programs:")
            for program_name, details in programs.items():
                st.subheader(f"✨ {format_ontology_name(program_name)}")
                st.write(f"**Description**: {details['description']}")
                formatted_careers = [format_ontology_name(career) for career in details['careers']]
                st.write(f"**Possible Careers**: {', '.join(formatted_careers)}")
                st.markdown("---")
        else:
            for i, (program_name, data) in enumerate(ranked_programs):
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.subheader(f"✨ {format_ontology_name(program_name)}")
                    st.write(f"**Description**: {programs[program_name]['description']}")
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
                
                # Expander for program-specific ontology map
                with st.expander(f"Show Ontology Map for {format_ontology_name(program_name)}", expanded=False):
                    st.info("This interactive map shows the direct relationships of this program with relevant skills and career paths based on your interests. Drag nodes to explore!")

                    program_specific_nodes = set()
                    program_specific_edges = []

                    # Add the program itself
                    program_specific_nodes.add((program_name, format_ontology_name(program_name), "Program", "#90EE90")) # Light Green

                    # Add skills developed by this program AND selected by the user
                    for skill_raw in programs[program_name]["skills_developed"]:
                        if skill_raw in student_derived_skills: # Only show skills that match user's interests
                            skill_display = format_ontology_name(skill_raw)
                            program_specific_nodes.add((skill_raw, skill_display, "Skill", "#ADD8E6")) # Light Blue
                            program_specific_edges.append((program_name, skill_raw, "develops", "#90EE90"))

                            # Add interests that lead to this skill
                            for interest_raw_key, related_skills_list in interest_to_related_skills.items():
                                if skill_raw in related_skills_list and interest_raw_key in selected_interests_raw:
                                    interest_display = format_ontology_name(interest_raw_key)
                                    program_specific_nodes.add((interest_raw_key, interest_display, "Interest", "#FFD700")) # Gold
                                    program_specific_edges.append((interest_raw_key, skill_raw, "relatedTo", "#FFD700"))
                    # Add careers related to this program
                    for career_raw in programs[program_name]["careers"]:
                        career_display = format_ontology_name(career_raw)
                        program_specific_nodes.add((career_raw, career_display, "Career", "#FFB6C1")) # Light Pink
                        program_specific_edges.append((program_name, career_raw, "leadsTo", "#FFB6C1"))

                        # Add skills required by this career, if they are derived from user's interests
                        if career_raw in careers_to_required_skills:
                            for required_skill_raw in careers_to_required_skills[career_raw]:
                                if required_skill_raw in student_derived_skills: # Only show skills that match user's interests
                                    required_skill_display = format_ontology_name(required_skill_raw)
                                    program_specific_nodes.add((required_skill_raw, required_skill_display, "Skill", "#ADD8E6")) # Light Blue
                                    program_specific_edges.append((career_raw, required_skill_raw, "requiresSkill", "#B0C4DE")) # Light Steel Blue


                    if program_specific_nodes:
                        display_ontology_subgraph(list(program_specific_nodes), program_specific_edges,
                                                f"Map for {format_ontology_name(program_name)}", f"program_map_{program_name}.html")
                    else:
                        st.info(f"No detailed ontology map to display for {format_ontology_name(program_name)} based on your selections. Try selecting more interests.")

                st.markdown("<br><br>", unsafe_allow_html=True)


else:
    st.header("2. Your Personalized Program Recommendations:")
    st.info("Select interests above to see your personalized program recommendations!")

# --- Skills You Might Enjoy Developing Section ---
st.header("3. Skills You Might Enjoy Developing:")
if student_derived_skills:
    formatted_derived_skills = [format_ontology_name(skill) for skill in sorted(list(student_derived_skills))]
    st.info(f"Based on your interests, you might enjoy developing these skills:\n\n •  " + "\n •  ".join(formatted_derived_skills))
    
    with st.expander("Show Ontology Map for Your Skills", expanded=False):
        st.info("This interactive map shows how your selected interests, derived skills, and relevant programs/careers are connected.")

        nodes_for_skills_map = set()
        edges_for_skills_map = []

        # Add all selected interests as nodes
        for interest_raw in selected_interests_raw:
            interest_display = format_ontology_name(interest_raw)
            nodes_for_skills_map.add((interest_raw, interest_display, "Interest", "#FFD700")) # Gold

            # Link interests to their related skills
            if interest_raw in interest_to_related_skills:
                for skill_raw in interest_to_related_skills[interest_raw]:
                    skill_display = format_ontology_name(skill_raw)
                    nodes_for_skills_map.add((skill_raw, skill_display, "Skill", "#ADD8E6")) # Light Blue
                    edges_for_skills_map.append((interest_raw, skill_raw, "relatedTo", "#FFD700"))

                    # Link skills to programs that develop them
                    for program_name, details in programs.items():
                        if skill_raw in details["skills_developed"]:
                            program_display = format_ontology_name(program_name)
                            nodes_for_skills_map.add((program_name, program_display, "Program", "#90EE90")) # Light Green
                            edges_for_skills_map.append((program_name, skill_raw, "develops", "#90EE90"))

                    # Link skills to careers that require them
                    for career_raw, required_skills_list in careers_to_required_skills.items():
                        if skill_raw in required_skills_list:
                            career_display = format_ontology_name(career_raw)
                            nodes_for_skills_map.add((career_raw, career_display, "Career", "#FFB6C1")) # Light Pink
                            edges_for_skills_map.append((career_raw, skill_raw, "requiresSkill", "#B0C4DE"))
                            
                            # Also link careers to programs that lead to them (if not already added)
                            for program_name, details in programs.items():
                                if career_raw in details["careers"]:
                                    program_display = format_ontology_name(program_name)
                                    nodes_for_skills_map.add((program_name, program_display, "Program", "#90EE90")) # Light Green
                                    edges_for_skills_map.append((program_name, career_raw, "leadsTo", "#FFB6C1"))


        if nodes_for_skills_map:
            display_ontology_subgraph(list(nodes_for_skills_map), edges_for_skills_map, "Your Skills Map", "skills_map.html")
        else:
            st.info("No connections to display in the ontology map based on your selected skills.")

st.markdown("---")
st.caption("This program provides suggestions based on your interests and the CICS curriculum.")

# --- Link to All Programs Page ---
st.sidebar.markdown("---")
st.sidebar.subheader("Explore CICS Programs")
if st.sidebar.button("View All Program Ontology Maps"):
    st.switch_page("pages/view_all_ontology_maps.py") # Ensure this path is correct relative to your main app