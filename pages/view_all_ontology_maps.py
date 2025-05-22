# view_all_ontology_maps.py
import streamlit as st
from pyvis.network import Network
from data import programs, interest_to_related_skills, careers_to_required_skills, format_ontology_name, ONTOLOGY_MAP_RAW_TO_MAIN_CLASS # Import ONTOLOGY_MAP

st.set_page_config(page_title="All CICS Program Ontology Maps", layout="wide")
st.title("📚 All CICS Program Ontology Maps")
st.markdown("Explore the detailed ontology map for each CICS program, showing connections between programs, skills, and career paths.")
st.markdown("---")

def display_ontology_graph(program_name_raw, output_html_file="graph.html"):
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", cdn_resources='remote', directed=True)
    net.set_edge_smooth('dynamic')

    nodes = set()
    edges = []

    program_display = format_ontology_name(program_name_raw)
    nodes.add((program_name_raw, program_display, "Program", "#90EE90")) # Light Green

    # Add skills developed by the program
    program_skills_developed = programs[program_name_raw]["skills_developed"]
    for skill_raw in program_skills_developed:
        skill_display = format_ontology_name(skill_raw)
        nodes.add((skill_raw, skill_display, "Skill", "#ADD8E6")) # Light Blue
        edges.append((program_name_raw, skill_raw, "develops", "#90EE90"))

        # Link skills back to interests (if known, though for full maps, it's about program relations)
        # For simplicity, we're not adding all interests directly unless they are crucial.
        # If you want to show all related interests for these skills, you would iterate through ONTOLOGY_MAP and interest_to_related_skills
        for interest_raw_key, related_skills_list in interest_to_related_skills.items():
            if skill_raw in related_skills_list:
                interest_display = format_ontology_name(interest_raw_key)
                nodes.add((interest_raw_key, interest_display, "Interest", "#FFD700")) # Gold
                edges.append((interest_raw_key, skill_raw, "relatedTo", "#FFD700"))


    # Add careers associated with the program
    program_careers = programs[program_name_raw]["careers"]
    for career_raw in program_careers:
        career_display = format_ontology_name(career_raw)
        nodes.add((career_raw, career_display, "Career", "#FFB6C1")) # Light Pink
        edges.append((program_name_raw, career_raw, "leadsTo", "#FFB6C1"))

        # Add skills required by these careers
        if career_raw in careers_to_required_skills:
            for required_skill_raw in careers_to_required_skills[career_raw]:
                required_skill_display = format_ontology_name(required_skill_raw)
                nodes.add((required_skill_raw, required_skill_display, "Skill", "#ADD8E6")) # Light Blue
                edges.append((career_raw, required_skill_raw, "requiresSkill", "#B0C4DE")) # Light Steel Blue


    # Add nodes and edges to the network
    for node_id, node_label, node_type, color in nodes:
        net.add_node(node_id, label=node_label, title=node_label, group=node_type, color=color, physics=True)

    for source, target, edge_label, color in edges:
        net.add_edge(source, target, title=edge_label, label=edge_label, color=color)

    # Set common physics options for all graphs
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


# Dropdown to select a program
st.subheader("Select a CICS Program to View its Ontology Map:")
program_options_display = {format_ontology_name(p): p for p in programs.keys()}
selected_program_display = st.selectbox(
    "Choose a Program:",
    options=[''] + sorted(list(program_options_display.keys())),
    index=0
)

if selected_program_display:
    selected_program_raw = program_options_display[selected_program_display]
    st.write(f"Displaying Ontology Map for **{selected_program_display}**")
    display_ontology_graph(selected_program_raw, f"ontology_map_{selected_program_raw}.html")
else:
    st.info("Please select a program from the dropdown to view its detailed ontology map.")

st.markdown("---")
st.caption("These maps visualize the relationships between CICS programs, the skills they develop, and the careers they lead to.")