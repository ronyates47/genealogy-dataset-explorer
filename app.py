from flask import Flask, request, jsonify, render_template
import pandas as pd
import openai
import os
import requests
from io import BytesIO

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set OpenAI API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Path to your dataset
DATASET_URL = "https://yates.one-name.net/gengen/static/datasets/DNA_Study_Library.xlsx"

# Global variable to hold the dataset
dataset = None

# Load dataset when the application starts
def load_dataset():
    global dataset
    try:
        response = requests.get(DATASET_URL)
        response.raise_for_status()  # Ensure the request was successful
        dataset = pd.read_excel(BytesIO(response.content))
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"Error loading dataset: {e}")

# Load dataset at startup
load_dataset()

@app.route('/')
def home():
    return render_template('index.html')  # Serve the main HTML page

@app.route('/query', methods=['POST'])
def query():
    global dataset
    if dataset is None:
        return jsonify({'error': 'Dataset not loaded'}), 500

    user_query = request.json.get('query', '').strip()
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Convert the dataset to a CSV string for analysis
        dataset_string = dataset.to_csv(index=False)

        # Send query to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert data analyst."},
                {"role": "user", "content": f"Dataset:\n{dataset_string}\n\nQuery: {user_query}"}
            ],
        )

        analysis = response['choices'][0]['message']['content']
        return jsonify({'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

