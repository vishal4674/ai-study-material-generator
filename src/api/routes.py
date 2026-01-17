# ========== Imports ==========
from flask import render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
from pathlib import Path

from src.utils.config import Config
from src.utils.helpers import Helpers
from src.core.file_parser import FileParser
from src.core.text_processor import TextProcessor
from src.core.flashcard_generator import FlashcardGenerator
from src.core.summary_generator import SummaryGenerator
from src.core.concept_mapper import ConceptMapper
from src.core.learning_path import LearningPathGenerator
from src.storage.file_manager import FileManager

# ========== Route Registration ==========

def register_routes(app):
    """
    Register all Flask routes for the application.

    This function sets up all the web pages and API endpoints
    that the app will respond to.
    """
    # Get database and file manager ready
    db = app.config['DATABASE']
    file_manager = FileManager(Config.OUTPUT_FOLDER)

    @app.route('/')
    def index():
        """Show the home page with file upload form."""
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        """Show dashboard with all uploaded study materials."""
        materials = db.get_all_materials()
        return render_template('dashboard.html', materials=materials)

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """
        Handle file upload and process the file.

        Steps:
        - Check if a file is uploaded
        - Validate file type
        - Save the file to uploads folder
        - Save file info to database
        - Process the file to generate study materials
        """
        try:
            # Check if file is present in the request
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400

            file = request.files['file']

            # Check if filename is not empty
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Check if file type is allowed
            if not Helpers.allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
                return jsonify({'error': 'Invalid file type. Allowed: PDF, TXT, DOCX'}), 400

            # Save the file with a unique name
            filename = Helpers.secure_filename_with_timestamp(file.filename)
            filepath = Config.UPLOAD_FOLDER / filename
            file.save(str(filepath))

            # Get file size and type
            file_size = filepath.stat().st_size
            file_type = Helpers.get_file_extension(filename)

            # Save file info to database
            material_id = db.save_material(filename, file_type, file_size)

            # Process the uploaded file to generate study materials
            process_result = process_uploaded_file(filepath, material_id, db, file_manager)

            # Return success response with stats
            return jsonify({
                'success': True,
                'material_id': material_id,
                'filename': filename,
                'message': 'File processed successfully',
                'stats': process_result
            })

        except Exception as e:
            # If any error occurs, return error message
            return jsonify({'error': str(e)}), 500

    @app.route('/material/<int:material_id>')
    def view_material(material_id):
        """
        Show details for a specific material.

        Displays flashcards, summary, and topics for the selected file.
        """
        material = db.get_material_by_id(material_id)

        if not material:
            return "Material not found", 404

        flashcards = db.get_flashcards_by_material(material_id)
        summary = db.get_summary_by_material(material_id)
        topics = db.get_topics_by_material(material_id)

        return render_template('material_detail.html',
                             material=material,
                             flashcards=flashcards,
                             summary=summary,
                             topics=topics)

    @app.route('/flashcards/<int:material_id>')
    def view_flashcards(material_id):
        """
        Show flashcards for a specific material.
        """
        material = db.get_material_by_id(material_id)
        flashcards = db.get_flashcards_by_material(material_id)

        return render_template('flashcards.html',
                             material=material,
                             flashcards=flashcards)

    @app.route('/summary/<int:material_id>')
    def view_summary(material_id):
        """
        Show summary for a specific material.
        """
        material = db.get_material_by_id(material_id)
        summary = db.get_summary_by_material(material_id)

        return render_template('summary.html',
                             material=material,
                             summary=summary)

    @app.route('/concept-map/<int:material_id>')
    def view_concept_map(material_id):
        """
        Show concept map for a specific material.

        Loads the concept map graph from file if available.
        """
        material = db.get_material_by_id(material_id)
        topics = db.get_topics_by_material(material_id)

        # Try to load concept graph from file
        concept_graph = None
        graph_file = Config.CONCEPT_MAPS_FOLDER / f"{material['filename']}_concept_map.json"
        if graph_file.exists():
            concept_graph = file_manager.load_json(graph_file)

        return render_template('concept_map.html',
                             material=material,
                             concept_graph=concept_graph,
                             topics=topics)

    @app.route('/download/<file_type>/<int:material_id>')
    def download_file(file_type, material_id):
        """
        Download generated files (flashcards, summary, concept map, etc.)
        """
        material = db.get_material_by_id(material_id)

        if not material:
            return "Material not found", 404

        filename = material['filename']
        file_map = {
            'flashcards_json': Config.FLASHCARDS_FOLDER / f"{filename}.json",
            'flashcards_csv': Config.FLASHCARDS_FOLDER / f"{filename}.csv",
            'summary': Config.SUMMARIES_FOLDER / f"{filename}.json",
            'concept_map': Config.CONCEPT_MAPS_FOLDER / f"{filename}_concept_map.json",
            'learning_path': Config.LEARNING_PATHS_FOLDER / f"{filename}_learning_path.json"
        }

        filepath = file_map.get(file_type)

        if filepath and filepath.exists():
            return send_file(str(filepath), as_attachment=True)

        return "File not found", 404

    @app.route('/delete/<int:material_id>', methods=['POST'])
    def delete_material(material_id):
        """
        Delete a material and all its related data.
        """
        try:
            db.delete_material(material_id)
            return jsonify({'success': True, 'message': 'Material deleted'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/search')
    def search():
        """
        Search materials by topic name.
        """
        query = request.args.get('q', '')

        if query:
            materials = db.search_by_topic(query)
        else:
            materials = db.get_all_materials()

        return render_template('dashboard.html', materials=materials, query=query)

    # ========== Stats Routes ==========

    @app.route('/stats')
    def stats_page():
        """Show statistics dashboard page."""
        return render_template('stats.html')

    @app.route('/api/stats')
    def get_stats():
        """
        API endpoint to get overall statistics.
        Returns total materials, flashcards, and summaries.
        """
        materials = db.get_all_materials()

        total_flashcards = sum(m['flashcard_count'] for m in materials)
        total_summaries = sum(m['summary_count'] for m in materials)

        return jsonify({
            'total_materials': len(materials),
            'total_flashcards': total_flashcards,
            'total_summaries': total_summaries
        })

    @app.route('/api/materials')
    def get_materials_api():
        """
        API endpoint to get all materials as JSON.
        """
        materials = db.get_all_materials()
        return jsonify(materials)

# ========== File Processing Logic ==========

def process_uploaded_file(filepath, material_id, db, file_manager):
    """
    Process the uploaded file and generate all study materials.

    Steps:
    - Parse the file and extract text
    - Extract topics from the text
    - Generate flashcards and save them
    - Generate summary and save it
    - Generate concept map and save it
    - Generate learning path and save it

    Returns:
        dict: Statistics about the generated materials
    """
    # Initialize all processors
    parser = FileParser()
    text_processor = TextProcessor()
    flashcard_gen = FlashcardGenerator()
    summary_gen = SummaryGenerator()
    concept_mapper = ConceptMapper()
    learning_path_gen = LearningPathGenerator()

    # Parse file to get text
    text = parser.parse(filepath)

    # Extract topics from text
    topics = text_processor.extract_topics(text)
    db.save_topics(material_id, topics)

    # Generate flashcards
    flashcards = flashcard_gen.generate(text, topics, num_cards=25)
    db.save_flashcards(material_id, flashcards)

    # Save flashcards to JSON and CSV files
    filename = filepath.stem
    file_manager.save_flashcards_json(flashcards, filename)
    file_manager.save_flashcards_csv(flashcards, filename)

    # Generate summary and save
    summary = summary_gen.generate(text, ratio=0.3)
    db.save_summary(material_id, summary)
    file_manager.save_summary_json(summary, filename)

    # Generate concept map and save
    concept_graph = concept_mapper.create_concept_graph(topics, text)
    file_manager.save_concept_map_json(concept_graph, f"{filename}_concept_map")

    # Generate learning path and save
    learning_path = learning_path_gen.generate(topics, flashcards)
    file_manager.save_learning_path_json(learning_path, f"{filename}_learning_path")

    # Return stats for UI
    return {
        'flashcards': len(flashcards),
        'topics': len(topics),
        'summary_length': len(summary['summary'].split()),
        'concept_nodes': len(concept_graph['nodes'])
    }