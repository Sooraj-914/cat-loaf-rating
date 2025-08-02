from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from utils.loaf_detector import LoafDetector
import cv2
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-api')
def test_api():
    detector = LoafDetector()
    result = detector.test_api_connection()
    return jsonify(result)

@app.route('/rate', methods=['POST'])
def rate_loaf():
    try:
        if 'image' not in request.files:
            print("No image file in request")
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        print(f"Received file: {file.filename}")
        
        if file.filename == '':
            print("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Saving file to: {filepath}")
            
            # Ensure directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)
            print(f"File saved successfully at {filepath}")
            
            try:
                detector = LoafDetector()
                result = detector.rate_loaf(filepath)
                print(f"Processing result: {result}")

                result = detector.rate_loaf(filepath)
                print(f"Actual result structure: {result}")
                print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                # Clean up
                os.remove(filepath)
                return jsonify(result)
                
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': str(e)}), 500
                
        else:
            print(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
