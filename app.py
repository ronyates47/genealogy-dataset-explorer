from flask import Flask, request, jsonify, render_template
import requests
import pandas as pd
from io import BytesIO
import openai
import os

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Dataset URL and global variable
DATASET_PATH = "https://yates.one-name.net/gengen/static/datasets/DNA_Study_Library.xlsx"  # URL to the dataset
dataset = None  # Global variable to store the dataset

# Load the dataset when the application starts
try:
    # Fetch the file from the URL
    response = requests.get(DATASET_PATH)
    response.raise_for_status()  # Raise an error for HTTP status codes >= 400

    # Read the dataset into a Pandas DataFrame
    dataset = pd.read_excel(BytesIO(response.content))
    print("Dataset loaded successfully from URL")
except requests.exceptions.RequestException as e:
    print(f"Error fetching dataset from URL: {e}")
except Exception as e:
    print(f"Error loading dataset: {e}")

@app.route('/')
def home():
    """Serve the HTML page."""
    return render_template('index.html')  # Serve the HTML page

@app.route('/query', methods=['POST'])
def query():
    """Handle user queries and interact with OpenAI."""
    global dataset
    if dataset is None:
        return jsonify({'error': 'Dataset not available'}), 500

    user_query = request.json.get('query', '')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Convert the dataset to a CSV string
        dataset_string = dataset.to_csv(index=False)

        # Send the dataset and query to ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": f"Dataset: {dataset_string}\n\nQuery: {user_query}"}
            ]
        )

        # Extract the analysis result from ChatGPT's response
        analysis = response['choices'][0]['message']['content']
        return jsonify({'analysis': analysis})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
