# Save this as lesson_plan.py

from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import re
from interdisciplinary_lesson_plan import generate_interdisciplinary_lesson_plan

# Load environment variables
load_dotenv()

# Debug: Print environment details
print(f"Current working directory: {os.getcwd()}")
print(f"Environment file path: {os.path.join(os.getcwd(), '.env')}")

# Initialize the OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key starts with: {api_key[:7]}...")

if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")

client = OpenAI(api_key=api_key)

def calculate_time_distribution(lesson_duration, grade_level):
    """
    Calculate time distribution for different stages based on grade level.
    Returns a dictionary with time allocations for each stage.
    """
    try:
        lesson_duration = int(lesson_duration)
    except (ValueError, TypeError):
        raise ValueError("Lesson duration must be a number")
    
    # Base time distribution
    time_distribution = {
        "introduction": 0.15 * lesson_duration,     # 15% of total time
        "competence_development": 0.40 * lesson_duration,  # 40% of total time
        "design": 0.25 * lesson_duration,           # 25% of total time
        "realisation": 0.20 * lesson_duration       # 20% of total time
    }
    
    # Adjust for certain grade levels
    if grade_level.lower() in ["form1", "form2", "form3"]:
        # More time for introduction and competence development for younger grades
        time_distribution["introduction"] *= 1.2
        time_distribution["competence_development"] *= 1.1
        time_distribution["design"] *= 0.9
        time_distribution["realisation"] *= 0.8
    elif grade_level.lower() in ["form4", "form5", "form6"]:
        # Balanced distribution for middle grades
        pass
    else:
        # More time for design and realisation for older grades
        time_distribution["introduction"] *= 0.8
        time_distribution["competence_development"] *= 0.9
        time_distribution["design"] *= 1.1
        time_distribution["realisation"] *= 1.2
    
    # Round to nearest minute
    for stage in time_distribution:
        time_distribution[stage] = round(time_distribution[stage])
    
    return time_distribution

def generate_specific_activities(main_learningactivity, grade_level, lesson_duration, time_distribution, lesson_type="regular", subject=None):
    """
    Generate specific learning activities for the main learning activity.
    Returns a JSON with the specific learning activities and their features.
    """
    try:
        # Create prompt for the OpenAI API
        prompt = f"""Generate specific learning activities for the following specifications:

        Subject: {subject}
        Main Learning Activity/ Topic: {main_learningactivity}
        Grade Level: {grade_level}
        Lesson Duration: {lesson_duration} minutes
        Lesson Type: {lesson_type}

        CRITICAL INSTRUCTIONS:
        1. Each specific learning activity must align with one of the four stages (Introduction, Competence Development, Design, Realisation).
        2. Each activity must start with an action verb (e.g., "define", "analyze", "demonstrate").
        3. Ensure activities align with Variation Principles (CONTRAST, SEPARATION, GENERALISATION, FUSION) and 5E Components (Engage, Explore, Explain, Elaborate, Evaluate).
        4. Include hands-on experiences where appropriate, and ensure activities are grade-level appropriate.
        5. Return the specific learning activities in JSON format.

        IMPORTANT: Return valid JSON only. Do not include any extra text.
        """
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional lesson planner. Your task is to create "
                        "specific learning activities that align with the IDDR model and the 5E approach. "
                        "Always return valid JSON."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        response_text = response.choices[0].message.content.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            activities = json.loads(response_text)
            return activities
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}\nRaw response: {response_text}")
            return {"error": "Failed to generate specific learning activities"}

    except Exception as e:
        print(f"Error generating specific activities: {str(e)}")
        return {"error": str(e)}

def generate_lesson_plan(main_learningactivity, grade_level, lesson_duration, time_distribution, lesson_type="regular", subject=None, selected_activity=None):
    """
    Generate a lesson plan (regular or project-based) based on the IDDR model and 5E approach.
    If selected_activity is provided, focus the lesson plan on that specific activity.
    """
    try:
        # If interdisciplinary, forward to specialized function
        if lesson_type and lesson_type.lower() == 'interdisciplinary':
            return generate_interdisciplinary_lesson_plan(main_learningactivity, grade_level, lesson_duration, time_distribution, subject)

        # First, generate specific learning activities if not provided
        if not selected_activity:
            activities = generate_specific_activities(main_learningactivity, grade_level, lesson_duration, time_distribution, lesson_type, subject)
            if "error" in activities:
                raise ValueError(activities["error"])
            return activities

        # Create prompt for the OpenAI API
        prompt = f"""Create a detailed lesson plan for the following specifications:

        Subject: {subject}
        Main Learning Activity/ Topic: {main_learningactivity}
        Selected Specific Activity: {selected_activity}
        Grade Level: {grade_level}
        Lesson Duration: {lesson_duration} minutes
        Lesson Type: {lesson_type}

        Time Distribution:
        - Introduction: {time_distribution['introduction']} minutes
        - Competence Development: {time_distribution['competence_development']} minutes
        - Design: {time_distribution['design']} minutes
        - Realisation: {time_distribution['realisation']} minutes

        CRITICAL INSTRUCTIONS:
        1. Ensure all stages (Introduction, Competence Development, Design, Realisation) align with the 5E approach and Variation Principles.
        2. Include real-world examples, hands-on exploration, practice exercises, and assessment tasks for each stage.
        3. Return the lesson plan in JSON format with these keys:
           - Main_Learning_Activity
           - Specific_Learning_Activities
           - Lesson_Plan (each stage should include Teaching Activities, Learning Activities, Assessment Criteria, Variation Principle, and 5E Component)
           - Remarks
        4. Always return valid JSON. Do not include any extra text.
        """
        
        # Remaining code unchanged...
