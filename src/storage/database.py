# ========== Imports ==========
import sqlite3
from datetime import datetime
from pathlib import Path

class Database:
    """
    Handle all database operations for the AI Study Material Generator.

    This class manages SQLite database interactions including:
    - Creating and initializing database tables
    - Saving and retrieving study materials
    - Managing flashcards, summaries, and topics
    - Providing search functionality
    """

    def __init__(self, db_path):
        """
        Initialize the database connection and create required tables.

        Args:
            db_path (str or Path): Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        # Create parent directories if they don't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # Initialize database with all required tables
        self._init_database()

    # ========== Database Initialization ==========

    def _init_database(self):
        """
        Initialize database with all required tables.

        Creates four main tables:
        - materials: Store uploaded file information
        - flashcards: Store generated question-answer pairs
        - summaries: Store text summaries and key points
        - topics: Store extracted topics for each material
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Materials table - stores basic file information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                status TEXT DEFAULT 'processed'
            )
        """)

        # Flashcards table - stores generated Q&A pairs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                topic TEXT,
                difficulty TEXT,
                card_type TEXT,
                FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
            )
        """)

        # Summaries table - stores generated text summaries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER NOT NULL,
                summary_text TEXT NOT NULL,
                key_points TEXT,
                compression_ratio REAL,
                FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
            )
        """)

        # Topics table - stores extracted topics from materials
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                frequency INTEGER,
                FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
            )
        """)

        # Save changes and close connection
        conn.commit()
        conn.close()

    # ========== Save Operations ==========

    def save_material(self, filename, file_type, file_size):
        """
        Save basic information about an uploaded file.

        Args:
            filename (str): Name of the uploaded file
            file_type (str): Type/extension of the file (pdf, txt, docx, etc.)
            file_size (int): Size of the file in bytes

        Returns:
            int: The ID of the newly created material record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert new material record with current timestamp
        cursor.execute("""
            INSERT INTO materials (filename, file_type, file_size, upload_date)
            VALUES (?, ?, ?, ?)
        """, (filename, file_type, file_size, datetime.now()))

        # Get the ID of the newly inserted material
        material_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return material_id

    def save_flashcards(self, material_id, flashcards):
        """
        Save generated flashcards to the database.

        Args:
            material_id (int): ID of the material these flashcards belong to
            flashcards (list): List of flashcard dictionaries with question/answer pairs
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert each flashcard into the database
        for card in flashcards:
            cursor.execute("""
                INSERT INTO flashcards (material_id, question, answer, topic, difficulty, card_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                material_id,
                card['question'],
                card['answer'],
                card.get('topic', 'General'),        # Default topic if not specified
                card.get('difficulty', 'medium'),    # Default difficulty if not specified
                card.get('type', 'general')          # Default type if not specified
            ))

        conn.commit()
        conn.close()

    def save_summary(self, material_id, summary_data):
        """
        Save generated summary to the database.

        Args:
            material_id (int): ID of the material this summary belongs to
            summary_data (dict): Dictionary containing summary text, key points, etc.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert key points list to a string (using ||| as separator)
        key_points_str = '|||'.join(summary_data.get('key_points', []))

        cursor.execute("""
            INSERT INTO summaries (material_id, summary_text, key_points, compression_ratio)
            VALUES (?, ?, ?, ?)
        """, (
            material_id,
            summary_data['summary'],
            key_points_str,
            summary_data.get('compression_ratio', 0.0)
        ))

        conn.commit()
        conn.close()

    def save_topics(self, material_id, topics):
        """
        Save extracted topics to the database.

        Args:
            material_id (int): ID of the material these topics belong to
            topics (list): List of topic strings extracted from the material
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert each topic with frequency 1 (can be enhanced later)
        for topic in topics:
            cursor.execute("""
                INSERT INTO topics (material_id, topic_name, frequency)
                VALUES (?, ?, ?)
            """, (material_id, topic, 1))

        conn.commit()
        conn.close()

    # ========== Retrieve Operations ==========

    def get_all_materials(self):
        """
        Get all uploaded materials with their statistics.

        Returns:
            list: List of material dictionaries with flashcard and summary counts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()

        # Join materials with flashcards and summaries to get counts
        cursor.execute("""
            SELECT m.*, 
                   COUNT(DISTINCT f.id) as flashcard_count,
                   COUNT(DISTINCT s.id) as summary_count
            FROM materials m
            LEFT JOIN flashcards f ON m.id = f.material_id
            LEFT JOIN summaries s ON m.id = s.material_id
            GROUP BY m.id
            ORDER BY m.upload_date DESC
        """)

        # Convert rows to dictionaries
        materials = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return materials

    def get_material_by_id(self, material_id):
        """
        Get a specific material by its ID.

        Args:
            material_id (int): ID of the material to retrieve

        Returns:
            dict or None: Material information dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
        material = cursor.fetchone()

        conn.close()
        return dict(material) if material else None

    def get_flashcards_by_material(self, material_id):
        """
        Get all flashcards for a specific material.

        Args:
            material_id (int): ID of the material

        Returns:
            list: List of flashcard dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM flashcards WHERE material_id = ?", (material_id,))
        flashcards = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return flashcards

    def get_summary_by_material(self, material_id):
        """
        Get summary for a specific material.

        Args:
            material_id (int): ID of the material

        Returns:
            dict or None: Summary dictionary with key_points as a list, or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM summaries WHERE material_id = ?", (material_id,))
        summary = cursor.fetchone()

        conn.close()

        if summary:
            summary_dict = dict(summary)
            # Convert key points string back to list (split by |||)
            summary_dict['key_points'] = summary_dict['key_points'].split('|||')
            return summary_dict

        return None

    def get_topics_by_material(self, material_id):
        """
        Get all topics for a specific material.

        Args:
            material_id (int): ID of the material

        Returns:
            list: List of topic dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM topics WHERE material_id = ?", (material_id,))
        topics = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return topics

    # ========== Delete Operations ==========

    def delete_material(self, material_id):
        """
        Delete a material and all its related data.

        This will automatically delete all associated flashcards, summaries,
        and topics due to the CASCADE foreign key constraints.

        Args:
            material_id (int): ID of the material to delete
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete material (CASCADE will handle related data)
        cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))

        conn.commit()
        conn.close()

    # ========== Search Operations ==========

    def search_by_topic(self, topic_name):
        """
        Search for materials that contain a specific topic.

        Args:
            topic_name (str): Topic name to search for (partial matches allowed)

        Returns:
            list: List of material dictionaries that contain the topic
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Search for materials that have topics containing the search term
        cursor.execute("""
            SELECT DISTINCT m.*
            FROM materials m
            JOIN topics t ON m.id = t.material_id
            WHERE t.topic_name LIKE ?
        """, (f"%{topic_name}%",))

        materials = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return materials

    # ========== Additional Utility Methods ==========

    def get_database_stats(self):
        """
        Get overall statistics about the database.

        Returns:
            dict: Dictionary containing counts of materials, flashcards, summaries, and topics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count records in each table
        stats = {}

        cursor.execute("SELECT COUNT(*) FROM materials")
        stats['total_materials'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM flashcards")
        stats['total_flashcards'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM summaries")
        stats['total_summaries'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM topics")
        stats['total_topics'] = cursor.fetchone()[0]

        conn.close()
        return stats

    def get_recent_materials(self, limit=10):
        """
        Get the most recently uploaded materials.

        Args:
            limit (int): Maximum number of materials to return

        Returns:
            list: List of recent material dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM materials 
            ORDER BY upload_date DESC 
            LIMIT ?
        """, (limit,))

        materials = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return materials

    def cleanup_orphaned_data(self):
        """
        Clean up any orphaned data (flashcards, summaries, topics without materials).
        
        This is a maintenance function to ensure data integrity.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clean up orphaned flashcards
        cursor.execute("""
            DELETE FROM flashcards 
            WHERE material_id NOT IN (SELECT id FROM materials)
        """)

        # Clean up orphaned summaries
        cursor.execute("""
            DELETE FROM summaries 
            WHERE material_id NOT IN (SELECT id FROM materials)
        """)

        # Clean up orphaned topics
        cursor.execute("""
            DELETE FROM topics 
            WHERE material_id NOT IN (SELECT id FROM materials)
        """)

        conn.commit()
        conn.close()