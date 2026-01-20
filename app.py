from flask import Flask, request, jsonify, render_template
import json
import os
import tempfile
import secrets
from datetime import datetime, timezone

app = Flask(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', '')
ENV = os.environ.get('ENV', 'development')

# Debug: Log token status on startup
if ENV == 'development':
    if ADMIN_TOKEN:
        # Mask token for security (show first 4 and last 4 chars)
        masked = ADMIN_TOKEN[:4] + '*' * max(0, len(ADMIN_TOKEN) - 8) + ADMIN_TOKEN[-4:] if len(ADMIN_TOKEN) > 8 else '***'
        # NOTE: Avoid emojis/unicode here to prevent Windows console UnicodeEncodeError.
        print(f"[INFO] ADMIN_TOKEN loaded: {masked} (length: {len(ADMIN_TOKEN)})")
    else:
        print("[WARN] ADMIN_TOKEN not set! POST /api/data and /admin will be blocked.")
        print("       Set it with: $env:ADMIN_TOKEN = 'your-token-here'")

# Security: Request size limit (1MB)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# Validation limits
MAX_MODELS = 100
MAX_ITEMS_PER_MODEL = 500
MAX_STRING_LENGTH = 1000
MAX_NAME_LENGTH = 200

# Đảm bảo file data tồn tại
def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"models": [], "version": 1, "updatedAt": datetime.now(timezone.utc).isoformat()}, f, indent=4, ensure_ascii=False)

ensure_data_file()


# Helper: load data with sane defaults
def read_data_file():
    ensure_data_file()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {"models": []}

    if not isinstance(data, dict):
        data = {"models": []}

    if 'models' not in data or not isinstance(data.get('models'), list):
        data['models'] = []

    # Versioning defaults
    if not isinstance(data.get('version'), int):
        data['version'] = 1
    if 'updatedAt' not in data:
        try:
            ts = os.path.getmtime(DATA_FILE)
            data['updatedAt'] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        except Exception:
            data['updatedAt'] = datetime.now(timezone.utc).isoformat()

    return data

# =========================
# SECURITY HELPERS
# =========================

def check_admin_token():
    """Verify Bearer token from Authorization header"""
    if not ADMIN_TOKEN:
        if ENV == 'development':
            app.logger.warning("ADMIN_TOKEN not configured on server")
        return False, "Admin token not configured on server"
    
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return False, "Missing Authorization header"
    
    if not auth_header.startswith('Bearer '):
        return False, "Authorization header must start with 'Bearer '"
    
    token = auth_header[7:].strip()
    if not token:
        return False, "Token is empty"
    
    if not secrets.compare_digest(token, ADMIN_TOKEN):
        if ENV == 'development':
            # In development, show more details
            app.logger.warning(f"Token mismatch. Received length: {len(token)}, Expected length: {len(ADMIN_TOKEN)}")
        return False, "Invalid token"
    
    return True, None

def validate_data_schema(data):
    """Validate JSON payload structure and content"""
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object"
    
    if 'models' not in data:
        return False, "Missing 'models' field"
    
    if not isinstance(data['models'], list):
        return False, "'models' must be an array"
    
    if len(data['models']) > MAX_MODELS:
        return False, f"Too many models (max {MAX_MODELS})"
    
    for model in data['models']:
        if not isinstance(model, dict):
            return False, "Each model must be an object"
        
        # Validate model fields
        if 'items' in model:
            if not isinstance(model['items'], list):
                return False, "Model 'items' must be an array"
            if len(model['items']) > MAX_ITEMS_PER_MODEL:
                return False, f"Too many items per model (max {MAX_ITEMS_PER_MODEL})"
            
            for item in model['items']:
                if not isinstance(item, dict):
                    return False, "Each item must be an object"
                
                # Validate item fields
                if 'name' in item and len(str(item['name'])) > MAX_NAME_LENGTH:
                    return False, f"Item name too long (max {MAX_NAME_LENGTH})"
                
                if 'content' in item and len(str(item['content'])) > MAX_STRING_LENGTH:
                    return False, f"Item content too long (max {MAX_STRING_LENGTH})"
                
                if 'link' in item and len(str(item['link'])) > MAX_STRING_LENGTH:
                    return False, f"Item link too long (max {MAX_STRING_LENGTH})"
                
                # Validate world coordinates
                if 'world' in item:
                    if not isinstance(item['world'], list) or len(item['world']) != 3:
                        return False, "Item 'world' must be array of 3 numbers"
                    for coord in item['world']:
                        if not isinstance(coord, (int, float)):
                            return False, "World coordinates must be numbers"
                
                # Validate camera
                if 'cam' in item:
                    if not isinstance(item['cam'], dict):
                        return False, "Item 'cam' must be an object"
                    if 'position' in item['cam']:
                        if not isinstance(item['cam']['position'], list) or len(item['cam']['position']) != 3:
                            return False, "Camera position must be array of 3 numbers"
                    if 'target' in item['cam']:
                        if not isinstance(item['cam']['target'], list) or len(item['cam']['target']) != 3:
                            return False, "Camera target must be array of 3 numbers"
    
    return True, None

