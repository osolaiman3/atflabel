from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from bcrypt import hashpw, gensalt, checkpw
import os
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
import threading
import uuid
import time

# Import and use OCRChecker for validation
from ocr_checker import OCRChecker

app = Flask(__name__)
CORS(app) # Enable CORS
auth = HTTPBasicAuth()

# Processing status tracking
is_processing = False  # Simple flag to prevent concurrent submissions
last_result = None  # Store result for client to retrieve
OCR_TIMEOUT = 60  # 60 seconds timeout for OCR processing

# users dictionary for demonstration purposes
salt = gensalt()
users = {
    "user": hashpw("password".encode('utf-8'), salt)
}

"""Verifies password
Using a dict for demo
Returns:
    string: username if verified, None otherwise
"""
@auth.verify_password
def verify_password(username, password):
    print("Verifying user:", username)
    print("verifying password:", password)
    if username in users and checkpw(password.encode('utf-8'), users.get(username)):
        return username
    return None

"""Login endpoint

    Returns:
    json: JWT token on successful authentication
""" 
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET') or app.config.get('SECRET_KEY') or 'please-set-a-secret-key'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt_manager = JWTManager(app)

@app.route('/login', methods=['POST'])
@auth.login_required # This is the key: it forces basic auth on this route
def login_success():
    # If the request makes it here, authentication was successful
    user = auth.current_user()
    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token), 200
    
@app.route('/verify-token', methods=['GET', 'POST'])
@jwt_required()
def verify_token():
    current_user_identity = get_jwt_identity()
    return jsonify(valid=True, user=current_user_identity, message="Token is valid"), 200
    

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected_route():
    return jsonify({
        'data': 'This is protected information!',
        'user': get_jwt_identity()
    }), 200

@app.route('/processing-status', methods=['GET'])
@jwt_required()
def get_processing_status():
    """
    Check if server is currently processing.
    
    Returns:
    - busy: boolean indicating if processing is active
    """
    global is_processing
    return jsonify({
        'busy': is_processing
    }), 200

@app.route('/submit-product', methods=['POST'])
@jwt_required()
def submit_product():
    """
    Submit product information with images for validation.
    Expects multipart/form-data with:
    - brandName (text)
    - productClass (text)
    - alcoholContent (text/number)
    - netContents (text/number)
    - netContentsUnit (text)
    - images (multiple files)
    """
    global is_processing, last_result
    
    # Check if already processing
    if is_processing:
        return jsonify({
            'success': False,
            'error': 'Server is busy processing another submission. Please wait.'
        }), 503
    
    # Mark as processing
    is_processing = True
    last_result = None
    
    # Start processing in a background thread
    thread = threading.Thread(
        target=_process_product,
        args=(request.form, request.files, get_jwt_identity())
    )
    thread.daemon = True
    thread.start()
    thread.join(timeout=OCR_TIMEOUT + 5)  # Wait for thread to complete
    
    # Get result and reset flag
    result = last_result
    is_processing = False
    
    if result is None:
        return jsonify({
            'success': False,
            'error': 'Processing timeout'
        }), 504
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result), 200 if result.get('success') else 400


@app.route('/submit-product', methods=['POST'])
@jwt_required()
def submit_product():
    """
    Submit product information with images for validation.
    Expects multipart/form-data with:
    - brandName (text)
    - productClass (text)
    - alcoholContent (text/number)
    - netContents (text/number)
    - netContentsUnit (text)
    - images (multiple files)
    
    Returns:
    - job_id: ID to check processing status
    - status: 'processing' (will be processed asynchronously)
    """
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    processing_jobs[job_id] = {
        'status': 'processing',
        'start_time': time.time(),
        'result': None,
        'error': None
    }
    
    # Start processing in a background thread
    thread = threading.Thread(
        target=_process_product,
        args=(job_id, request.form, request.files, get_jwt_identity())
    )
    thread.daemon = True
    thread.start()
    
    # Return job ID immediately for client to poll
    return jsonify({
        'job_id': job_id,
        'status': 'processing',
        'message': 'Processing started. Use job_id to check status.'
    }), 202  # 202 Accepted


def _process_product(job_id, form_data, files_data, user):
    """
    Background worker function for OCR processing.
    """
    try:
        # Get form fields
        brand_name = form_data.get('brandName')
        product_class = form_data.get('productClass')
        alcohol_content = form_data.get('alcoholContent')
        net_contents = form_data.get('netContents')
        net_contents_unit = form_data.get('netContentsUnit')
        
        # Get images (kept in memory as binary data)
        image_files = files_data.getlist('images')
        images = []
        
        for image_file in image_files:
            if image_file and image_file.filename:
                # Read image into memory as bytes
                image_data = image_file.read()
                images.append(image_data)
        
        print(f"[Job {job_id}] Processing started for user: {user}")
        print(f"[Job {job_id}] Brand Name: {brand_name}")
        print(f"[Job {job_id}] Product Class: {product_class}")
        print(f"[Job {job_id}] Alcohol Content: {alcohol_content}")
        print(f"[Job {job_id}] Net Contents: {net_contents}")
        print(f"[Job {job_id}] Net Contents Unit: {net_contents_unit}")
        print(f"[Job {job_id}] Number of images received: {len(images)}")
        
        # Check for timeout before processing
        if time.time() - processing_jobs[job_id]['start_time'] > OCR_TIMEOUT:
            raise TimeoutError(f"Processing timeout after {OCR_TIMEOUT} seconds")
        
        # Perform OCR validation
        validation_results = OCRChecker.validate_all(
            images=images,
            brand_name=brand_name,
            product_class=product_class,
            alcohol_content=alcohol_content,
            net_contents=net_contents,
            net_contents_unit=net_contents_unit
        )
        
        # Check if all validations passed
        all_valid = all(result.get('isValid', False) for result in validation_results.values())
        
        # Store result
        processing_jobs[job_id]['result'] = {
            'success': all_valid,
            'validations': validation_results,
            'user': user
        }
        processing_jobs[job_id]['status'] = 'completed'
        
        print(f"[Job {job_id}] Processing completed successfully")
        
    except TimeoutError as e:
        processing_jobs[job_id]['status'] = 'failed'
        processing_jobs[job_id]['error'] = str(e)
        print(f"[Job {job_id}] Timeout error: {e}")
        
    except Exception as e:
        processing_jobs[job_id]['status'] = 'failed'
        processing_jobs[job_id]['error'] = str(e)
        print(f"[Job {job_id}] Error during processing: {e}")

if __name__ == '__main__':
    app.run(debug=True)