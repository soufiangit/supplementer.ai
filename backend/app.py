from flask import Flask, request, jsonify, render_template
import os
import pandas as pd
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from supabase import create_client, Client
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env or Restack.io environment
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load CSV file into memory at startup (example: supplements.csv)
supplement_df = pd.read_csv('./backend/supplementinfo.csv')

# Initialize GPT-2 model for enhanced recommendations
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML form

@app.route('/recommend', methods=['POST'])
def recommend():
    user_goals = request.form.get('goals')  # Get user's goals from the form
    depth_level = request.form.get('depth_level', 'general')  # Depth level from the form
    use_gpt2 = request.form.get('use_gpt2', False)  # Whether to use GPT-2 (checkbox)

    recommendations = []
    questions_asked = []

    # General filter logic for supplements based on goals
    for _, row in supplement_df.iterrows():
        if any(goal.lower() in row['description'].lower() for goal in user_goals.split(',')):
            recommendations.append(row['supplement_name'])

    if not recommendations:
        recommendations = ["No suitable supplements found."]

    # GPT-2 based dynamic questioning and deeper refinement based on depth level
    gpt2_response = None
    if use_gpt2:
        prompt = f"Recommend supplements for these goals: {', '.join(user_goals.split(','))}. Current recommendations: {', '.join(recommendations)}. Depth level: {depth_level}."
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        outputs = model.generate(inputs, max_length=200, do_sample=True, top_p=0.95, top_k=50)
        gpt2_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Dynamic questions based on depth level
    if depth_level == 'general':
        questions_asked.append("What is your primary health goal?")
    elif depth_level == 'specific':
        questions_asked.append("What specific health concerns do you want to target?")
        questions_asked.append("Do you have any dietary restrictions?")
    elif depth_level == 'precise':
        questions_asked.append("Do you have a specific health condition you're treating?")
        questions_asked.append("How long are you willing to take supplements?")

    return render_template(
        'result.html', 
        recommendations=recommendations,
        gpt2_response=gpt2_response,
        questions=questions_asked
    )

if __name__ == '__main__':
    app.run(debug=True)
