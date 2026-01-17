from nltk.tokenize import sent_tokenize
from collections import Counter
import re

class SummaryGenerator:
    """Generate summaries from text content"""
    
    def __init__(self):
        pass
    
    def generate(self, text, ratio=0.3):
        """
        Generate summary using extractive summarization
        
        Args:
            text (str): Source text
            ratio (float): Ratio of sentences to keep (0.0 to 1.0)
            
        Returns:
            dict: Summary with full text and key points
        """
        sentences = sent_tokenize(text)
        
        # Score sentences
        sentence_scores = self._score_sentences(sentences, text)
        
        # Select top sentences
        num_sentences = max(3, int(len(sentences) * ratio))
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
        
        # Sort by original order
        summary_sentences = sorted(top_sentences, key=lambda x: sentences.index(x[0]))
        summary_text = " ".join([s[0] for s in summary_sentences])
        
        # Extract key points
        key_points = self._extract_key_points(text, sentences)
        
        return {
            'summary': summary_text,
            'key_points': key_points,
            'original_length': len(text.split()),
            'summary_length': len(summary_text.split()),
            'compression_ratio': len(summary_text.split()) / len(text.split())
        }
    
    def _score_sentences(self, sentences, full_text):
        """Score sentences based on word frequency"""
        # Get word frequency
        words = re.findall(r'\b[a-zA-Z]{3,}\b', full_text.lower())
        word_freq = Counter(words)
        
        # Score each sentence
        sentence_scores = {}
        for sentence in sentences:
            sentence_words = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
            score = sum([word_freq.get(word, 0) for word in sentence_words])
            sentence_scores[sentence] = score / (len(sentence_words) + 1)
        
        return sentence_scores
    
    def _extract_key_points(self, text, sentences):
        """Extract key points (bullet points)"""
        key_points = []
        
        # Look for sentences with important keywords
        important_keywords = ['important', 'key', 'main', 'primary', 'essential', 'critical', 
                             'significant', 'fundamental', 'core', 'major']
        
        for sentence in sentences[:30]:  # Check first 30 sentences
            if any(keyword in sentence.lower() for keyword in important_keywords):
                key_points.append(sentence.strip())
            
            if len(key_points) >= 5:
                break
        
        # If not enough points found, take first few sentences
        if len(key_points) < 3:
            key_points = sentences[:5]
        
        return key_points[:5]
    
    def generate_chapter_summaries(self, text):
        """Generate summaries for different chapters/sections"""
        # Simple chapter detection based on headings or paragraph breaks
        chapters = self._split_into_chapters(text)
        
        summaries = []
        for i, chapter in enumerate(chapters):
            summary = self.generate(chapter, ratio=0.3)
            summaries.append({
                'chapter_number': i + 1,
                'summary': summary['summary'],
                'key_points': summary['key_points']
            })
        
        return summaries
    
    def _split_into_chapters(self, text):
        """Split text into chapters (simple version)"""
        # Split by double newlines or section markers
        chapters = re.split(r'\n\n+', text)
        
        # Filter out very short sections
        chapters = [ch for ch in chapters if len(ch.split()) > 50]
        
        # If no clear chapters, split into equal parts
        if len(chapters) < 2:
            words = text.split()
            chunk_size = len(words) // 3
            chapters = [
                " ".join(words[i:i+chunk_size]) 
                for i in range(0, len(words), chunk_size)
            ]
        
        return chapters[:5]  # Max 5 chapters