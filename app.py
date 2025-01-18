from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)  # Initialize Flask app

# Global variable to store the uploaded dataset
dataset = None

# Basic route to verify the app is running
@app.route('/')
def home():
    return "Flask app is running!"

# Route to handle file uploads
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

if __name__ == "__main__":
    app.run(debug=True)

    curl -X POST -F "file=@path_to_file.xlsx" https://ronyates47.pythonanywhere.com/upload

