# ========== Imports ==========
import os
import re
from datetime import datetime
from werkzeug.utils import secure_filename

class Helpers:
    """
    Common utility functions for the AI Study Material Generator.

    This class provides helpful functions that are used throughout the application:
    - File validation (checking if uploads are allowed)
    - Filename security (making filenames safe)
    - Text cleaning (removing unwanted characters)
    - Date formatting (making dates readable)
    - ID generation (creating unique identifiers)
    """

    # ========== File Validation Methods ==========

    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """
        Check if the uploaded file type is allowed.

        This prevents users from uploading dangerous files or unsupported formats.
        Only allows files with extensions in the allowed_extensions set.

        Args:
            filename (str): Name of the file to check
            allowed_extensions (set): Set of allowed file extensions (like {'pdf', 'txt'})

        Returns:
            bool: True if file is allowed, False if not allowed

        Example:
            >>> Helpers.allowed_file('document.pdf', {'pdf', 'txt'})
            True
            >>> Helpers.allowed_file('virus.exe', {'pdf', 'txt'})
            False
        """
        # Check if filename has a dot (indicating an extension)
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    # ========== Filename Security Methods ==========

    @staticmethod
    def secure_filename_with_timestamp(filename):
        """
        Create a secure filename with timestamp to avoid conflicts.

        Takes a user-provided filename and makes it safe for the filesystem
        by removing dangerous characters and adding a timestamp to make it unique.

        Args:
            filename (str): Original filename from user upload

        Returns:
            str: Safe filename with timestamp added

        Example:
            >>> Helpers.secure_filename_with_timestamp('My Document.pdf')
            'My_Document_20240117_143052.pdf'
        """
        # First, make the filename safe using werkzeug's secure_filename
        name = secure_filename(filename)
        
        # Create timestamp string (Year-Month-Day_Hour-Minute-Second)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Split filename into name and extension
        name_parts = name.rsplit('.', 1)
        
        if len(name_parts) == 2:
            # If file has extension, add timestamp before extension
            return f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        
        # If no extension, just add timestamp at the end
        return f"{name}_{timestamp}"

    # ========== Text Processing Methods ==========

    @staticmethod
    def clean_text(text):
        """
        Clean and normalize text by removing unwanted characters.

        Removes extra spaces, special characters, and other text artifacts
        that might interfere with processing.

        Args:
            text (str): Raw text to clean

        Returns:
            str: Cleaned and normalized text

        Example:
            >>> Helpers.clean_text('Hello    world!!! @#$')
            'Hello world!'
        """
        # Remove extra whitespace (multiple spaces become single space)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        # Keep: letters, numbers, spaces, periods, commas, question marks, exclamation marks
        text = re.sub(r'[^\w\s\.\,\?\!]', '', text)
        
        # Remove leading and trailing whitespace
        return text.strip()

    # ========== File Information Methods ==========

    @staticmethod
    def get_file_extension(filename):
        """
        Extract the file extension from a filename.

        Gets the part after the last dot in lowercase for consistency.

        Args:
            filename (str): Name of the file

        Returns:
            str: File extension in lowercase (without the dot)

        Example:
            >>> Helpers.get_file_extension('document.PDF')
            'pdf'
            >>> Helpers.get_file_extension('noextension')
            ''
        """
        # Check if filename contains a dot
        if '.' in filename:
            # Split by dot and take the last part (extension)
            return filename.rsplit('.', 1)[1].lower()
        else:
            # No extension found
            return ''

    # ========== Date and Time Methods ==========

    @staticmethod
    def format_date(date_obj):
        """
        Format a datetime object into a readable string.

        Converts datetime objects to a standard string format for display
        in the user interface.

        Args:
            date_obj (datetime): Python datetime object

        Returns:
            str: Formatted date string

        Example:
            >>> from datetime import datetime
            >>> dt = datetime(2024, 1, 17, 14, 30, 52)
            >>> Helpers.format_date(dt)
            '2024-01-17 14:30:52'
        """
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')

    # ========== ID Generation Methods ==========

    @staticmethod
    def generate_unique_id():
        """
        Generate a unique identifier based on current timestamp.

        Creates a unique string that can be used as an ID for records,
        files, or other objects that need unique identification.

        Returns:
            str: Unique ID string based on timestamp

        Example:
            >>> Helpers.generate_unique_id()
            '20240117143052123456'
        """
        # Create ID using: Year-Month-Day-Hour-Minute-Second-Microsecond
        return datetime.now().strftime('%Y%m%d%H%M%S%f')