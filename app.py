from flask import Flask, request, jsonify, render_template
import json
import os
import tempfile
import secrets
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
import ssl
import pg8000.dbapi

app = Flask(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Allow overriding data file location via environment variable.
# This is important for production (e.g. Render) where you mount
# a persistent disk and point DATA_PATH to that location so that
# all clients share ONE central source of truth.
DATA_PATH = os.environ.get("DATA_PATH", os.path.join(BASE_DIR, "data.json"))
DATA_FILE = DATA_PATH

ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', '')
ENV = os.environ.get('ENV', 'development')
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
USE_DATABASE = bool(DATABASE_URL)

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
    # Create directory for DATA_FILE if needed
    data_dir = os.path.dirname(DATA_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"models": [], "version": 1, "updatedAt": datetime.now(timezone.utc).isoformat()}, f, indent=4, ensure_ascii=False)

ensure_data_file()


def get_db_connection():
    """Create a new DB connection (Postgres)."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set")
    url = urlparse(DATABASE_URL)
    if url.scheme not in ("postgres", "postgresql"):
        raise ValueError("DATABASE_URL must start with postgres:// or postgresql://")

    query = parse_qs(url.query or "")
    sslmode = (query.get("sslmode") or [""])[0]
    ssl_context = None
    if sslmode == "require":
        ssl_context = ssl.create_default_context()

    return pg8000.dbapi.connect(
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port or 5432,
        database=url.path.lstrip("/"),
        ssl_context=ssl_context
    )


def init_db():
    if not USE_DATABASE:
        return
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
                CREATE TABLE IF NOT EXISTS data_store (
                    id INTEGER PRIMARY KEY,
                    data JSONB NOT NULL,
                    version INTEGER NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL
                )
            """)
        conn.commit()
    finally:
        conn.close()


def ensure_data_store():
    """Ensure a single row exists in DB; seed from file if empty."""
    if not USE_DATABASE:
        return
    init_db()
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM data_store WHERE id = 1")
        row = cur.fetchone()
        if row:
            return
        seed = read_data_file()
        version = int(seed.get("version", 1))
        updated_at = seed.get("updatedAt", datetime.now(timezone.utc).isoformat())
        cur.execute(
            "INSERT INTO data_store (id, data, version, updated_at) VALUES (1, %s, %s, %s)",
            (json.dumps({"models": seed.get("models", [])}, ensure_ascii=False), version, updated_at),
        )
        conn.commit()
    finally:
        conn.close()

# Initialize DB on startup (after ensure_data_store is defined)
if USE_DATABASE:
    try:
        ensure_data_store()
    except Exception as e:
        if ENV == 'development':
            app.logger.warning(f"Failed to init database, falling back to file: {e}")
        USE_DATABASE = False


def read_data_store():
    """Read data from DB (or file fallback) with defaults."""
    if not USE_DATABASE:
        return read_data_file()
    ensure_data_store()
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT data, version, updated_at FROM data_store WHERE id = 1")
        row = cur.fetchone()
        if not row:
            return {"models": [], "version": 1, "updatedAt": datetime.now(timezone.utc).isoformat()}
        raw_data, version, updated_at = row
        data = raw_data if isinstance(raw_data, dict) else json.loads(raw_data)
        if "models" not in data or not isinstance(data.get("models"), list):
            data["models"] = []
        data["version"] = int(version)
        data["updatedAt"] = updated_at.astimezone(timezone.utc).isoformat() if updated_at else datetime.now(timezone.utc).isoformat()
        return data
    finally:
        conn.close()


def write_data_store(data):
    """Write data to DB (or file fallback) with versioning."""
    if not USE_DATABASE:
        current = read_data_file()
        next_version = int(current.get("version", 0)) + 1
        data["version"] = next_version
        data["updatedAt"] = datetime.now(timezone.utc).isoformat()
        atomic_write_file(DATA_FILE, data)
        return data

    ensure_data_store()
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT version FROM data_store WHERE id = 1 FOR UPDATE")
        row = cur.fetchone()
        current_version = int(row[0]) if row else 0
        next_version = current_version + 1
        updated_at = datetime.now(timezone.utc)
        payload = {"models": data.get("models", [])}
        cur.execute(
            "UPDATE data_store SET data = %s, version = %s, updated_at = %s WHERE id = 1",
            (json.dumps(payload, ensure_ascii=False), next_version, updated_at),
        )
        conn.commit()
    finally:
        conn.close()
    data["version"] = next_version
    data["updatedAt"] = updated_at.isoformat()
    return data


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
        data = read_data_store()
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

        # Write to DB (or file fallback) with versioning
        saved = write_data_store(data)

        resp = jsonify({"status": "success", "version": saved.get("version"), "updatedAt": saved.get("updatedAt")})
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        resp.headers['ETag'] = f"W/\"{saved.get('version', 0)}\""
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
