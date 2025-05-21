import re
from descriptions import interest_descriptions

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
            "Setting_Up_Characters_for_Animation", "Editing_Videos", "Making_Motion_Graphics",
            "Digital_Painting", "Developing_Concept_Art", "Designing_User_Experience",
            "Designing_User_Interface", "Crafting_Digital_Stories", "Giving_Presentations"
        ],
        "careers": [
            "Multimedia_Artist", "UX_UI_Designer", "Graphic_Designer", "2D_Animator",
            "3D_Artist_Modeler", "Video_Editor", "Motion_Graphics_Designer",
            "Concept_Artist", "Digital_Illustrator", "Web_Designer"
        ]
    },
    "BS Entertainment and Multimedia Computing (Game Development)": {
        "description": "This specialization dives into the exciting world of creating video games, covering everything from coding the game logic to designing immersive worlds and characters.",
        "skills_developed": [
            "Building_Games_Code", "Designing_Game_Rules", "Building_Game_Levels",
            "Testing_Games", "Creating_Game_Stories", "Writing_Code", "Organizing_Data_in_Programs",
            "Creating_3D_Models", "Setting_Up_Characters_for_Animation",
            "Designing_User_Experience", "Designing_User_Interface"
        ],
        "careers": [
            "Game_Developer", "Game_Designer", "Level_Designer", "Game_Programmer",
            "Game_Tester", "3D_Artist_Modeler", "UX_UI_Designer"
        ]
    },
    "BS Information Systems": {
        "description": "This program bridges the gap between technology and business, teaching you how to design, implement, and manage information systems to solve real-world organizational challenges.",
        "skills_developed": [
            "Planning_and_Leading_Projects", "Using_Agile_Methods", "Spotting_and_Handling_Risks",
            "Talking_to_Stakeholders", "Gathering_Requirements", "Mapping_Business_Processes",
            "Making_Business_Strategies", "Analyzing_Markets", "Basic_Financial_Analysis",
            "Collecting_Data", "Cleaning_and_Preparing_Data", "Understanding_Statistics",
            "Presenting_Data_Visually", "Managing_Databases_Admin", "Managing_Databases_with_Code"
        ],
        "careers": [
            "Project_Manager", "Business_Analyst", "Systems_Analyst", "IT_Project_Manager",
            "Operations_Manager", "Product_Manager", "Entrepreneur", "Data_Analyst",
            "Business_Intelligence_Analyst", "IT_Consultant"
        ]
    }
}

