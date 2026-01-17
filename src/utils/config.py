# ========== Imports ==========
import os
from pathlib import Path

class Config:
    """
    Application configuration settings for the AI Study Material Generator.

    This class contains all the important settings and paths that the application needs:
    - File upload settings (where to save files, size limits)
    - Database settings (where to store data)
    - Output folders (where to save generated materials)
    - Video processing settings
    - Security settings for Flask web app
    """
    
    # ========== Base Directory Setup ==========
    # Get the main project folder (goes up 3 levels from this file)
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # ========== Flask Web App Settings ==========
    # Secret key for Flask security (encrypting sessions, etc.)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Development or production mode
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # ========== File Upload Settings ==========
    # Folder where uploaded files are temporarily stored
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    # Maximum file size allowed (100MB for videos, PDFs, etc.)
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 100 * 1024 * 1024))
    # File types that users can upload
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'mp4', 'avi', 'mov', 'mkv', 'webm'}
    
    # ========== Output Folder Settings ==========
    # Main folder where all generated study materials are saved
    OUTPUT_FOLDER = BASE_DIR / 'outputs'
    # Specific subfolders for different types of generated content
    FLASHCARDS_FOLDER = OUTPUT_FOLDER / 'flashcards'        # Q&A cards saved here
    SUMMARIES_FOLDER = OUTPUT_FOLDER / 'summaries'          # Text summaries saved here
    CONCEPT_MAPS_FOLDER = OUTPUT_FOLDER / 'concept_maps'    # Visual concept maps saved here
    LEARNING_PATHS_FOLDER = OUTPUT_FOLDER / 'learning_paths' # Study plans saved here
    TRANSCRIPTS_FOLDER = OUTPUT_FOLDER / 'transcripts'      # Video transcripts saved here
    
    # ========== Database Settings ==========
    # Path to SQLite database file where all data is stored
    DATABASE_PATH = BASE_DIR / 'data' / 'study_materials.db'
    
    # ========== Natural Language Processing Settings ==========
    # Minimum number of flashcards to generate per file
    MIN_FLASHCARDS = 10
    # Maximum number of flashcards to generate per file
    MAX_FLASHCARDS = 50
    # How much to compress text when making summaries (0.3 = 30% of original length)
    SUMMARY_RATIO = 0.3
    
    # ========== Video Processing Settings ==========
    # How long each audio chunk should be when processing videos (in seconds)
    VIDEO_CHUNK_DURATION = 60
    # Audio quality setting for speech recognition
    AUDIO_SAMPLE_RATE = 16000
    # Language setting for speech-to-text conversion
    SPEECH_RECOGNITION_LANGUAGE = 'en-US'
    
    # ========== Folder Creation Method ==========
    @classmethod
    def init_folders(cls):
        """
        Create all necessary folders if they don't exist.

        This method is called when the app starts to make sure all required
        folders exist before users start uploading files or the app tries
        to save generated materials.

        Creates folders for:
        - File uploads
        - Generated outputs (flashcards, summaries, etc.)
        - Database storage
        - Video transcripts
        """
        # List of all folders that need to exist
        folders = [
            cls.UPLOAD_FOLDER,          # Where uploaded files go
            cls.OUTPUT_FOLDER,          # Main output folder
            cls.FLASHCARDS_FOLDER,      # Generated flashcards
            cls.SUMMARIES_FOLDER,       # Generated summaries
            cls.CONCEPT_MAPS_FOLDER,    # Generated concept maps
            cls.LEARNING_PATHS_FOLDER,  # Generated learning paths
            cls.TRANSCRIPTS_FOLDER,     # Video transcripts
            cls.DATABASE_PATH.parent    # Database folder
        ]
        
        # Create each folder (including parent folders if needed)
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)