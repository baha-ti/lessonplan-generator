# Lesson Plan Generator

A web application that generates detailed lesson plans using OpenAI's GPT model. The application follows the IDDR model and 5E's approach for creating comprehensive and effective lesson plans.

## Features

- Generate regular lesson plans
- Generate interdisciplinary lesson plans
- Customize existing lesson plans
- Time distribution calculation based on grade level
- Real-time lesson plan generation using OpenAI GPT

## Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd lessonplan
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application
```bash
python app.py
```

## Deployment

This application can be deployed on Render. Make sure to:
1. Set the environment variables in Render dashboard
2. Use `gunicorn app:app` as the start command

## API Endpoints

- `POST /generate_lesson_plan`: Generate a new lesson plan
- `POST /customize_lesson_plan`: Customize an existing lesson plan

## Technologies Used

- Flask
- OpenAI GPT
- Python-dotenv
- Gunicorn (for production deployment) 