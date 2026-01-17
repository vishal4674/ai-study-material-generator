# ========== Imports ==========
import PyPDF2
import docx
from pathlib import Path
import re

class FileParser:
    """
    Parse different file types (PDF, TXT, DOCX, Video) and extract text content.

    This class handles reading files, cleaning up the text, and returning it as a string.
    """

    def __init__(self):
        # List of supported file formats
        self.supported_formats = ['pdf', 'txt', 'docx', 'mp4', 'avi', 'mov', 'mkv', 'webm']

    def parse(self, file_path):
        """
        Parse file and extract text based on file type.

        Args:
            file_path (str or Path): Path to the file

        Returns:
            str: Extracted text content
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()[1:]  # Get extension without dot

        # Check file type and call the right method
        if extension == 'pdf':
            return self._parse_pdf(file_path)
        elif extension == 'txt':
            return self._parse_txt(file_path)
        elif extension == 'docx':
            return self._parse_docx(file_path)
        elif extension in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
            return self._parse_video(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def _parse_pdf(self, file_path):
        """
        Extract text from a PDF file and clean it.

        Args:
            file_path (Path): Path to the PDF file

        Returns:
            str: Cleaned text from the PDF
        """
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                # Loop through all pages and extract text
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    # Clean the text from each page
                    page_text = self._clean_pdf_text(page_text)
                    if page_text.strip():  # Only add non-empty pages
                        text += page_text + "\n\n"
                print(f" PDF extracted: {len(text)} characters from {len(pdf_reader.pages)} pages")
        except Exception as e:
            # If PyPDF2 fails, try pdfplumber as a backup
            try:
                import pdfplumber
                text = self._parse_pdf_with_pdfplumber(file_path)
            except ImportError:
                raise Exception(f"Error parsing PDF: {str(e)}. Install pdfplumber for better extraction.")

        # Final cleanup before returning
        return self._final_text_cleanup(text)

    def _clean_pdf_text(self, raw_text):
        """
        Clean raw text extracted from PDF.

        Args:
            raw_text (str): Raw text from PDF

        Returns:
            str: Cleaned text
        """
        if not raw_text:
            return ""

        # Remove unwanted characters and artifacts
        text = re.sub(r'[^\w\s\.\,\?\!\:\;\-\(\)\[\]\/]', ' ', raw_text)
        # Fix broken words (letters with spaces)
        text = re.sub(r'\b([a-z])\s+([a-z])\s+([a-z])', r'\1\2\3', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove single characters and numbers alone
        text = re.sub(r'\b[0-9]\b|\b[a-zA-Z]\b', '', text)

        # Remove lines with only symbols or short text
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Only keep lines with more than 3 words
            if len(line.split()) >= 3:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _parse_pdf_with_pdfplumber(self, file_path):
        """
        Alternative PDF parsing using pdfplumber.

        Args:
            file_path (Path): Path to the PDF file

        Returns:
            str: Extracted text
        """
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += self._clean_pdf_text(page_text) + "\n\n"
            return text
        except Exception as e:
            raise Exception(f"pdfplumber extraction failed: {str(e)}")

    def _final_text_cleanup(self, text):
        """
        Final cleanup of extracted text.

        Args:
            text (str): Text to clean

        Returns:
            str: Cleaned text ready for processing
        """
        if not text:
            return "Unable to extract meaningful text from this PDF."

        # Remove very short lines
        lines = text.split('\n')
        meaningful_lines = []
        for line in lines:
            line = line.strip()
            # Keep lines with at least 5 characters and 2 words
            if len(line) >= 5 and len(line.split()) >= 2:
                meaningful_lines.append(line)

        cleaned_text = '\n'.join(meaningful_lines)
        # Limit consecutive newlines and spaces
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)  # Max 2 newlines
        cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)     # Single spaces

        return cleaned_text.strip()

    def _parse_txt(self, file_path):
        """
        Extract text from a TXT file.

        Args:
            file_path (Path): Path to the TXT file

        Returns:
            str: Text content from the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            # Try with different encoding if utf-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                text = file.read()
        return text.strip()

    def _parse_docx(self, file_path):
        """
        Extract text from a DOCX file.

        Args:
            file_path (Path): Path to the DOCX file

        Returns:
            str: Text content from the file
        """
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
        return text.strip()

    def _parse_video(self, file_path):
        """
        Extract text (transcript) from a video file.

        Args:
            file_path (Path): Path to the video file

        Returns:
            str: Transcript text from the video
        """
        try:
            # Import video processor only when needed
            from src.core.video_processor import VideoProcessor

            processor = VideoProcessor()
            transcript = processor.extract_text_from_video(file_path)

            # Save transcript to file for later use
            from src.utils.config import Config
            transcript_path = Config.TRANSCRIPTS_FOLDER / f"{file_path.stem}_transcript.json"
            processor.save_transcript(transcript, transcript_path)

            return transcript['full_text']

        except Exception as e:
            raise Exception(f"Error parsing video: {str(e)}")

    def get_file_info(self, file_path):
        """
        Get basic information about a file.

        Args:
            file_path (str or Path): Path to the file

        Returns:
            dict: File info (name, size, extension, modified time)
        """
        file_path = Path(file_path)
        return {
            'name': file_path.name,
            'size': file_path.stat().st_size,
            'extension': file_path.suffix[1:],
            'modified': file_path.stat().st_mtime
        }