def atomic_write_file(filepath, data):
    """Write file atomically using temp file + replace"""
    try:
        # Write to temp file first
        temp_fd, temp_path = tempfile.mkstemp(dir=BASE_DIR, suffix='.tmp', prefix='data_')
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            # Atomic replace
            os.replace(temp_path, filepath)
        except Exception as e:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise e
    except Exception as e:
        raise Exception(f"Failed to write file: {str(e)}")

# =========================
# SECURITY HEADERS
# =========================

@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # CSP: Allow Sketchfab, Tailwind CDN, and same-origin
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://static.sketchfab.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "frame-src 'self' https://sketchfab.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://sketchfab.com;"
    )
    response.headers['Content-Security-Policy'] = csp
    
    return response

# =========================
# ROUTES GIAO DIỆN
# =========================

@app.route('/')
def index():
    return render_template('guest.html')

@app.route('/admin')
def admin():
    # Admin route - có thể thêm token check ở đây nếu cần
    # Hiện tại để public nhưng POST API đã được bảo vệ
    return render_template('admin.html')

@app.route('/mindmap_order.json')
def mindmap_order():
    """Serve mindmap order JSON file"""
    try:
        order_file = os.path.join(BASE_DIR, 'mindmap_order.json')
        if os.path.exists(order_file):
            with open(order_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        return jsonify({"error": "mindmap_order.json not found"}), 404
    except Exception as e:
        if ENV == 'development':
            return jsonify({"error": str(e)}), 500
        return jsonify({"error": "Internal server error"}), 500

# =========================
# API
# =========================

@app.route('/api/data', methods=['GET'])
def get_data():
    """Public read-only endpoint"""
    try:
        data = read_data_file()
        resp = jsonify(data)
        # Avoid stale caches on API responses
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        resp.headers['ETag'] = f"W/\"{data.get('version', 0)}\""
        return resp
    except Exception as e:
        if ENV == 'development':
            return jsonify({"error": str(e), "models": []}), 500
        return jsonify({"error": "Internal server error", "models": []}), 500

@app.route('/api/debug/token-status', methods=['GET'])
def debug_token_status():
    """Debug endpoint - chỉ hoạt động trong development mode"""
    if ENV != 'development':
        return jsonify({"error": "Not available in production"}), 404
    
    if ADMIN_TOKEN:
        masked = ADMIN_TOKEN[:4] + '*' * max(0, len(ADMIN_TOKEN) - 8) + ADMIN_TOKEN[-4:] if len(ADMIN_TOKEN) > 8 else '***'
        return jsonify({
            "status": "set",
            "length": len(ADMIN_TOKEN),
            "masked": masked,
            "first_4": ADMIN_TOKEN[:4] if len(ADMIN_TOKEN) >= 4 else "",
            "last_4": ADMIN_TOKEN[-4:] if len(ADMIN_TOKEN) >= 4 else "",
            "hint": "Compare first_4 and last_4 with your token to verify"
        })
    else:
        return jsonify({
            "status": "not_set",
            "warning": "ADMIN_TOKEN environment variable is not set",
            "hint": "Set it with: $env:ADMIN_TOKEN = 'your-token-here'"
        })

@app.route('/api/data', methods=['POST'])
def save_data():
    """Protected write endpoint - requires Bearer token"""
    # Check authentication
    is_valid, error_msg = check_admin_token()
    if not is_valid:
        if ENV == 'development':
            app.logger.warning(f"Authentication failed: {error_msg}")
        return jsonify({"error": error_msg}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate schema
        is_valid, error_msg = validate_data_schema(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        # Versioning: increment server version & updatedAt
        current = read_data_file()
        next_version = int(current.get('version', 0)) + 1
        data['version'] = next_version
        data['updatedAt'] = datetime.now(timezone.utc).isoformat()

        # Atomic write
        atomic_write_file(DATA_FILE, data)

        resp = jsonify({"status": "success", "version": next_version, "updatedAt": data['updatedAt']})
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        resp.headers['ETag'] = f"W/\"{next_version}\""
        return resp
    except ValueError as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400
    except Exception as e:
        if ENV == 'development':
            return jsonify({"error": str(e)}), 500
        return jsonify({"error": "Internal server error"}), 500

# =========================
# ERROR HANDLERS
# =========================

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "Request too large"}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    if ENV == 'development':
        return jsonify({"error": str(error)}), 500
    return jsonify({"error": "Internal server error"}), 500

# =========================
# CHẠY LOCAL
# =========================
if __name__ == '__main__':
    # Development mode
    if ENV == 'production':
        # Production should use gunicorn
        print("WARNING: Running in production mode. Use gunicorn instead.")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=(ENV != 'production'))
