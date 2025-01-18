from flask import Flask, request, jsonify, render_template
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__, static_folder='static', template_folder='templates')

# URL to your dataset
DATASET_PATH = "https://yates.one-name.net/gengen/static/datasets/DNA_Study_Library.xlsx"
dataset = None  # Global variable to store the dataset


# Function to load the dataset
def load_dataset():
    global dataset
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


# Load the dataset when the app starts
load_dataset()


@app.route('/')
def home():
    return render_template('index.html')  # Serve the HTML page


@app.route('/query', methods=['POST'])
def query():
    global dataset
    if dataset is None:
        return jsonify({'error': 'No dataset loaded'}), 400

    user_query = request.json.get('query', '')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        dataset_string = dataset.to_csv(index=False)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": f"Dataset: {dataset_string}\n\nQuery: {user_query}"}
            ]
        )
        analysis = response['choices'][0]['message']['content']
        return jsonify({'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
