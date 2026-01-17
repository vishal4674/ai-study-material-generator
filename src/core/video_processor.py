# ========== Imports ==========
import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path
import json
from datetime import timedelta

class VideoProcessor:
    """
    Extract text from video files using speech recognition.

    This class takes video files and converts the speech/audio content
    into written text that can be used to generate study materials.

    Process:
    - Extract audio from video file
    - Split audio into chunks for better recognition
    - Use Google Speech Recognition to convert speech to text
    - Return structured transcript with timestamps
    """

    def __init__(self):
        # Initialize speech recognizer from Google
        self.recognizer = sr.Recognizer()
        # List of video formats we can process
        self.supported_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm']

    # ========== Main Video Processing Method ==========

    def extract_text_from_video(self, video_path):
        """
        Extract text from video using audio transcription.

        This is the main function that handles the complete process of
        converting a video file into readable text.

        Args:
            video_path (str or Path): Path to the video file

        Returns:
            dict: Complete transcript with text, timestamps, and metadata
        """
        video_path = Path(video_path)

        print(f" Processing video: {video_path.name}")

        # Step 1: Extract audio from the video file
        audio_path = self._extract_audio(video_path)

        # Step 2: Convert the audio to text using speech recognition
        transcript = self._transcribe_audio(audio_path)

        # Step 3: Clean up the temporary audio file we created
        if audio_path.exists():
            audio_path.unlink()

        return transcript

    # ========== Audio Extraction ==========

    def _extract_audio(self, video_path):
        """
        Extract audio track from video file.

        Uses moviepy to separate the audio from video and save it as a WAV file
        that can be processed by speech recognition.

        Args:
            video_path (Path): Path to the video file

        Returns:
            Path: Path to the extracted audio file
        """
        try:
            print(" Extracting audio from video...")

            # Load the video file using moviepy
            video = VideoFileClip(str(video_path))

            # Create path for the audio file (same name as video but .wav)
            audio_path = video_path.parent / f"{video_path.stem}_audio.wav"

            # Extract audio and save as WAV file
            # logger=None prevents moviepy from showing progress messages
            video.audio.write_audiofile(str(audio_path), logger=None)

            # Close video file to free up memory
            video.close()

            print(f" Audio extracted: {audio_path.name}")
            return audio_path

        except Exception as e:
            raise Exception(f"Error extracting audio: {str(e)}")

    # ========== Speech Recognition ==========

    def _transcribe_audio(self, audio_path):
        """
        Transcribe audio to text using speech recognition.

        Breaks the audio into smaller chunks and uses Google's speech recognition
        service to convert each chunk into text.

        Args:
            audio_path (Path): Path to the audio file

        Returns:
            dict: Complete transcript with text, timestamps, and statistics
        """
        try:
            print(" Starting speech recognition...")

            # Load the audio file using pydub
            audio = AudioSegment.from_wav(str(audio_path))

            # Split audio into chunks based on silence
            # This helps improve recognition accuracy
            chunks = split_on_silence(
                audio,
                min_silence_len=500,      # Minimum silence length (ms)
                silence_thresh=audio.dBFS - 14,  # Silence threshold
                keep_silence=250         # Keep some silence at chunk edges
            )

            # If no chunks found, use the whole audio as one chunk
            if not chunks:
                chunks = [audio]

            print(f" Split audio into {len(chunks)} chunks")

            # Process each chunk and collect results
            full_text = []
            timestamps = []
            current_time = 0

            # Limit to 20 chunks to prevent very long processing times
            for i, chunk in enumerate(chunks[:20]):
                try:
                    # Create temporary file for this audio chunk
                    chunk_path = audio_path.parent / f"chunk_{i}.wav"
                    chunk.export(str(chunk_path), format="wav")

                    # Use speech recognition on this chunk
                    with sr.AudioFile(str(chunk_path)) as source:
                        # Load the audio data
                        audio_data = self.recognizer.record(source)
                        # Convert speech to text using Google's API
                        text = self.recognizer.recognize_google(audio_data)

                        if text:  # If we got some text from this chunk
                            full_text.append(text)
                            timestamps.append({
                                'start': str(timedelta(milliseconds=current_time)),
                                'end': str(timedelta(milliseconds=current_time + len(chunk))),
                                'text': text
                            })

                    # Delete the temporary chunk file
                    chunk_path.unlink()

                    # Update current time position
                    current_time += len(chunk)

                    print(f" Chunk {i+1}/{min(len(chunks), 20)} transcribed")

                except sr.UnknownValueError:
                    # Speech recognition couldn't understand this chunk
                    print(f"⚠ Could not understand chunk {i+1}")
                except sr.RequestError as e:
                    # API error (network issues, quota exceeded, etc.)
                    print(f"⚠ API error on chunk {i+1}: {e}")
                except Exception as e:
                    # Any other error processing this chunk
                    print(f"⚠ Error processing chunk {i+1}: {e}")

            # Combine all transcribed text into one string
            combined_text = " ".join(full_text)

            print(f" Transcription complete: {len(combined_text.split())} words")

            # Return structured transcript data
            return {
                'full_text': combined_text,
                'timestamps': timestamps,
                'word_count': len(combined_text.split()),
                'duration': str(timedelta(milliseconds=current_time))
            }

        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")

    # ========== File Saving ==========

    def save_transcript(self, transcript, output_path):
        """
        Save transcript to JSON file for later use.

        Saves the complete transcript data including timestamps and metadata
        in a structured JSON format.

        Args:
            transcript (dict): Transcript data from transcription
            output_path (str or Path): Where to save the transcript file
        """
        output_path = Path(output_path)

        # Make sure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save transcript as formatted JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)

        print(f" Transcript saved: {output_path.name}")

    # ========== Utility Methods ==========

    def get_video_info(self, video_path):
        """
        Get basic information about a video file.

        Args:
            video_path (str or Path): Path to video file

        Returns:
            dict: Video information (duration, size, etc.)
        """
        try:
            video_path = Path(video_path)
            video = VideoFileClip(str(video_path))

            info = {
                'filename': video_path.name,
                'duration': str(timedelta(seconds=int(video.duration))),
                'fps': video.fps,
                'resolution': f"{video.w}x{video.h}",
                'file_size': video_path.stat().st_size
            }

            video.close()
            return info

        except Exception as e:
            return {'error': f"Could not read video info: {str(e)}"}

    def is_supported_format(self, filename):
        """
        Check if video file format is supported.

        Args:
            filename (str): Name of the video file

        Returns:
            bool: True if format is supported, False otherwise
        """
        if '.' not in filename:
            return False

        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.supported_formats