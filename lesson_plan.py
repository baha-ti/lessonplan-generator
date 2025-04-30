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
        1. Each specific learning activity must be an EXACT breakdown of the main learning activity
        2. When combined, all specific learning activities should form the complete main learning activity
        3. Maximum of FOUR specific learning activities
        4. Each activity must start with an action verb (e.g., "define", "analyze", "demonstrate")
        5. For each specific learning activity, provide specific tasks/problems/scenarios that:
           • Start with action verbs
           • Are brief and clear
           • Will be used in the FOUR STAGES of the lesson plan matrix
           • Include hands-on experiences where appropriate
           • Are grade-level appropriate
           • Directly support achieving the specific learning activity

        Return the specific learning activities in JSON format:
        {{
            "Specific_Learning_Activities": {{
                "1": {{
                    "Activity": "Activity Title",
                    "Features": ["Feature 1", "Feature 2"]
                }},
                "2": {{
                    "Activity": "Another Activity Title",
                    "Features": ["Feature 1", "Feature 2"]
                }}
            }}
        }}

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
                        "specific learning activities that break down the main learning activity. "
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
        1. Focus the entire lesson plan on the selected specific activity
        2. Ensure all stages (Introduction, Competence Development, Design, Realisation) 
           directly support the selected specific activity
        3. All teaching and learning activities should be aligned with the selected activity
        4. Assessment criteria should specifically measure achievement of the selected activity
        5. Use the following principles as GUIDING PRINCIPLES (do not include them in the output):
           - Variation Principles:
             • Introduction: CONTRAST (show differences)
             • Competence Development: SEPARATION (break down components)
             • Design: GENERALIZATION (apply to new situations)
             • Realisation: FUSION (combine all elements)
           - 5E's Approach:
             • Introduction: Engage
             • Competence Development: Explore/Explain
             • Design: Elaborate
             • Realisation: Evaluate

        Return the lesson plan in JSON format:
        {{
            "Main_Learning_Activity": "{main_learningactivity}",
            "Specific_Learning_Activities": {{
                "{selected_activity}": {{
                    "Activity": "Selected Activity Title",
                    "Features": ["Feature 1", "Feature 2"]
                }}
            }},
            "Lesson_Plan": [
                {{
                    "Stage": "Introduction",
                    "Time (Minutes)": "{time_distribution['introduction']}",
                    "Teaching Activities": "Activities that engage students with the selected activity",
                    "Learning Activities": "Tasks that help students explore the selected activity",
                    "Assessment Criteria": "Criteria that measure engagement with the selected activity"
                }},
                {{
                    "Stage": "Competence Development",
                    "Time (Minutes)": "{time_distribution['competence_development']}",
                    "Teaching Activities": "Activities that develop understanding of the selected activity",
                    "Learning Activities": "Tasks that help students understand the selected activity",
                    "Assessment Criteria": "Criteria that measure understanding of the selected activity"
                }},
                {{
                    "Stage": "Design",
                    "Time (Minutes)": "{time_distribution['design']}",
                    "Teaching Activities": "Activities that deepen understanding of the selected activity",
                    "Learning Activities": "Tasks that apply the selected activity to new situations",
                    "Assessment Criteria": "Criteria that measure application of the selected activity"
                }},
                {{
                    "Stage": "Realisation",
                    "Time (Minutes)": "{time_distribution['realisation']}",
                    "Teaching Activities": "Activities that evaluate mastery of the selected activity",
                    "Learning Activities": "Tasks that demonstrate mastery of the selected activity",
                    "Assessment Criteria": "Criteria that measure mastery of the selected activity"
                }}
            ],
            "Remarks": [
                "Students were able to [what they were able to do] in relation to the selected activity. However, some students failed [specific areas]. Therefore, I will [remedial actions]."
            ]
        }}

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
                        "detailed lesson plans following the IDDR model and 5E's approach. "
                        "Always return valid JSON."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        response_text = response.choices[0].message.content.strip()
        
        # Clean up the response text
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            lesson_plan = json.loads(response_text)
            
            # Validate keys
            required_keys = ["Main_Learning_Activity", "Specific_Learning_Activities", "Lesson_Plan", "Remarks"]
            for key in required_keys:
                if key not in lesson_plan:
                    raise ValueError(f"Missing required key in lesson plan: {key}")
            
            # Ensure key sections exist
            if "Specific_Learning_Activities" not in lesson_plan:
                lesson_plan["Specific_Learning_Activities"] = {}
            
            if "Lesson_Plan" not in lesson_plan:
                lesson_plan["Lesson_Plan"] = []
            
            if "Remarks" not in lesson_plan:
                lesson_plan["Remarks"] = []
            
            # Make sure Teaching Activities are teacher-focused (not starting with 'Students')
            for stage in lesson_plan.get("Lesson_Plan", []):
                if "Teaching Activities" in stage:
                    teaching_activities = stage["Teaching Activities"]
                    if teaching_activities.lower().startswith("students"):
                        teaching_activities = teaching_activities[8:].strip()
                        teaching_activities = teaching_activities[0].upper() + teaching_activities[1:]
                        stage["Teaching Activities"] = teaching_activities
            
            return lesson_plan

        except json.JSONDecodeError as e:
            print(f"Initial JSON parsing failed: {str(e)}")
            print(f"Raw response: {response_text}")
            
            # Try cleanup
            response_text = response_text.replace("'", '"')  
            response_text = re.sub(r'(\\w+):', r'\"\\1\":', response_text)
            response_text = re.sub(r',\\s*}', '}', response_text)
            response_text = re.sub(r',\\s*]', ']', response_text)
            
            try:
                lesson_plan = json.loads(response_text)
                # Validate again
                required_keys = ["Main_Learning_Activity", "Specific_Learning_Activities", "Lesson_Plan", "Remarks"]
                for key in required_keys:
                    if key not in lesson_plan:
                        raise Exception(f"Missing required key in lesson plan: {key}")
                return lesson_plan
            except json.JSONDecodeError as e:
                print(f"Second JSON parsing attempt failed: {str(e)}")
                print(f"Cleaned response: {response_text}")
                
                return {
                    "Main_Learning_Activity": main_learningactivity,
                    "Specific_Learning_Activities": {
                        "1": {
                            "Activity": "Activity related to " + main_learningactivity,
                            "Features": ["Feature 1", "Feature 2"]
                        }
                    },
                    "Lesson_Plan": [
                        {
                            "Stage": "Introduction",
                            "Time (Minutes)": time_distribution['introduction'],
                            "Teaching Activities": f"Show examples related to {main_learningactivity}",
                            "Learning Activities": "Activity 1",
                            "Assessment Criteria": "Criterion 1",
                            "Variation Principle": "CONTRAST",
                            "5E Component": "Engage"
                        }
                    ],
                    "Remarks": [
                        "Error occurred while generating the full lesson plan. Simplified version provided."
                    ]
                }
        
        except Exception as e:
            print(f"Error generating lesson plan: {str(e)}")
            return {
                "Main_Learning_Activity": main_learningactivity,
                "Specific_Learning_Activities": {
                    "1": {
                        "Activity": "Activity related to " + main_learningactivity,
                        "Features": ["Feature 1", "Feature 2"]
                    }
                },
                "Lesson_Plan": [
                    {
                        "Stage": "Introduction",
                        "Time (Minutes)": time_distribution['introduction'],
                        "Teaching Activities": f"Show examples related to {main_learningactivity}",
                        "Learning Activities": "Activity 1",
                        "Assessment Criteria": "Criterion 1",
                        "Variation Principle": "CONTRAST",
                        "5E Component": "Engage"
                    }
                ],
                "Remarks": [
                    "Error occurred while generating the full lesson plan. Simplified version provided."
                ]
            }

    except Exception as e:
        print(f"Error generating lesson plan: {str(e)}")
        return {
            "Main_Learning_Activity": main_learningactivity,
            "Specific_Learning_Activities": {
                "1": {
                    "Activity": "Activity related to " + main_learningactivity,
                    "Features": ["Feature 1", "Feature 2"]
                }
            },
            "Lesson_Plan": [
                {
                    "Stage": "Introduction",
                    "Time (Minutes)": time_distribution['introduction'],
                    "Teaching Activities": f"Show examples related to {main_learningactivity}",
                    "Learning Activities": "Activity 1",
                    "Assessment Criteria": "Criterion 1",
                    "Variation Principle": "CONTRAST",
                    "5E Component": "Engage"
                }
            ],
            "Remarks": [
                "Error occurred while generating the full lesson plan. Simplified version provided."
            ]
        }

