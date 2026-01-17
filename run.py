import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.app import create_app

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print(" AI STUDY MATERIAL GENERATOR")
    print("="*60)
    print("✨ Application Started Successfully!")
    print("="*60)
    print(" URLs:")
    print("   • Home Page:      http://localhost:5000")
    print("   • Dashboard:      http://localhost:5000/dashboard")
    print("   • API Stats:      http://localhost:5000/api/stats")
    print("="*60)
    print(" Folders Initialized:")
    print("   • Uploads:        uploads/")
    print("   • Outputs:        outputs/")
    print("   • Database:       data/study_materials.db")
    print("="*60)
    print(" Features Available:")
    print("   ✓ PDF, TXT, DOCX Support")
    print("   ✓ Flashcard Generation")
    print("   ✓ Smart Summaries")
    print("   ✓ Concept Mapping")
    print("   ✓ Learning Paths")
    print("="*60)
    print("Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print(" Server stopped. Thank you for using!")
        print("="*60 + "\n")