interest_to_related_skills = {
    "Web_Development": ["Making_Websites", "Writing_Code", "Building_System_Backbones", "Designing_User_Interfaces_Code", "Managing_Databases_with_Code", "Designing_User_Experience", "Designing_User_Interface"],
    "Mobile_App_Development": ["Creating_Mobile_Apps", "Writing_Code", "Building_System_Backbones", "Designing_User_Interfaces_Code", "Designing_User_Experience", "Designing_User_Interface"],
    "Game_Programming": ["Building_Games_Code", "Writing_Code", "Building_Program_Logic", "Designing_Game_Rules"],
    "Artificial_Intelligence_Machine_Learning": ["Teaching_Computers_to_Learn", "Analyzing_Data_with_Code", "Understanding_Statistics", "Building_Program_Logic", "Predicting_Trends_from_Data"],
    "Data_Science_Analytics_Programming": ["Analyzing_Data_with_Code", "Understanding_Statistics", "Collecting_Data", "Cleaning_and_Preparing_Data", "Presenting_Data_Visually", "Working_with_Huge_Amounts_of_Data"],
    "Backend_Development": ["Building_System_Backbones", "Writing_Code", "Managing_Databases_with_Code", "Building_Program_Logic", "Setting_Up_Networks"],
    "Frontend_Development": ["Designing_User_Interfaces_Code", "Making_Websites", "Writing_Code", "Designing_User_Experience", "Designing_User_Interface"],
    "UX_UI_Design": ["Designing_User_Experience", "Designing_User_Interface", "Creating_Graphics_and_Art", "Developing_Concept_Art"],
    "Graphic_Design": ["Creating_Graphics_and_Art", "Digital_Painting", "Developing_Concept_Art", "Digital_Illustration"],
    "Video_Editing_Production": ["Editing_Videos", "Making_Motion_Graphics", "Crafting_Digital_Stories"],
    "3D_Modeling_Animation": ["Creating_3D_Models", "Setting_Up_Characters_for_Animation", "Making_2D_Animations", "Making_Motion_Graphics"],
    "Motion_Graphics": ["Making_Motion_Graphics", "Editing_Videos", "Creating_Graphics_and_Art", "Making_2D_Animations"],
    "Illustration": ["Digital_Painting", "Creating_Graphics_and_Art", "Digital_Illustration", "Developing_Concept_Art"],
    "Digital_Art": ["Digital_Painting", "Creating_Graphics_and_Art", "Digital_Illustration", "Developing_Concept_Art"],
    "Digital_Content_Creation_(broader)": ["Crafting_Digital_Stories", "Developing_Content_Plans", "Running_Digital_Marketing", "Editing_Videos"],
    "Technical_Writing": ["Writing_Technical_Guides", "Crafting_Digital_Stories", "Developing_Content_Plans", "Doing_Research"],
    "Blogging_Vlogging": ["Crafting_Digital_Stories", "Developing_Content_Plans", "Running_Digital_Marketing", "Editing_Videos"],
    "Podcasting": ["Crafting_Digital_Stories", "Developing_Content_Plans", "Editing_Videos", "Giving_Presentations"],
    "Network_Administration": ["Setting_Up_Networks", "Managing_Computer_Systems", "Securing_Networks", "Fixing_Tech_Problems"],
    "Cybersecurity": ["Basic_Online_Security", "Securing_Networks", "Responding_to_Security_Issues", "Fixing_Tech_Problems", "Logical_Problem_Solving"],
    "Cloud_Computing": ["Handling_Cloud_Systems", "Setting_Up_Networks", "Managing_Computer_Systems", "Setting_Up_Virtual_Computers"],
    "Database_Management": ["Managing_Databases_Admin", "Managing_Databases_with_Code", "Collecting_Data", "Organizing_Data_in_Programs"],
    "Operating_Systems": ["Managing_Operating_Systems", "Fixing_Tech_Problems", "Managing_Computer_Systems"],
    "IT_Infrastructure": ["Setting_Up_Networks", "Managing_Computer_Systems", "Handling_Cloud_Systems", "Managing_Operating_Systems", "Fixing_Tech_Problems"],
    "Problem_Solving_Logic": ["Logical_Problem_Solving", "Thinking_Critically", "Doing_Research"],
    "Project_Management": ["Planning_and_Leading_Projects", "Using_Agile_Methods", "Spotting_and_Handling_Risks", "Talking_to_Stakeholders"],
    "Business_Analysis": ["Gathering_Requirements", "Mapping_Business_Processes", "Analyzing_Markets", "Basic_Financial_Analysis", "Making_Business_Strategies"],
    "Entrepreneurship": ["Making_Business_Strategies", "Analyzing_Markets", "Planning_and_Leading_Projects", "Running_Digital_Marketing"],
    "Digital_Marketing": ["Running_Digital_Marketing", "Developing_Content_Plans", "Creating_Graphics_and_Art", "Crafting_Digital_Stories"],
    "Financial_Technology_(FinTech)": ["Basic_Financial_Analysis", "Managing_Databases_with_Code", "Building_System_Backbones", "Analyzing_Data_with_Code"],
    "Operations_Management": ["Mapping_Business_Processes", "Planning_and_Leading_Projects", "Gathering_Requirements"],
    "Strategy_Planning": ["Making_Business_Strategies", "Analyzing_Markets", "Planning_and_Leading_Projects", "Thinking_Critically"],
    "Game_Design": ["Designing_Game_Rules", "Building_Game_Levels", "Creating_Game_Stories", "Designing_User_Experience"],
    "Game_Development_(broader,_includes_non-programming_aspects)": ["Building_Games_Code", "Designing_Game_Rules", "Building_Game_Levels", "Testing_Games", "Writing_Code", "Creating_3D_Models"],
    "Interactive_Storytelling": ["Creating_Game_Stories", "Crafting_Digital_Stories", "Designing_User_Experience", "Writing_Technical_Guides"],
    "Virtual_Reality_Augmented_Reality": ["Creating_3D_Models", "Building_Games_Code", "Designing_User_Experience", "Connecting_Smart_Devices_(IoT)", "Programming_Small_Computers"],
    "Esports_Management": ["Planning_and_Leading_Projects", "Running_Digital_Marketing", "Talking_to_Stakeholders"],
    "Computer_Hardware": ["Assembling_and_Fixing_Hardware", "Fixing_Tech_Problems", "Designing_Circuits"],
    "Embedded_Systems": ["Programming_Small_Computers_(Microcontrollers)", "Designing_Circuits", "Assembling_and_Fixing_Hardware"],
    "Robotics": ["Controlling_Robots", "Programming_Small_Computers_(Microcontrollers)", "Designing_Circuits", "Assembling_and_Fixing_Hardware"],
    "IoT_(Internet_of_Things)": ["Connecting_Smart_Devices_(IoT)", "Programming_Small_Computers_(Microcontrollers)", "Setting_Up_Networks", "Building_System_Backbones"],
    "Electronics": ["Designing_Circuits", "Assembling_and_Fixing_Hardware", "Programming_Small_Computers_(Microcontrollers)"],
    "Academic_Research": ["Doing_Research", "Logical_Problem_Solving", "Thinking_Critically", "Analyzing_Data_with_Code", "Understanding_Statistics"],
    "New_Technologies": ["Learning_New_Technologies", "Logical_Problem_Solving", "Doing_Research", "Building_Program_Logic"],
    "Solving_Complex_Problems": ["Logical_Problem_Solving", "Thinking_Critically", "Doing_Research", "Analyzing_Data_with_Code"]
}

