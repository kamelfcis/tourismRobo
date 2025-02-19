from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from roboflow import Roboflow

import os

# Initialize Flask app
app = Flask(__name__)

# Set up Roboflow
rf = Roboflow(api_key="cwWfQjtnh6TbErsY0e9X")
project = rf.workspace().project("identifying-egyptian-artifacts")
model = project.version(2).model

# Set a folder to store uploaded images temporarily
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions for image upload
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API endpoint for image upload 
@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Use the Roboflow model for inference
            result = model.predict(filepath).json()
            
            # Extract the "top" prediction
            top_prediction = result.get('predictions', [{}])[0].get('top', None)
            
            if top_prediction:
                return jsonify({"top_prediction": top_prediction})
            else:
                return jsonify({"error": "No top prediction found"}), 500
        
        except Exception as e:
            return jsonify({"error": f"Error during inference: {str(e)}"}), 500

    return jsonify({"error": "Invalid file type. Only JPG, JPEG, and PNG are allowed."}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Use the Roboflow model for inference
            result = model.predict(filepath).json()
            return jsonify(result)
        
        except Exception as e:
            return jsonify({"error": f"Error during inference: {str(e)}"}), 500

    return jsonify({"error": "Invalid file type. Only JPG, JPEG, and PNG are allowed."}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
