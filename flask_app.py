from flask import Flask, render_template, request, jsonify
import logging
from werkzeug.utils import secure_filename
from utils.loaf_detector import LoafDetector
import cv2
import numpy as np
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyBCCIsVjh2Rox6khna5fvIO00gCLp0HdzM'

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rate', methods=['POST'])
def rate_loaf():
    try:
        if 'image' not in request.files:
            logger.error("No image file in request")
            return jsonify({'error': 'No image provided'}), 400
       
        file = request.files['image']
       
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
       
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logger.debug(f"Saving file to: {filepath}")
           
            file.save(filepath)
            logger.debug(f"File saved successfully")
           
            try:
                logger.debug("Initializing LoafDetector")
                detector = LoafDetector()
                
                # Add debug logging to check API key status
                logger.debug(f"API Key present: {detector.use_ai}")
                logger.debug(f"API Key first 10 chars: {detector.api_key[:10] if detector.api_key else 'None'}")
               
                logger.debug("Processing image")
                result = detector.rate_loaf(filepath)
                logger.debug(f"Result: {result}")
               
                # Clean up file
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify(result)
               
            except Exception as e:
                logger.exception("Error in image processing")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({
                    'error': f'Error processing image: {str(e)}',
                    'details': str(e.__class__.__name__)
                }), 500
        else:
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
           
    except Exception as e:
        logger.exception("Unexpected error in rate_loaf")
        return jsonify({
            'error': 'Server error',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    # Test API key before starting server
    test_detector = LoafDetector()
    print(f"API Configuration Status: {'✅ AI Enabled' if test_detector.use_ai else '❌ Using Fallback'}")
    app.run(debug=True)