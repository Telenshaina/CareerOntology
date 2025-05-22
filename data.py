# data.py

import re
from descriptions import interest_descriptions

# Moved ONTOLOGY_MAP_RAW_TO_MAIN_CLASS here
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


categorized_student_interests_raw = {
    "Programming & Software Development": [
        "Web_Development", "Mobile_App_Development", "Game_Programming",
        "Artificial_Intelligence_Machine_Learning", "Data_Science_Analytics_Programming",
        "Backend_Development", "Frontend_Development"
    ],
    "Creative & Multimedia Arts": [
        "UX_UI_Design", "Graphic_Design", "Video_Editing_Production",
        "3D_Modeling_Animation", "Motion_Graphics", "Illustration", "Digital_Art",
        "Digital_Content_Creation_(broader)", "Technical_Writing", "Blogging_Vlogging", "Podcasting"
    ],
    "IT Infrastructure & Cybersecurity": [
        "Network_Administration", "Cybersecurity", "Cloud_Computing", "Database_Management",
        "Operating_Systems", "IT_Infrastructure"
    ],
    "Business, Management & Analytics": [
        "Project_Management", "Business_Analysis", "Entrepreneurship", "Digital_Marketing",
        "Financial_Technology_(FinTech)", "Operations_Management", "Strategy_Planning"
    ],
    "Game Design & Interactive Media": [
        "Game_Design", "Game_Development_(broader,_includes_non-programming_aspects)", "Interactive_Storytelling",
        "Virtual_Reality_Augmented_Reality", "Esports_Management"
    ],
    "Hardware, Robotics & IoT": [
        "Computer_Hardware", "Embedded_Systems", "Robotics", "IoT_(Internet_of_Things)", "Electronics"
    ],
    "Foundational & Research Skills": [
        "Problem_Solving_Logic", "Academic_Research", "New_Technologies", "Solving_Complex_Problems"
    ]
}

