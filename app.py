from flask import Flask, request, jsonify, render_template
import pandas as pd
import openai
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

openai.api_key = os.getenv("OPENAI_API_KEY")  # Use your environment variable for security

# Load the dataset from a fixed location on the server
DATASET_PATH = "https://yates.one-name.net/gengen/static/datasets/DNA_Study_Library.xlsx"  # Update this path to your dataset's location
dataset = None  # Global variable to store the dataset

@app.before_first_request
def load_dataset():
    global dataset
    try:
        dataset = pd.read_excel(DATASET_PATH)
        print(f"Dataset loaded successfully from {DATASET_PATH}")
    except FileNotFoundError:
        print(f"File not found at {DATASET_PATH}. Check the path and ensure the file exists.")
    except Exception as e:
        print(f"Error loading dataset: {e}")


@app.route('/')
def home():
    return render_template('index.html')  # Serve the HTML page

@app.route('/query', methods=['POST'])
def query():
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
        response = openai.Chat.create(
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
