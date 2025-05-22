import streamlit as st
import uuid
import datetime
from pyvis.network import Network

from st_supabase_connection import SupabaseConnection

from data import categorized_student_interests_raw, programs, interest_to_related_skills, format_ontology_name
from descriptions import interest_descriptions

ONTOLOGY_MAP_RAW_TO_MAIN_CLASS = {
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
    "Digital_Art": "Digital Art & Illustration",
    "Digital_Painting": "Digital Art & Illustration",

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

careers_to_required_skills = {
    "Software_Engineer": ["Building_Program_Logic", "Organizing_Data_in_Programs", "Writing_Code"],
    "Frontend_Developer": ["Making_Websites", "Designing_User_Interfaces_Code"],
    "Backend_Developer": ["Building_System_Backbones", "Managing_Databases_with_Code"],
    "Fullstack_Developer": ["Making_Websites", "Building_System_Backbones", "Writing_Code"],
    "Mobile_App_Developer": ["Creating_Mobile_Apps", "Writing_Code"],
    "AI_ML_Engineer": ["Teaching_Computers_to_Learn", "Analyzing_Data_with_Code"],
    "Data_Scientist": ["Analyzing_Data_with_Code", "Understanding_Statistics"],
    "Game_Programmer": ["Building_Games_Code", "Writing_Code"],
    "DevOps_Engineer": ["Building_System_Backbones", "Setting_Up_Networks", "Handling_Cloud_Systems"],
    "Cloud_Developer": ["Handling_Cloud_Systems", "Building_System_Backbones"],
    "Embedded_Systems_Developer": ["Programming_Small_Computers", "Designing_Circuits"],
    "Cybersecurity_Developer": ["Basic_Online_Security", "Writing_Code"],

    "IT_Support_Specialist": ["Fixing_Tech_Problems", "Managing_Computer_Systems"],
    "Network_Administrator": ["Setting_Up_Networks", "Securing_Networks"],
    "System_Administrator": ["Managing_Computer_Systems", "Managing_Operating_Systems"],
    "Cloud_Administrator": ["Handling_Cloud_Systems", "Setting_Up_Virtual_Computers"],
    "Database_Administrator": ["Managing_Databases_Admin", "Organizing_Data_in_Programs"],
    "Cybersecurity_Analyst": ["Basic_Online_Security", "Responding_to_Security_Issues"],
    "IT_Consultant": ["Logical_Problem_Solving", "Talking_to_Stakeholders"],
    "Help_Desk_Technician": ["Fixing_Tech_Problems", "Talking_to_Stakeholders"],

    "Multimedia_Artist": ["Creating_Graphics_and_Art", "Editing_Videos"],
    "UX_UI_Designer": ["Designing_User_Experience", "Designing_User_Interface"],
    "Graphic_Designer": ["Creating_Graphics_and_Art", "Digital_Painting"],
    "2D_Animator": ["Making_2D_Animations", "Digital_Painting"],
    "3D_Artist_Modeler": ["Creating_3D_Models", "Setting_Up_Characters_for_Animation"],
    "Video_Editor": ["Editing_Videos", "Making_Motion_Graphics"],
    "Motion_Graphics_Designer": ["Making_Motion_Graphics", "Creating_Graphics_and_Art"],
    "Concept_Artist": ["Developing_Concept_Art", "Digital_Painting"],
    "Digital_Illustrator": ["Digital_Painting", "Digital_Illustration"],
    "Web_Designer": ["Making_Websites", "Designing_User_Interface"],

    "Data_Analyst": ["Collecting_Data", "Cleaning_and_Preparing_Data", "Understanding_Statistics"],
    "Business_Intelligence_Analyst": ["Presenting_Data_Visually", "Analyzing_Markets"],
    "Database_Developer": ["Managing_Databases_with_Code", "Organizing_Data_in_Programs"],
    "Big_Data_Engineer": ["Working_with_Huge_Amounts_of_Data", "Managing_Databases_with_Code"],

    "Project_Manager": ["Planning_and_Leading_Projects", "Using_Agile_Methods"],
    "Business_Analyst": ["Gathering_Requirements", "Mapping_Business_Processes"],
    "Systems_Analyst": ["Logical_Problem_Solving", "Gathering_Requirements"],
    "IT_Project_Manager": ["Planning_and_Leading_Projects", "Spotting_and_Handling_Risks"],
    "Operations_Manager": ["Mapping_Business_Processes", "Planning_and_Leading_Projects"],
    "Product_Manager": ["Analyzing_Markets", "Making_Business_Strategies"],
    "Entrepreneur": ["Making_Business_Strategies", "Running_Digital_Marketing"],

    "Game_Developer": ["Building_Games_Code", "Designing_Game_Rules"],
    "Game_Designer": ["Designing_Game_Rules", "Building_Game_Levels"],
    "Level_Designer": ["Building_Game_Levels", "Creating_Game_Stories"],
    "Game_Tester": ["Testing_Games", "Logical_Problem_Solving"],
    "Game_Producer": ["Planning_and_Leading_Projects", "Talking_to_Stakeholders"],
    "Esports_Manager": ["Planning_and_Leading_Projects", "Running_Digital_Marketing"],

    "Robotics_Engineer": ["Controlling_Robots", "Programming_Small_Computers"],
    "Hardware_Engineer": ["Designing_Circuits", "Assembling_and_Fixing_Hardware"],
    "IoT_Developer": ["Connecting_Smart_Devices_IoT", "Programming_Small_Computers"],
    "Electronics_Engineer": ["Designing_Circuits", "Assembling_and_Fixing_Hardware"],

    "Technical_Writer": ["Writing_Technical_Guides", "Crafting_Digital_Stories"],
    "Digital_Content_Creator": ["Crafting_Digital_Stories", "Developing_Content_Plans"],
    "Digital_Marketing_Specialist": ["Running_Digital_Marketing", "Developing_Content_Plans"],
    "SEO_Specialist": ["Running_Digital_Marketing", "Analyzing_Markets"],
    "Social_Media_Manager": ["Developing_Content_Plans", "Crafting_Digital_Stories"],

    "IT_Researcher": ["Doing_Research", "Learning_New_Technologies"],
    "Academic_Programmer": ["Building_Program_Logic", "Writing_Code"],
    "Technology_Consultant": ["Logical_Problem_Solving", "Learning_New_Technologies"],
}


st.set_page_config(page_title="CICS Program Suggester", layout="wide")

conn = st.connection("supabase", type=SupabaseConnection)

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

    .checkbox-with-tooltip-container {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    div.stCheckbox > label > div[data-testid="stCheckbox"] > span {
        display: none;
    }

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
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.95em;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }

    .tooltip-box::after {
        content: "";
        position: absolute;
        top: 100%;
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
    
    [data-testid="stTooltipIcon"] {
        display: none;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎓 CICS Program Recommender for Grade 12 Students")
st.markdown("---")

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
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving your profile: {e}")
                    st.warning("Please ensure your Supabase 'user_profiles' table is correctly set up.")
    
    st.stop()

if st.session_state.profile_complete:
    st.sidebar.markdown(f"Welcome, **{st.session_state.user_name}**!")
    st.sidebar.info(f"Your Strand: **{st.session_state.user_strand}**")

if 'selected_interests' not in st.session_state:
    st.session_state.selected_interests = set()

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
                    "selected_at": datetime.datetime.now().isoformat()
                }).execute()
            else:
                if interest_raw_key in st.session_state.selected_interests:
                    st.session_state.selected_interests.remove(interest_raw_key)
                
                conn.table("user_selections").delete()\
                    .eq("profile_id", st.session_state.supabase_profile_id)\
                    .eq("interest_raw", interest_raw_key)\
                    .execute()
        except Exception as e:
            print(f"Error saving/deleting interest {interest_raw_key}: {e}")
    else:
        print(f"Attempted to save interest {interest_raw_key} without profile_id. Profile not yet saved?")


st.header("1. Tell Us About Your Interests:")
st.markdown("Select all the areas that you are curious about and passionate about.")
st.info("**Tip:** Selecting **more interests** will help us provide **more accurate and personalized** recommendations!")


if st.session_state.profile_complete and st.session_state.supabase_profile_id and not st.session_state.selected_interests:
    try:
        response = conn.table("user_selections").select("interest_raw").eq("profile_id", st.session_state.supabase_profile_id).execute()
        if response.data:
            for item in response.data:
                st.session_state.selected_interests.add(item['interest_raw'])
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
                key=f"interest_{interest_raw}",
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

selected_interests_raw = list(st.session_state.selected_interests)

st.markdown('<div id="program_recommendations_section" style="height: 0px;"></div>', unsafe_allow_html=True)

def display_ontology_subgraph(nodes, edges, graph_title="Ontology Subgraph", output_html_file="graph.html"):
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", cdn_resources='remote', directed=True)
    net.set_edge_smooth('dynamic')

    for node_id, node_label, node_type, color in nodes:
        net.add_node(node_id, label=node_label, title=node_label, group=node_type, color=color, physics=True)

    for source, target, edge_label, color in edges:
        net.add_edge(source, target, title=edge_label, label=edge_label, color=color)

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
        net.save_graph(output_html_file)
        
        HtmlFile = open(output_html_file, 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        st.components.v1.html(source_code, height=650, scrolling=True)
        HtmlFile.close()
    except Exception as e:
        st.error(f"Error displaying graph: {e}")
        st.info("Ensure Pyvis is installed and has write permissions to create graph.html.")


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

        ranked_programs = sorted(
            [item for item in program_scores.items() if item[1]["score"] > 0],
            key=lambda item: item[1]["score"],
            reverse=True
        )

        if not ranked_programs:
            st.info("No programs strongly match your interests. Here's a summary of all CICS programs:")
            for program_name, details in programs.items():
                st.subheader(f"✨ {format_ontology_name(program_name)}")
                st.write(f"**{format_ontology_name(program_name)}**:  {details['description']}")
                formatted_careers = [format_ontology_name(career) for career in details['careers']]
                st.write(f"**Possible Careers**: {', '.join(formatted_careers)}")
                st.markdown("---")
        else:
            for i, (program_name, data) in enumerate(ranked_programs):
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.subheader(f"✨ {format_ontology_name(program_name)}")
                    st.write(f"**{format_ontology_name(program_name)}**: {programs[program_name]['description']}")
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
                
                with st.expander(f"Show Ontology Map for {format_ontology_name(program_name)}", expanded=False):
                    st.info("This interactive map shows the direct relationships of this program with relevant skills and career paths based on your interests. Drag nodes to explore!")

                    program_specific_nodes = set()
                    program_specific_edges = []

                    program_display = format_ontology_name(program_name)
                    program_specific_nodes.add((program_name, program_display, "Program", "#90EE90"))

                    for skill_raw in programs[program_name]["skills_developed"]:
                        if skill_raw in student_derived_skills:
                            skill_display = format_ontology_name(skill_raw)
                            program_specific_nodes.add((skill_raw, skill_display, "Skill", "#ADD8E6"))
                            program_specific_edges.append((program_name, skill_raw, "develops", "#90EE90"))

                            for interest_raw_key, related_skills_list in interest_to_related_skills.items():
                                if skill_raw in related_skills_list and interest_raw_key in selected_interests_raw:
                                    interest_display = format_ontology_name(interest_raw_key)
                                    program_specific_nodes.add((interest_raw_key, interest_display, "Interest", "#FFD700"))
                                    program_specific_edges.append((interest_raw_key, skill_raw, "relatedTo", "#FFD700"))

                    for career_raw in programs[program_name]["careers"]:
                        career_display = format_ontology_name(career_raw)
                        program_specific_nodes.add((career_raw, career_display, "Career", "#FFB6C1"))
                        program_specific_edges.append((program_name, career_raw, "leadsTo", "#FFB6C1"))

                        if career_raw in careers_to_required_skills:
                            for required_skill_raw in careers_to_required_skills[career_raw]:
                                if required_skill_raw in student_derived_skills:
                                    required_skill_display = format_ontology_name(required_skill_raw)
                                    program_specific_nodes.add((required_skill_raw, required_skill_display, "Skill", "#ADD8E6"))
                                    program_specific_edges.append((career_raw, required_skill_raw, "requiresSkill", "#B0C4DE"))

                    if program_specific_nodes:
                        display_ontology_subgraph(list(program_specific_nodes), program_specific_edges,
                                                f"Map for {program_display}", f"program_map_{program_name}.html")
                    else:
                        st.info(f"No detailed ontology map to display for {program_display} based on your selections.")

                st.markdown("<br><br>", unsafe_allow_html=True)


else:
    st.header("2. Your Personalized Program Recommendations:")
    st.info("Select interests above to see your personalized program recommendations!")

st.header("3. Skills You Might Enjoy Developing:")
if student_derived_skills:
    formatted_derived_skills = [format_ontology_name(skill) for skill in sorted(list(student_derived_skills))]
    st.info(f"Based on your interests, you might enjoy developing these skills:\n\n •  " + "\n •  ".join(formatted_derived_skills))
    
    with st.expander("Show Ontology Map for Your Skills", expanded=False):
        st.info("This interactive map shows how your selected interests, derived skills, and relevant programs/careers are connected.")

        nodes_for_skills_map = set()
        edges_for_skills_map = []

        for interest_raw in selected_interests_raw:
            interest_display = format_ontology_name(interest_raw)
            nodes_for_skills_map.add((interest_raw, interest_display, "Interest", "#FFD700"))

            if interest_raw in interest_to_related_skills:
                for skill_raw in interest_to_related_skills[interest_raw]:
                    skill_display = format_ontology_name(skill_raw)
                    nodes_for_skills_map.add((skill_raw, skill_display, "Skill", "#ADD8E6"))
                    edges_for_skills_map.append((interest_raw, skill_raw, "relatedTo", "#FFD700"))

                    for program_name, details in programs.items():
                        if skill_raw in details["skills_developed"]:
                            program_display = format_ontology_name(program_name)
                            nodes_for_skills_map.add((program_name, program_display, "Program", "#90EE90"))
                            edges_for_skills_map.append((program_name, skill_raw, "develops", "#90EE90"))

                    for career_raw, required_skills_list in careers_to_required_skills.items():
                        if skill_raw in required_skills_list:
                            career_display = format_ontology_name(career_raw)
                            nodes_for_skills_map.add((career_raw, career_display, "Career", "#FFB6C1"))
                            edges_for_skills_map.append((career_raw, skill_raw, "requiresSkill", "#B0C4DE"))
                            
                            for program_name, details in programs.items():
                                if career_raw in details["careers"] and program_name not in [n[0] for n in nodes_for_skills_map]:
                                    program_display = format_ontology_name(program_name)
                                    nodes_for_skills_map.add((program_name, program_display, "Program", "#90EE90"))
                                    edges_for_skills_map.append((program_name, career_raw, "leadsTo", "#FFB6C1"))


        if nodes_for_skills_map:
            display_ontology_subgraph(list(nodes_for_skills_map), edges_for_skills_map, "Your Skills Map", "skills_map.html")
        else:
            st.info("No connections to display in the ontology map based on your selected skills.")

st.markdown("---")
st.caption("This program provides suggestions based on your interests and the CICS curriculum.")