programs = {
    "BS Computer Science": {
        "description": "This program teaches you the deep theory and practice behind how computers work and how to make them do complex tasks. You'll learn to build intelligent systems, manage large data, and secure digital environments.",
        "skills_developed": [
            "Building_Program_Logic", "Organizing_Data_in_Programs", "Writing_Code",
            "Teaching_Computers_to_Learn", "Analyzing_Data_with_Code",
            "Building_System_Backbones", "Designing_User_Interfaces_Code",
            "Understanding_Statistics", "Logical_Problem_Solving",
            "Basic_Online_Security", "Managing_Databases_with_Code"
        ],
        "careers": [
            "Software_Engineer", "Frontend_Developer", "Backend_Developer", "Fullstack_Developer",
            "Mobile_App_Developer", "AI_ML_Engineer", "Data_Scientist", "Game_Programmer",
            "DevOps_Engineer", "Cloud_Developer", "Embedded_Systems_Developer", "Cybersecurity_Developer", "IT_Researcher"
        ]
    },
    "BS Information Technology": {
        "description": "This program focuses on the practical side of technology, like setting up, managing, and maintaining computer systems, networks, and providing technical support.",
        "skills_developed": [
            "Setting_Up_Networks", "Managing_Computer_Systems", "Handling_Cloud_Systems",
            "Managing_Operating_Systems", "Setting_Up_Virtual_Computers",
            "Fixing_Tech_Problems", "Managing_Databases_Admin", "Basic_Online_Security",
            "Securing_Networks", "Responding_to_Security_Issues",
            "Assembling_and_Fixing_Hardware", "Connecting_Smart_Devices_(IoT)"
        ],
        "careers": [
            "IT_Support_Specialist", "Network_Administrator", "System_Administrator",
            "Cloud_Administrator", "Database_Administrator", "Cybersecurity_Analyst",
            "IT_Consultant", "Help_Desk_Technician", "IoT_Developer", "Hardware_Engineer"
        ]
    },
    "BS Entertainment and Multimedia Computing (Digital Animation)": {
        "description": "This specialization focuses on creating compelling visual content, from cartoon characters to complex 3D environments, for various digital platforms.",
        "skills_developed": [
            "Creating_Graphics_and_Art", "Making_2D_Animations", "Creating_3D_Models",
            "Setting_Up_Characters_for_Animation", "Editing_Videos",
            "Making_Motion_Graphics", "Designing_User_Experience",
            "Designing_User_Interface", "Developing_Concept_Art",
            "Digital_Painting", "Digital_Illustration", "Crafting_Digital_Stories"
        ],
        "careers": [
            "Multimedia_Artist", "UX_UI_Designer", "Graphic_Designer", "2D_Animator",
            "3D_Artist_Modeler", "Video_Editor", "Motion_Graphics_Designer",
            "Concept_Artist", "Digital_Illustrator", "Web_Designer"
        ]
    },
    "BS Information System": {
        "description": "This program teaches you how to bridge the gap between business needs and technology solutions, focusing on designing, implementing, and managing information systems that help organizations run smoothly.",
        "skills_developed": [
            "Planning_and_Leading_Projects", "Gathering_Requirements", "Mapping_Business_Processes",
            "Analyzing_Markets", "Making_Business_Strategies", "Running_Digital_Marketing",
            "Talking_to_Stakeholders", "Logical_Problem_Solving", "Collecting_Data",
            "Cleaning_and_Preparing_Data", "Understanding_Statistics",
            "Presenting_Data_Visually", "Organizing_Data_in_Programs",
            "Working_with_Huge_Amounts_of_Data", "Managing_Databases_Admin",
            "Managing_Databases_with_Code", "Writing_Code"
        ],
        "careers": [
            "Data_Analyst", "Business_Analyst", "Project_Manager", "Systems_Analyst",
            "IT_Project_Manager", "Operations_Manager", "Product_Manager", "Entrepreneur",
            "Business_Intelligence_Analyst", "Database_Developer", "Big_Data_Engineer",
            "Digital_Marketing_Specialist", "SEO_Specialist", "Social_Media_Manager"
        ]
    },
    "BS Entertainment and Multimedia Computing (Game Development)": {
        "description": "This specialization is all about creating video games, from designing the game mechanics and stories to programming the game's logic and graphics.",
        "skills_developed": [
            "Building_Games_Code", "Designing_Game_Rules", "Building_Game_Levels",
            "Creating_Game_Stories", "Testing_Games", "Planning_and_Leading_Projects",
            "Writing_Code", "Building_System_Backbones", "Teaching_Computers_to_Learn",
            "Creating_Graphics_and_Art", "Designing_User_Experience",
            "Designing_User_Interface", "Interactive_Storytelling",
            "Developing_Concept_Art", "Digital_Painting", "Digital_Illustration",
            "Running_Digital_Marketing"
        ],
        "careers": [
            "Game_Developer", "Game_Designer", "Game_Programmer", "Level_Designer",
            "Game_Tester", "Game_Producer", "Esports_Manager", "Concept_Artist",
            "Digital_Illustrator", "UX_UI_Designer"
        ]
    },
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


interest_to_related_skills = {
    # Programming & Software Development
    "Web_Development": ["Making_Websites", "Building_Program_Logic", "Writing_Code", "Designing_User_Interfaces_Code"],
    "Mobile_App_Development": ["Creating_Mobile_Apps", "Building_Program_Logic", "Writing_Code"],
    "Game_Programming": ["Building_Games_Code", "Building_Program_Logic", "Writing_Code"],
    "Artificial_Intelligence_Machine_Learning": ["Teaching_Computers_to_Learn", "Analyzing_Data_with_Code", "Understanding_Statistics"],
    "Data_Science_Analytics_Programming": ["Analyzing_Data_with_Code", "Organizing_Data_in_Programs", "Understanding_Statistics"],
    "Backend_Development": ["Building_System_Backbones", "Managing_Databases_with_Code", "Writing_Code"],
    "Frontend_Development": ["Making_Websites", "Designing_User_Interfaces_Code", "Writing_Code"],

    # Creative & Multimedia Arts
    "UX_UI_Design": ["Designing_User_Experience", "Designing_User_Interface"],
    "Graphic_Design": ["Creating_Graphics_and_Art", "Digital_Painting", "Digital_Illustration"],
    "Video_Editing_Production": ["Editing_Videos", "Making_Motion_Graphics", "Crafting_Digital_Stories"],
    "3D_Modeling_Animation": ["Creating_3D_Models", "Setting_Up_Characters_for_Animation"],
    "Motion_Graphics": ["Making_Motion_Graphics", "Creating_Graphics_and_Art"],
    "Illustration": ["Digital_Painting", "Digital_Illustration", "Creating_Graphics_and_Art"],
    "Digital_Art": ["Digital_Painting", "Digital_Illustration", "Creating_Graphics_and_Art"],
    "Digital_Content_Creation_(broader)": ["Crafting_Digital_Stories", "Developing_Content_Plans", "Running_Digital_Marketing", "Editing_Videos"],
    "Technical_Writing": ["Writing_Technical_Guides", "Crafting_Digital_Stories"],
    "Blogging_Vlogging": ["Crafting_Digital_Stories", "Developing_Content_Plans", "Editing_Videos"],
    "Podcasting": ["Crafting_Digital_Stories", "Developing_Content_Plans", "Editing_Videos"],

    # IT Infrastructure & Cybersecurity
    "Network_Administration": ["Setting_Up_Networks", "Securing_Networks", "Fixing_Tech_Problems"],
    "Cybersecurity": ["Basic_Online_Security", "Responding_to_Security_Issues", "Securing_Networks"],
    "Cloud_Computing": ["Handling_Cloud_Systems", "Setting_Up_Virtual_Computers"],
    "Database_Management": ["Managing_Databases_Admin", "Managing_Databases_with_Code", "Organizing_Data_in_Programs"],
    "Operating_Systems": ["Managing_Operating_Systems", "Fixing_Tech_Problems"],
    "IT_Infrastructure": ["Managing_Computer_Systems", "Setting_Up_Networks", "Handling_Cloud_Systems"],

    # Business, Management & Analytics
    "Project_Management": ["Planning_and_Leading_Projects", "Using_Agile_Methods", "Spotting_and_Handling_Risks"],
    "Business_Analysis": ["Gathering_Requirements", "Mapping_Business_Processes"],
    "Entrepreneurship": ["Making_Business_Strategies", "Analyzing_Markets", "Running_Digital_Marketing"],
    "Digital_Marketing": ["Running_Digital_Marketing", "Developing_Content_Plans", "Analyzing_Markets"],
    "Financial_Technology_(FinTech)": ["Analyzing_Markets", "Making_Business_Strategies", "Understanding_Statistics"],
    "Operations_Management": ["Mapping_Business_Processes", "Planning_and_Leading_Projects"],
    "Strategy_Planning": ["Making_Business_Strategies", "Analyzing_Markets"],

    # Game Design & Interactive Media
    "Game_Design": ["Designing_Game_Rules", "Building_Game_Levels", "Creating_Game_Stories"],
    "Game_Development_(broader,_includes_non-programming_aspects)": ["Building_Games_Code", "Designing_Game_Rules", "Building_Game_Levels"],
    "Interactive_Storytelling": ["Creating_Game_Stories", "Crafting_Digital_Stories"],
    "Virtual_Reality_Augmented_Reality": ["Creating_3D_Models", "Building_Program_Logic"],
    "Esports_Management": ["Planning_and_Leading_Projects", "Running_Digital_Marketing"],

    # Hardware, Robotics & IoT
    "Computer_Hardware": ["Assembling_and_Fixing_Hardware", "Designing_Circuits"],
    "Embedded_Systems": ["Programming_Small_Computers", "Designing_Circuits"],
    "Robotics": ["Controlling_Robots", "Programming_Small_Computers"],
    "IoT_(Internet_of_Things)": ["Connecting_Smart_Devices_(IoT)", "Programming_Small_Computers"],
    "Electronics": ["Designing_Circuits", "Assembling_and_Fixing_Hardware"],

    # Foundational & Research Skills
    "Problem_Solving_Logic": ["Logical_Problem_Solving"],
    "Academic_Research": ["Doing_Research", "Learning_New_Technologies"],
    "New_Technologies": ["Learning_New_Technologies", "Doing_Research"],
    "Solving_Complex_Problems": ["Logical_Problem_Solving", "Doing_Research"],
}


def format_ontology_name(name):
    """Formats an ontology name for display by replacing underscores with spaces, and removing specific suffixes."""
    # Convert FinTech back to its original form before mapping to avoid accidental stripping
    name = name.replace("Financial_Technology_(FinTech)", "Financial Technology (FinTech)")

    # Remove the broader/includes non-programming aspects part
    name = name.replace('(broader, includes non-programming aspects)', '')

    # Remove (FinTech) if it's still there after the first replacement
    name = name.replace('(FinTech)', '')

    # Remove the (broader) part from Digital_Content_Creation_(broader)
    name = name.replace('_(broader)', '')

    # Replace underscores with spaces
    name = name.replace('_', ' ')

    # Remove the (Internet of Things) for IoT
    name = name.replace('(Internet of Things)', '')

    # Clean up multiple spaces and strip leading/trailing spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name