def format_ontology_name(name):
    name = name.replace("_Skill", "")
    formatted_name = name.replace("_", " ")

    def process_parentheses(match):
        content_inside = match.group(1).replace('_', ' ')
        words_inside = [
            word.capitalize() if word.lower() not in ['ui', 'ux', 'ai', 'ml', 'iot', 'it', 'seo', 'fintech'] else word.upper()
            for word in content_inside.split()
        ]
        return '(' + " ".join(words_inside) + ')'

    formatted_name = re.sub(r'\(([^)]*)\)', process_parentheses, formatted_name)

    words = []
    for word in formatted_name.split():
        if word.lower() in ['ui', 'ux', 'ai', 'ml', 'iot', 'it', 'seo', '3d', '2d']:
            words.append(word.upper())
        elif 'vlogging' in word.lower():
            words.append(word.replace("vlogging", "Vlogging"))
        elif '(broader' in word.lower() or '(includes' in word.lower():
             words.append(word)
        else:
            words.append(word.capitalize())
    formatted_name = " ".join(words)

    formatted_name = formatted_name.replace("Ux/ui", "UX/UI")
    formatted_name = formatted_name.replace("Ai/ml", "AI/ML")
    formatted_name = formatted_name.replace("Iot", "IoT")
    formatted_name = formatted_name.replace("It ", "IT ")
    formatted_name = formatted_name.replace("3d", "3D")
    formatted_name = formatted_name.replace("2d", "2D")
    formatted_name = formatted_name.replace("Fintech", "FinTech")
    formatted_name = formatted_name.replace("Blogging Vlogging", "Blogging/Vlogging")

    return formatted_name.strip()