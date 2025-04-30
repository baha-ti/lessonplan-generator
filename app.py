# Save this as app.py

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests  # for catching network/connection errors if needed
from lesson_plan import generate_lesson_plan, customize_lesson_plan, calculate_time_distribution, generate_specific_activities
from interdisciplinary_lesson_plan import generate_interdisciplinary_lesson_plan
import json

load_dotenv()  # Load environment variables

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# For session management, ensure you have a secure, persistent secret key in production
app.secret_key = os.urandom(24)

# Create a temporary directory for storing files
temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
os.makedirs(temp_dir, exist_ok=True)

@app.route('/')
def index():
    # Render your index or UI page
    return render_template('index.html')

@app.route('/generate_specific_activities', methods=['POST'])
def generate_specific_activities_route():
    try:
        data = request.get_json()
        main_learningactivity = data.get('main_learning_activity')
        grade_level = data.get('grade_level')
        lesson_duration = data.get('lesson_duration')
        lesson_type = data.get('lesson_type', 'regular')
        subject = data.get('subject')

        if not all([main_learningactivity, grade_level, lesson_duration]):
            return jsonify({"error": "Missing required fields"}), 400

        time_distribution = calculate_time_distribution(lesson_duration, grade_level)
        activities = generate_specific_activities(
            main_learningactivity,
            grade_level,
            lesson_duration,
            time_distribution,
            lesson_type,
            subject
        )

        if "error" in activities:
            return jsonify(activities), 500

        return jsonify(activities)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_lesson_plan', methods=['POST'])
def generate_lesson_plan_route():
    try:
        data = request.get_json()
        main_learningactivity = data.get('main_learning_activity')
        grade_level = data.get('grade_level')
        lesson_duration = data.get('lesson_duration')
        lesson_type = data.get('lesson_type', 'regular')
        subject = data.get('subject')
        selected_activity = data.get('selected_activity')

        if not all([main_learningactivity, grade_level, lesson_duration]):
            return jsonify({"error": "Missing required fields"}), 400

        time_distribution = calculate_time_distribution(lesson_duration, grade_level)
        lesson_plan = generate_lesson_plan(
            main_learningactivity,
            grade_level,
            lesson_duration,
            time_distribution,
            lesson_type,
            subject,
            selected_activity
        )

        if "error" in lesson_plan:
            return jsonify(lesson_plan), 500

        return jsonify(lesson_plan)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/customize_lesson_plan', methods=['POST'])
def customize_lesson_plan_route():
    try:
        # Ensure request is JSON
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400

        data = request.get_json()

        # Validate required fields
        required_fields = ['current_lesson_plan', 'customization']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Optional: get lesson_type if provided
        lesson_type = data.get('lesson_type', None)

        # Customize the lesson plan
        customized_plan = customize_lesson_plan(
            data['current_lesson_plan'],
            data['customization'],
            lesson_type
        )

        return jsonify(customized_plan)

    except requests.exceptions.RequestException as net_err:
        # Catch network/connection-related errors
        print(f"[Network Error in customize_lesson_plan_route]: {str(net_err)}")
        return jsonify({
            'error': 'A network error occurred while customizing the lesson plan. '
                     'Please check your internet connection or try again later.'
        }), 503

    except ValueError as val_err:
        print(f"[ValueError in customize_lesson_plan_route]: {str(val_err)}")
        return jsonify({'error': str(val_err)}), 400

    except Exception as e:
        print(f"[Error in customize_lesson_plan_route]: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred while customizing the lesson plan. Please try again.'}), 500

if __name__ == '__main__':
    # Adjust host/port if needed. 0.0.0.0 is typical for container deployments.
    # In production, disable debug mode and set a stable secret key.
    app.run(debug=True, host='0.0.0.0', port=5000)
