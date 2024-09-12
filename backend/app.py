from flask import Flask, request, jsonify
import os
import pandas as pd
from flask_cors import CORS
from supabase import create_client, Client
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables from .env or Restack.io environment
load_dotenv()

REACT_APP_SUPABASE_URL = os.getenv('REACT_APP_SUPABASE_URL')
REACT_APP_SUPABASE_ANON_KEY= os.getenv('REACT_APP_SUPABASE_ANON_KEY')
REACT_APP_OPENAI_API_KEY = os.getenv('REACT_APP_OPENAI_API_KEY')

# Initialize Supabase Client
supabase: Client = create_client(REACT_APP_SUPABASE_URL, REACT_APP_SUPABASE_ANON_KEY)

# Load CSV file into memory at startup
supplement_df = pd.read_csv('./backend/supplementinfo.csv')

# Initialize GPT-2 model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    user_goals = data.get('goals')  # User's health goals
    depth_level = data.get('depth_level', 'general').lower()  # User-selected depth level
    use_gpt2 = data.get('use_gpt2', False)  # Flag to use GPT-2 for enhanced recommendations

    recommendations = []
    questions_asked = []

    # General filter logic for supplements based on goals
    for _, row in supplement_df.iterrows():
        if any(goal.lower() in row['description'].lower() for goal in user_goals):
            recommendations.append(row['supplement_name'])

    if not recommendations:
        recommendations = ["No suitable supplements found."]

    # GPT-2 based dynamic questioning and deeper refinement based on depth level
    if use_gpt2:
        prompt = f"Recommend supplements for these goals: {', '.join(user_goals)}. The current recommendations are: {', '.join(recommendations)}. Depth level: {depth_level}. Generate more specific recommendations based on the depth level and ask questions as needed."
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        outputs = model.generate(inputs, max_length=200, do_sample=True, top_p=0.95, top_k=50)
        gpt2_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Dynamically generated questions based on depth level
        if depth_level == 'general':
            questions_asked.append("What is your primary health goal?")
        elif depth_level == 'specific':
            questions_asked.append("What specific health concerns do you want to target?")
            questions_asked.append("Do you have any dietary restrictions?")
        elif depth_level == 'precise':
            questions_asked.append("Do you have a specific health condition you're treating?")
            questions_asked.append("How long are you willing to take supplements?")
            questions_asked.append("Any known supplement sensitivities or side effects?")
    else:
        gpt2_response = None

    response = {
        "message": "ok",
        "goals": user_goals,
        "recommendations": recommendations,
        "gpt2_response": gpt2_response,
        "questions_to_ask": questions_asked  # Dynamically generated questions
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
