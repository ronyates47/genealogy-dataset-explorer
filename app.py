import requests
import pandas as pd
from flask import Flask, request, jsonify, render_template
from io import BytesIO

app = Flask(__name__, static_folder="static", template_folder="templates")

# Dataset location
DATASET_URL = "https://yates.one-name.net/gengen/static/datasets/DNA_Study_Library.xlsx"
dataset = None  # Global variable to store the dataset


@app.before_first_request
def load_dataset():
    """Fetch and load the dataset from the server."""
    global dataset
    try:
        print(f"Fetching dataset from: {DATASET_URL}")
        response = requests.get(DATASET_URL)
        response.raise_for_status()
        dataset = pd.read_excel(BytesIO(response.content))
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        dataset = None


@app.route("/")
def home():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    """Handle user queries on the dataset."""
    global dataset
    if dataset is None:
        return jsonify({"error": "Dataset not loaded. Please try again later."}), 500

    user_query = request.json.get("query", "").strip()
    if not user_query:
        return jsonify({"error": "No query provided."}), 400

    try:
        # Convert the dataset to CSV for analysis
        dataset_string = dataset.to_csv(index=False)

        # Simulated OpenAI response (replace with your API logic)
        analysis = f"Simulated analysis for query: {user_query}"

        return jsonify({"analysis": analysis})

    except Exception as e:
        return jsonify({
            "error": "Could not process query.",
            "fallback": "Here is a preview of the dataset.",
            "dataset": dataset.head(10).to_dict(orient="records")
        })


if __name__ == "__main__":
    app.run(debug=True)
