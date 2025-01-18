import requests
import pandas as pd
from io import BytesIO
import openai
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Global variable to store the dataset
dataset = None

# Dataset URL
DATASET_PATH = "https://yates.one-name.net/gengen/static/datasets/DNA_Study_Library.xlsx"

# Load the dataset during app initialization
def load_dataset():
    global dataset
    try:
        # Fetch the dataset from the URL
        response = requests.get(DATASET_PATH)
        response.raise_for_status()  # Raise an error for HTTP status codes >= 400

        # Load the dataset into a Pandas DataFrame
        dataset = pd.read_excel(BytesIO(response.content))
        print("Dataset loaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching dataset: {e}")
    except Exception as e:
        print(f"Error loading dataset: {e}")

# Call the dataset loader when the app starts
with app.app_context():
    load_dataset()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    global dataset
    if dataset is None:
        return jsonify({'error': 'Dataset is not loaded.'}), 400

    user_query = request.json.get('query', '')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Convert the dataset to a CSV string for processing
        dataset_string = dataset.to_csv(index=False)

        # Use OpenAI's API to analyze the dataset based on the user's question
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst. Answer questions about the dataset."},
                {"role": "user", "content": f"Dataset: {dataset_string}\n\nQuery: {user_query}"}
            ]
        )
        analysis = response['choices'][0]['message']['content']
        return jsonify({'response': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
