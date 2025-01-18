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
        # Handle user query (replace this with OpenAI logic if needed)
        if user_query.lower() == "count number of rows":
            return jsonify({'response': f"The dataset has {len(dataset)} rows."})
        else:
            return jsonify({'response': "I didn't understand your query. Try 'count number of rows'."})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

