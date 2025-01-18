import os
import requests
import pandas as pd
from flask import Flask, request, jsonify, render_template

# Initialize Flask app
app = Flask(__name__)

# URL to your dataset
DATASET_URL = "https://yates.one-name.net/gengen/static/datasets/DNA_Study_Library.xlsx"
dataset = None  # Global variable to hold the dataset

# Load the dataset when the app starts
@app.before_first_request
def load_dataset():
    global dataset
    try:
        # Download the dataset from the server
        response = requests.get(DATASET_URL)
        response.raise_for_status()
        dataset = pd.read_excel(response.content)
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"Error loading dataset: {e}")

# Home route to serve the HTML page
@app.route("/")
def home():
    return render_template("index.html")

# Query route for handling AI-based queries
@app.route("/query", methods=["POST"])
def query():
    global dataset
    if dataset is None:
        return jsonify({"error": "Dataset not loaded."}), 500

    user_query = request.json.get("query", "")
    if not user_query:
        return jsonify({"error": "No query provided."}), 400

    try:
        # Prepare dataset as a string
        dataset_string = dataset.to_csv(index=False)

        # Query OpenAI API
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure the API key is set in the environment

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst who provides insights from datasets."},
                {"role": "user", "content": f"Dataset: {dataset_string}\n\nQuery: {user_query}"}
            ],
        )

        # Extract AI response
        analysis = response['choices'][0]['message']['content']
        return jsonify({"analysis": analysis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

