from flask import Flask, request, jsonify, send_from_directory
from flask_httpauth import HTTPBasicAuth
from bcrypt import hashpw, gensalt, checkpw
import os
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
import threading
import time
from pathlib import Path
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    # Create logger early for this message
    logging.warning("dotenv not installed, proceeding without loading .env file")
    pass  # Will use defaults if dotenv not available

from ocr_checker import OCRChecker

ocrchecker = OCRChecker(modelSelect=os.environ.get('OCR_MODEL', 'easyocr'))

# Configure Flask to serve React static files
# BUILD_PATH can be set via environment variable for Docker/production
build_path = os.environ.get('BUILD_PATH', os.path.join(os.path.dirname(__file__), '../../atffront/build'))
app = Flask(
    __name__,
    static_folder=build_path if os.path.exists(build_path) else None,
    static_url_path=''
)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

CORS(app)  # Enable CORS
auth = HTTPBasicAuth()

# Processing status tracking
is_processing = False  # Simple flag to prevent concurrent submissions
last_result = None  # Store result for client to retrieve
oimages = None  # Store processed images for client to retrieve

OCR_TIMEOUT = int(os.environ.get('OCR_TIMEOUT', 60))  # 60 seconds timeout for OCR processing

# Configuration from environment variables
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET', 'dev-jwt-secret-change-in-production')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=int(os.environ.get('JWT_EXPIRATION_HOURS', 1)))

# User credentials from environment
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'user')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')

# Setup authentication
salt = gensalt()
users = {
    ADMIN_USERNAME: hashpw(ADMIN_PASSWORD.encode('utf-8'), salt)
}

jwt_manager = JWTManager(app)

@auth.verify_password
def verify_password(username, password):
    """Verify password against stored credentials."""
    app.logger.info(f"Verifying user: {username}")
    if username in users and checkpw(password.encode('utf-8'), users.get(username)):
        return username
    return None

@app.route('/login', methods=['POST', 'GET'])
@auth.login_required
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
    - images (allows multiple files)
    """
    global is_processing, last_result
    
    # Check if already processing
    if is_processing:
        return jsonify({
            'success': False,
            'error': 'Server is busy processing another submission. Please wait.'
        }), 503
        
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes
    image_files = request.files.getlist('images')
    
    #check sizes of all images
    for image_file in image_files:
        if image_file and image_file.filename:
            # Check file size by seeking to end
            image_file.seek(0, os.SEEK_END)
            file_size = image_file.tell()
            image_file.seek(0)  # Reset file pointer
            
            if file_size > MAX_IMAGE_SIZE:
                is_processing = False
                return jsonify({
                    'success': False,
                    'error': f'Image "{image_file.filename}" exceeds 5 MB limit. Size: {file_size / (1024*1024):.2f} MB'
                }), 413
    #TODO: proper file type checking
        
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
    last_result = None  # Clear last result after retrieval
    
    if result is None:
        return jsonify({
            'success': False,
            'error': 'Processing timeout'
        }), 504
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result), 200 if result.get('success') else 200


def _process_product(form_data, files_data, user):
    """
    Background worker function for OCR processing.
    """
    global last_result
    
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
        
        app.logger.info("Received the following data for validation:")
        app.logger.info(f"Brand Name: {brand_name}")
        app.logger.info(f"Product Class: {product_class}")
        app.logger.info(f"Alcohol Content: {alcohol_content}")
        app.logger.info(f"Net Contents: {net_contents}")
        app.logger.info(f"Net Contents Unit: {net_contents_unit}")
        app.logger.info(f"Number of images received: {len(images)}")
        
        # Perform OCR validation
        validation_results, oimages = ocrchecker.validate(
            images=images,
            brand_name=brand_name,
            product_class=product_class,
            alcohol_content=alcohol_content,
            net_contents=net_contents,
            net_contents_unit=net_contents_unit
        )
        
        app.logger.info(f"Validation results: {validation_results}")
        
        all_valid = all(validation_results.values())
        
        # Convert images to base64 for JSON response
        import base64
        images_base64 = []
        for img_data in oimages:
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            images_base64.append(f"data:image/jpeg;base64,{img_b64}")
        
        # Store result
        last_result = {
            'success': all_valid,
            'validations': validation_results,
            'user': user,
            'images': images_base64
        }
        
        
        
        app.logger.info("Processing completed successfully")
        
    except Exception as e:
        last_result = {
            'success': False,
            'error': str(e)
        }
        app.logger.error(f"Error during processing: {e}", exc_info=True)

# ============================================
# React Frontend Serving Routes
# ============================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """
    Serve React app for all non-API routes.
    This allows React Router to handle client-side routing.
    """
    # List of API routes that should not be served as React
    api_routes = [
        'login', 'verify-token', 'submit-product', 'processing-status',
        'api/', 'protected'
    ]
    
    # Check if this is an API route
    for route in api_routes:
        if path.startswith(route):
            return jsonify({'error': 'Not found'}), 404
    
    # Try to serve the static file
    if path and os.path.exists(os.path.join(build_path, path)):
        return send_from_directory(build_path, path)
    
    # Serve index.html for all other routes (React Router handles it)
    index_path = os.path.join(build_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(build_path, 'index.html')
    else:
        return jsonify({'error': 'React app not built. Run: cd ../atffront && npm run build'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = FLASK_ENV == 'development'
    
    app.logger.info(f"{'='*60}")
    app.logger.info(f"ATF Label Application")
    app.logger.info(f"Environment: {FLASK_ENV}")
    app.logger.info(f"Server: http://{host}:{port}")
    app.logger.info(f"Debug: {debug}")
    app.logger.info(f"{'='*60}")
    
    app.run(host=host, port=port, debug=debug)