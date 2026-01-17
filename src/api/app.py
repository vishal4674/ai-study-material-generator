# ========== Imports ==========
from flask import Flask
from pathlib import Path
import sys

# ========== Path Setup ==========
# Add project root to Python path for easy imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ========== Config & Database ==========
from src.utils.config import Config
from src.storage.database import Database

def create_app():
    """
    Create and configure the Flask application.

    - Sets up Flask app with template and static folders.
    - Loads configuration and sets secret key, upload folder, and max file size.
    - Initializes required folders and the database.
    - Registers all routes for the app.
    - Returns the configured Flask app instance.
    """
    app = Flask(
        __name__,
        template_folder=str(project_root / 'templates'),
        static_folder=str(project_root / 'static')
    )

    # Set secret key and upload settings
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['UPLOAD_FOLDER'] = str(Config.UPLOAD_FOLDER)
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE

    # Create all necessary folders (uploads, outputs, etc.)
    Config.init_folders()

    # Initialize the database and attach to app config
    db = Database(Config.DATABASE_PATH)
    app.config['DATABASE'] = db

    # Register all Flask routes (views, APIs, etc.)
    from src.api.routes import register_routes
    register_routes(app)

    return app

# ========== Main Entry Point ==========
if __name__ == '__main__':
    # Start the Flask development server
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)