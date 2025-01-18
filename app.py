from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import openai
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

openai.api_key = os.getenv("OPENAI_API_KEY")  # Use your environment variable for security

# Global variable to store the uploaded dataset
dataset = None

@app.route('/')
def home():
    return render_template('index.html')  # Serve the HTML page

@app.route('/upload', methods=['POST'])
def upload():
    global dataset
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    try:
        # Read the uploaded file into a Pandas DataFrame
        dataset = pd.read_excel(file)
        dataset_html = dataset.head(10).to_html(index=False)  # Convert first 10 rows to HTML
        return jsonify({'message': 'File uploaded successfully', 'data': dataset_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/query', methods=['POST'])
def query():
    global dataset
    if dataset is None:
        return jsonify({'error': 'No dataset uploaded'}), 400

    user_query = request.json.get('query', '')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Convert the dataset to a CSV string
        dataset_string = dataset.to_csv(index=False)

        # Send the dataset and query to ChatGPT using the updated API structure
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