def customize_lesson_plan(current_lesson_plan, customization, lesson_type=None):
    """
    Customize an existing lesson plan based on user requests.
    This function calls the OpenAI API to adjust the existing plan
    according to the user's customization request, then returns
    a new or updated JSON lesson plan.
    """
    print(f"Customizing lesson plan with request: {customization}")
    
    try:
        if not isinstance(current_lesson_plan, dict):
            return {"Error": "Invalid lesson plan format"}
        
        if not isinstance(customization, str):
            return {"Error": "Invalid customization request"}
        
        original_main_activity = current_lesson_plan.get("Main_Learning_Activity", "")
        
        prompt = f"""Modify the following lesson plan based on this request: "{customization}"

        Current Lesson Plan:
        {json.dumps(current_lesson_plan, indent=2)}

        Lesson Type: {lesson_type if lesson_type else "regular"}
        
        CRITICAL INSTRUCTIONS:
        1. Keep the Main_Learning_Activity exactly as it is: "{original_main_activity}"
        2. Do not remove keys: "Main_Learning_Activity", "Specific_Learning_Activities", "Lesson_Plan", "Remarks"
        3. Maintain IDDR + 5E structure
        4. Keep assessment criteria in passive voice, present tense
        5. Return valid JSON only, with no extra text
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional lesson planner. Your task is to create or modify "
                        "detailed lesson plans following the IDDR model and the 5E approach."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        response_text = response.choices[0].message.content.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            customized_plan = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}\nRaw response: {response_text}")
            # Attempt basic cleanup
            cleaned_text = response_text.replace("'", '"')
            cleaned_text = re.sub(r'(\\w+):', r'\"\\1\":', cleaned_text)
            cleaned_text = re.sub(r',\\s*}', '}', cleaned_text)
            cleaned_text = re.sub(r',\\s*]', ']', cleaned_text)
            customized_plan = json.loads(cleaned_text)
        
        required_keys = ["Main_Learning_Activity", "Specific_Learning_Activities", "Lesson_Plan", "Remarks"]
        for key in required_keys:
            if key not in customized_plan:
                raise Exception(f"Missing required key in lesson plan: {key}")
        
        # Make sure the Main_Learning_Activity remains unchanged
        customized_plan["Main_Learning_Activity"] = original_main_activity
        
        # Ensure minimal structure is present
        if "Specific_Learning_Activities" not in customized_plan:
            customized_plan["Specific_Learning_Activities"] = {}
        if "Lesson_Plan" not in customized_plan:
            customized_plan["Lesson_Plan"] = []
        if "Remarks" not in customized_plan:
            customized_plan["Remarks"] = []
        
        return customized_plan

    except Exception as e:
        print(f"Error customizing lesson plan: {str(e)}")
        return {"Error": f"Could not customize lesson plan: {str(e)}"}
