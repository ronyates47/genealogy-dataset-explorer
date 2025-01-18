from flask import Flask, request, jsonify, render_template
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__, static_folder='static', template_folder='templates')

# Dataset URL
DATASET_URL = "https://yates.one-name.net/gengen/static/datasets/DNA_Study_Library.xlsx"
dataset = None  # Global variable to store the dataset

# Load the dataset during the app startup
@app.before_first_request
def load_dataset():
    global dataset
    try:
        response = requests.get(DATASET_URL)
        response.raise_for_status()
        dataset = pd.read_excel(BytesIO(response.content))
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"Error loading dataset: {e}")

@app.route('/')
def home():
    return render_template('index.html')  # Render the homepage

@app.route('/query', methods=['POST'])
def query():
    global dataset
    if dataset is None:
        return jsonify({'error': 'Dataset not loaded.'}), 500

    user_query = request.json.get('query', '').strip()
    if not user_query:
        return jsonify({'error': 'No query provided.'}), 400

    # Process simple queries
    try:
        if "count number of rows" in user_query.lower():
            count = len(dataset)
            return jsonify({'response': f"The dataset has {count} rows."})
        elif "show columns" in user_query.lower():
            columns = dataset.columns.tolist()
            return jsonify({'response': f"Columns in the dataset: {', '.join(columns)}"})
        else:
            return jsonify({'response': "Query not recognized. Try asking 'count number of rows' or 'show columns'."})
    except Exception as e:
        return jsonify({'error': f"Error processing query: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
