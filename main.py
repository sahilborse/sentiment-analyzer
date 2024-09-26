from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
from dotenv import load_dotenv
import requests


load_dotenv()
app = Flask(__name__)

GROQ_API_URL = os.getenv('GROQ_URL')

@app.route('/',methods=['GET'])
def mainer():
     return render_template('index.html',error="")

@app.route('/upload',methods=['GET'])
def upload_check():
    return "upload available"

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file is part of the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Validate file extension
    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        return jsonify({'error': 'Unsupported file type. Only CSV and XLSX are allowed.'}), 400

    # Read the file into a DataFrame
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
    except Exception as e:
        return render_template("index.html",error=e)

    # Check if 'review' column exists
    if 'review' not in df.columns:
        return jsonify({'error': 'No "review" column found in the file'}), 400

    # Extract reviews
    reviews = df['review'].tolist()

    
    
    if len(reviews) < 50:
        return jsonify({'error': f'Expected 50 reviews, but got {len(reviews)}.'}), 400
    # Groq api for sentimental analysis
    # Return the extracted reviews
    sentiment_scores = analyze_sentiment(reviews)
   
  



def analyze_sentiment(reviews):
    payload = {"reviews": reviews}
    try:
        response = requests.post(GROQ_API_URL, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
    
        # Extract scores (adapt as necessary based on Groq API response format)
        positive_score = data.get("positive", 0)
        negative_score = data.get("negative", 0)
        neutral_score = data.get("neutral", 0)
          
          
        return render_template("output.html",postive=positive_score,negative=negative_score,neutral=neutral_score)
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500
    
    
    
    
    
    
if __name__ == '__main__':
    app.run(debug=True)
