# ========== Imports ==========
import json
import csv
from pathlib import Path
from datetime import datetime

class FileManager:
    """
    Manage file operations for saving and loading output files.

    This class handles saving generated study materials to different file formats:
    - Flashcards (JSON and CSV)
    - Summaries (JSON)
    - Concept maps (JSON)
    - Learning paths (JSON)
    """

    def __init__(self, output_folder):
        """
        Initialize the FileManager with output folder structure.

        Args:
            output_folder (str or Path): Main folder where all outputs will be saved
        """
        self.output_folder = Path(output_folder)
        
        # Create subfolders for different types of outputs
        self.flashcards_folder = self.output_folder / 'flashcards'
        self.summaries_folder = self.output_folder / 'summaries'
        self.concept_maps_folder = self.output_folder / 'concept_maps'
        self.learning_paths_folder = self.output_folder / 'learning_paths'
        
        # Create all folders if they don't exist
        self._create_folders()

    # ========== Folder Management ==========

    def _create_folders(self):
        """
        Create all necessary output folders if they don't exist.

        Makes sure we have folders for flashcards, summaries, concept maps,
        and learning paths before we try to save files.
        """
        folders = [
            self.flashcards_folder,
            self.summaries_folder,
            self.concept_maps_folder,
            self.learning_paths_folder
        ]

        for folder in folders:
            # Create folder and any parent folders if needed
            folder.mkdir(parents=True, exist_ok=True)

    # ========== Flashcard Saving Methods ==========

    def save_flashcards_json(self, flashcards, filename):
        """
        Save flashcards as a JSON file with metadata.

        Creates a structured JSON file containing all flashcard data
        plus generation timestamp and statistics.

        Args:
            flashcards (list): List of flashcard dictionaries
            filename (str): Name for the output file (without extension)

        Returns:
            str: Full path to the saved file
        """
        filepath = self.flashcards_folder / f"{filename}.json"

        # Create structured data with metadata
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_cards': len(flashcards),
            'flashcards': flashcards
        }

        # Save as formatted JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def save_flashcards_csv(self, flashcards, filename):
        """
        Save flashcards as a CSV file for easy import into other tools.

        Creates a spreadsheet-compatible CSV with columns for each flashcard field.
        Great for importing into Anki, Quizlet, or Excel.

        Args:
            flashcards (list): List of flashcard dictionaries
            filename (str): Name for the output file (without extension)

        Returns:
            str: Full path to the saved file
        """
        filepath = self.flashcards_folder / f"{filename}.csv"

        # Define the columns we want in the CSV
        fieldnames = ['id', 'question', 'answer', 'topic', 'difficulty', 'type']

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write column headers
            writer.writeheader()

            # Write each flashcard as a row
            for card in flashcards:
                # Create row with all required fields (empty string if missing)
                row = {key: card.get(key, '') for key in fieldnames}
                writer.writerow(row)

        return str(filepath)

    # ========== Summary Saving Methods ==========

    def save_summary_json(self, summary_data, filename):
        """
        Save summary data as a structured JSON file.

        Includes the summary text, key points, and statistics about
        the original text length and compression ratio.

        Args:
            summary_data (dict): Dictionary containing summary and statistics
            filename (str): Name for the output file (without extension)

        Returns:
            str: Full path to the saved file
        """
        filepath = self.summaries_folder / f"{filename}.json"

        # Structure the summary data with metadata
        data = {
            'generated_at': datetime.now().isoformat(),
            'summary': summary_data['summary'],
            'key_points': summary_data['key_points'],
            'statistics': {
                'original_length': summary_data.get('original_length', 0),
                'summary_length': summary_data.get('summary_length', 0),
                'compression_ratio': summary_data.get('compression_ratio', 0.0)
            }
        }

        # Save as formatted JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    # ========== Concept Map Saving Methods ==========

    def save_concept_map_json(self, concept_map, filename):
        """
        Save concept map data as JSON for visualization tools.

        Stores the graph structure with nodes and edges that can be
        loaded by D3.js or other visualization libraries.

        Args:
            concept_map (dict): Graph structure with nodes and edges
            filename (str): Name for the output file (without extension)

        Returns:
            str: Full path to the saved file
        """
        filepath = self.concept_maps_folder / f"{filename}.json"

        # Wrap concept map data with metadata
        data = {
            'generated_at': datetime.now().isoformat(),
            'graph': concept_map
        }

        # Save as formatted JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    # ========== Learning Path Saving Methods ==========

    def save_learning_path_json(self, learning_path, filename):
        """
        Save learning path data as JSON for study planning.

        Stores the structured learning plan with steps, time estimates,
        and difficulty progression.

        Args:
            learning_path (dict): Learning path with steps and metadata
            filename (str): Name for the output file (without extension)

        Returns:
            str: Full path to the saved file
        """
        filepath = self.learning_paths_folder / f"{filename}.json"

        # Wrap learning path data with metadata
        data = {
            'generated_at': datetime.now().isoformat(),
            'learning_path': learning_path
        }

        # Save as formatted JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    # ========== File Loading Methods ==========

    def load_json(self, filepath):
        """
        Load and parse a JSON file.

        Reads a JSON file and returns the parsed data as a Python object.

        Args:
            filepath (str or Path): Path to the JSON file to load

        Returns:
            dict or list: Parsed JSON data
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ========== File Management Utilities ==========

    def get_file_list(self, folder_type='flashcards'):
        """
        Get list of saved files in a specific output folder.

        Useful for showing users what files have been generated
        or for loading previously saved data.

        Args:
            folder_type (str): Type of folder to check
                              ('flashcards', 'summaries', 'concept_maps', 'learning_paths')

        Returns:
            list: List of filenames in the specified folder
        """
        # Map folder types to actual folder paths
        folder_map = {
            'flashcards': self.flashcards_folder,
            'summaries': self.summaries_folder,
            'concept_maps': self.concept_maps_folder,
            'learning_paths': self.learning_paths_folder
        }

        # Get the requested folder (default to flashcards)
        folder = folder_map.get(folder_type, self.flashcards_folder)
        
        # Find all JSON files in the folder
        files = list(folder.glob('*.json'))

        # Return just the filenames (not full paths)
        return [f.name for f in files]

    # ========== Additional Utility Methods ==========

    def get_folder_stats(self):
        """
        Get statistics about saved files in all folders.

        Returns:
            dict: Count of files in each folder type
        """
        stats = {}
        
        folder_types = ['flashcards', 'summaries', 'concept_maps', 'learning_paths']
        
        for folder_type in folder_types:
            file_count = len(self.get_file_list(folder_type))
            stats[folder_type] = file_count
        
        return stats

    def cleanup_old_files(self, days_old=30):
        """
        Clean up files older than specified number of days.

        Args:
            days_old (int): Files older than this many days will be deleted
        """
        from datetime import timedelta
        import time
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        # Check all output folders
        for folder in [self.flashcards_folder, self.summaries_folder, 
                      self.concept_maps_folder, self.learning_paths_folder]:
            
            for file_path in folder.glob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()  # Delete the file
                    deleted_count += 1
        
        return deleted_count

    def export_all_data(self, export_path):
        """
        Export all saved data to a single backup file.

        Args:
            export_path (str or Path): Where to save the backup file

        Returns:
            str: Path to the created backup file
        """
        export_path = Path(export_path)
        
        # Collect all data from all folders
        all_data = {
            'export_date': datetime.now().isoformat(),
            'flashcards': [],
            'summaries': [],
            'concept_maps': [],
            'learning_paths': []
        }
        
        # Load all files from each folder
        for folder_type in ['flashcards', 'summaries', 'concept_maps', 'learning_paths']:
            files = self.get_file_list(folder_type)
            folder_path = getattr(self, f"{folder_type}_folder")
            
            for filename in files:
                file_path = folder_path / filename
                try:
                    data = self.load_json(file_path)
                    all_data[folder_type].append({
                        'filename': filename,
                        'data': data
                    })
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        
        # Save backup file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        return str(export_path)