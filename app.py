import streamlit as st
from data import categorized_student_interests_raw, programs, interest_to_related_skills, format_ontology_name
from descriptions import interest_descriptions

st.set_page_config(page_title="CICS Program Suggester", layout="wide")

if 'selected_interests' not in st.session_state:
    st.session_state.selected_interests = []

st.markdown(
    """
    <style>
    .st-emotion-cache-z5fcl4 {
        padding-top: 1rem;
        padding-right: 3rem;
        padding-bottom: 1rem;
        padding-left: 3rem;
    }
    
    .st-emotion-cache-1jmve30 > div {
        margin-bottom: 0.5rem;
    }

    /* Container for a single checkbox + custom label/tooltip */
    .checkbox-with-tooltip-container {
        display: flex; /* Use flexbox to align checkbox and custom label text */
        align-items: center; /* Vertically center them */
        margin-bottom: 0.5rem; /* Space between each item */
    }

    /* Hide the default Streamlit checkbox label (the text "hidden") */
    /* Target the span element that holds the visible label text of Streamlit's native checkbox */
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
    /* Only hover over the custom-label-text itself to show the tooltip */
    .custom-label-text:hover .tooltip-box {
        visibility: visible;
        opacity: 1;
    }
    
    /* Hide the default Streamlit tooltip icon (?) if it appears anywhere */
    [data-testid="stTooltipIcon"] {
        display: none;
    }

    /* Media queries for responsiveness on smaller screens (e.g., mobile) */
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
        .tooltip-box {
            display: none !important; /* Hide tooltips on mobile to avoid awkward popups */
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎓 CICS Program Recommender for Grade 12 Students")
st.markdown("---")

st.header("1. Tell Us About Your Interests:")
st.markdown("Select all the areas that you are curious about and passionate about. The more you select, the better we can tailor the recommendations!")

def update_interest_selection(interest_raw_key):
    if st.session_state[interest_raw_key]:
        if interest_raw_key not in st.session_state.selected_interests:
            st.session_state.selected_interests.append(interest_raw_key)
    else:
        if interest_raw_key in st.session_state.selected_interests:
            st.session_state.selected_interests.remove(interest_raw_key)

for category, interests in categorized_student_interests_raw.items():
    st.subheader(f"🌐 {category}")
    
    num_cols_for_category = min(5, len(interests))
    cols = st.columns(num_cols_for_category)

    for i, interest_raw in enumerate(interests):
        display_interest = format_ontology_name(interest_raw)
        description = interest_descriptions.get(interest_raw, "No description available.")
        
        is_checked = interest_raw in st.session_state.selected_interests

        with cols[i % num_cols_for_category]:
            # Use a custom div to wrap both the native Streamlit checkbox and its custom label
            st.markdown(f'<div class="checkbox-with-tooltip-container">', unsafe_allow_html=True)
            
            # 1. Native Streamlit checkbox: Handles the actual state management
            #    - label="" makes its own label empty.
            #    - key=interest_raw links it directly to the unique interest ID.
            #    - value=is_checked sets its initial state.
            #    - on_change=update_interest_selection calls our function when clicked.
            #    - label_visibility="hidden" fully hides its default Streamlit label and related padding.
            st.checkbox(
                "",
                key=interest_raw,
                value=is_checked,
                on_change=update_interest_selection,
                args=(interest_raw,),
                label_visibility="hidden"
            )
            
            # 2. Custom HTML for the label text with the hover tooltip
            st.markdown(
                f"""
                <span class="custom-label-text">
                    {display_interest}
                    <span class="tooltip-box">{description}</span>
                </span>
                """,
                unsafe_allow_html=True
            )
            
            # Close the container div for this checkbox+label pair
            st.markdown(f'</div>', unsafe_allow_html=True) 

    st.markdown("---")

selected_interests_raw = st.session_state.selected_interests

if selected_interests_raw:
    st.header("2. Your Personalized Program Recommendations:")

    student_derived_skills = set()
    for interest_raw in selected_interests_raw:
        if interest_raw in interest_to_related_skills:
            student_derived_skills.update(interest_to_related_skills[interest_raw])

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

    st.header("3. Skills You Might Enjoy Developing:")
    if student_derived_skills:
        formatted_derived_skills = [format_ontology_name(skill) for skill in sorted(list(student_derived_skills))]
        st.info(f"Based on your interests, you might enjoy developing these skills:\n\n •  " + "\n •  ".join(formatted_derived_skills))
    else:
        st.info("Select some interests to see the related skills.")

    st.markdown("---")
    st.caption("This program provides suggestions based on your interests and the CICS curriculum.")
