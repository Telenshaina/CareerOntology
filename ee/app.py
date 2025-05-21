import streamlit as st
from data import categorized_student_interests_raw, programs, interest_to_related_skills, format_ontology_name
from descriptions import interest_descriptions

st.set_page_config(page_title="CICS Program Suggester", layout="wide")

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

st.title("🎓 CICS Program Recommender for Grade 12 Students")
st.markdown("---")

st.header("1. Tell Us About Your Interests:")
st.markdown("Select all the areas that you are curious about and passionate about. The more you select, the better we can tailor the recommendations!")

selected_interests_raw = []

for category, interests in categorized_student_interests_raw.items():
    st.subheader(f"🌐 {category}")
    
    num_cols_for_category = min(5, len(interests))
    cols = st.columns(num_cols_for_category)

    for i, interest_raw in enumerate(interests):
        display_interest = format_ontology_name(interest_raw)
        description = interest_descriptions.get(interest_raw, "No description available.")
        
        with cols[i % num_cols_for_category]:
            checkbox_state = st.checkbox(display_interest, key=interest_raw, help=description)
            if checkbox_state:
                selected_interests_raw.append(interest_raw)

    st.markdown("---")

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