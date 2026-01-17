# ========== Imports ==========
import nltk
from collections import Counter
import re
import string

class TextProcessor:
    """
    Process text and extract key topics/concepts dynamically from any content.

    This class analyzes text and finds important topics without needing
    predefined lists. It uses multiple smart methods to identify what's
    important in the text and creates a ranked list of topics.
    """
    
    def __init__(self):
        """
        Initialize the TextProcessor with NLTK tools and stopwords.
        
        Downloads required NLTK data if not already present and sets up
        a comprehensive list of stopwords to filter out common words.
        """
        # Download NLTK data if needed
        try:
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize, sent_tokenize
            self.stopwords = set(stopwords.words('english'))
        except:
            print("Downloading NLTK data...")
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            from nltk.corpus import stopwords
            self.stopwords = set(stopwords.words('english'))
        
        # Enhanced stopwords - add common junk words that aren't meaningful as topics
        self.stopwords.update([
            'it', 'they', 'we', 'that', 'this', 'these', 'those',
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'may',
            'might', 'must', 'can', 'time', 'need', 'make',
            'use', 'used', 'using', 'also', 'one', 'two', 'three',
            'first', 'second', 'third', 'many', 'some', 'more',
            'most', 'other', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just',
            'but', 'what', 'which', 'who', 'when', 'where', 'why',
            'how', 'all', 'each', 'every', 'both', 'few', 'way',
            'work', 'part', 'take', 'get', 'give', 'made', 'find',
            'tell', 'ask', 'show', 'try', 'leave', 'call', 'back',
            'keep', 'let', 'put', 'said', 'know', 'come', 'look',
            'want', 'seem', 'feel', 'new', 'right', 'good', 'old',
            'great', 'little', 'own', 'other', 'last', 'long',
            'small', 'large', 'next', 'early', 'young', 'important',
            'few', 'public', 'bad', 'same', 'able', 'page', 'pages',
            'version', 'number', 'numbers', 'chapter', 'section',
            'figure', 'table', 'see', 'show', 'example', 'examples'
        ])
        
        # Add single letters, numbers, and symbols to stopwords
        self.stopwords.update(string.ascii_lowercase)
        self.stopwords.update([str(i) for i in range(100)])
        self.stopwords.update(['=', '-', '_', '+', '*', '/', '\\', '|', '&', '%', '$', '#', '@', '!', '?'])

    # ========== Main Topic Extraction Method ==========

    def extract_topics(self, text):
        """
        Extract topics dynamically from text content using multiple methods.

        This is the main function that combines 5 different techniques to find
        important topics in any text without needing predefined topic lists.

        Args:
            text (str): The text content to analyze

        Returns:
            list: List of up to 15 most important topics found in the text
        """
        print(f" Processing text: {len(text)} characters")
        
        # Handle very short text
        if len(text) < 50:
            return ["General Topic"]
        
        # Use 5 different extraction methods (NO HARDCODING)
        topics = []
        
        # Method 1: Extract from actual text structure (headers, lists)
        structure_topics = self._extract_from_text_structure(text)
        topics.extend(structure_topics)
        
        # Method 2: Extract high-frequency meaningful terms
        frequency_topics = self._extract_high_frequency_terms(text)
        topics.extend(frequency_topics)
        
        # Method 3: Extract capitalized noun sequences (proper nouns)
        noun_topics = self._extract_capitalized_nouns(text)
        topics.extend(noun_topics)
        
        # Method 4: Extract context-based important terms (definition patterns)
        context_topics = self._extract_context_based_terms(text)
        topics.extend(context_topics)
        
        # Method 5: Extract semantic clusters (words that appear together)
        cluster_topics = self._extract_semantic_clusters(text)
        topics.extend(cluster_topics)
        
        # Clean up, remove duplicates, and rank by importance
        clean_topics = self._clean_and_filter_topics(topics)
        ranked_topics = self._rank_by_importance(clean_topics, text)
        
        print(f" Extracted {len(ranked_topics)} dynamic topics")
        return ranked_topics[:15]  # Return top 15 topics

    # ========== Topic Extraction Methods ==========

    def _extract_from_text_structure(self, text):
        """
        Extract topics from text structure like headers, lists, and emphasis.

        Looks for patterns that typically indicate important topics:
        - Lines that start with capital letters (headers)
        - Numbered sections
        - ALL CAPS text
        - Bullet points and lists

        Args:
            text (str): Input text to analyze

        Returns:
            list: Topics found in text structure
        """
        topics = []
        
        # Pattern 1: Different header formats
        header_patterns = [
            r'^([A-Z][A-Za-z\s]{3,40}):?\s*$',  # Line starting with capital letter
            r'^\d+\.?\s+([A-Z][A-Za-z\s]{3,40})',  # Numbered sections like "1. Introduction"
            r'^([A-Z\s]{4,30})$',  # ALL CAPS headers
            r'^\s*[-=]{3,}\s*([A-Za-z\s]{3,40})\s*[-=]{3,}',  # Decorated headers with lines
        ]
        
        # Check each line for header patterns
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            for pattern in header_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if self._is_meaningful_topic(match):
                            topics.append(match.strip())
        
        # Pattern 2: Bullet points and numbered lists
        list_patterns = [
            r'[-*•]\s+([A-Z][A-Za-z\s]{5,40})',  # Bullet points with dashes, stars, bullets
            r'\d+\)\s+([A-Z][A-Za-z\s]{5,40})',  # Numbered lists like "1) Something"
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                if self._is_meaningful_topic(match):
                    topics.append(match.strip())
        
        return topics[:20]  # Return maximum 20 structure-based topics

    def _extract_high_frequency_terms(self, text):
        """
        Extract high-frequency meaningful terms that appear multiple times.

        Finds words that appear frequently in the text and are likely to be
        important topics. Filters out common words and junk.

        Args:
            text (str): Input text to analyze

        Returns:
            list: High-frequency meaningful terms
        """
        # Break text into individual words (3+ characters only)
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        
        # Count how often each word appears
        word_freq = Counter(words)
        
        # Filter for meaningful terms only
        meaningful_terms = []
        for word, freq in word_freq.most_common(100):
            if (freq >= 3 and  # Must appear at least 3 times
                len(word) > 4 and  # Must be at least 5 characters long
                word not in self.stopwords and  # Can't be a common stopword
                not word.isdigit() and  # Can't be just a number
                self._has_meaning_indicators(word, text)):  # Must have semantic meaning
                
                meaningful_terms.append(word.title())  # Convert to title case
        
        return meaningful_terms[:15]  # Return top 15 frequent terms

    def _extract_capitalized_nouns(self, text):
        """
        Extract capitalized noun sequences using natural language processing.

        Finds proper nouns (names, places, concepts) that are capitalized
        in the text, which often represent important topics.

        Args:
            text (str): Input text to analyze

        Returns:
            list: Capitalized noun phrases found in text
        """
        try:
            from nltk import pos_tag, word_tokenize
            
            # Process first 30 sentences (for performance)
            sentences = re.split(r'[.!?]+', text)[:30]
            capitalized_terms = []
            
            for sentence in sentences:
                if len(sentence.strip()) < 10:
                    continue
                
                # Break sentence into words and tag parts of speech
                words = word_tokenize(sentence)
                tagged = pos_tag(words)
                
                # Find sequences of capitalized nouns
                current_sequence = []
                for word, tag in tagged:
                    if (tag in ['NN', 'NNS', 'NNP', 'NNPS'] and  # Noun part-of-speech tags
                        word[0].isupper() and  # First letter is capitalized
                        len(word) > 2 and  # Meaningful length
                        word.lower() not in self.stopwords):  # Not a stopword
                        
                        current_sequence.append(word)
                    else:
                        # End of noun sequence - save it if meaningful
                        if len(current_sequence) >= 1:
                            phrase = ' '.join(current_sequence)
                            if self._is_meaningful_topic(phrase):
                                capitalized_terms.append(phrase)
                        current_sequence = []
            
            # Count frequency and return common capitalized terms
            term_freq = Counter(capitalized_terms)
            return [term for term, count in term_freq.most_common(20) if count >= 2]
            
        except Exception as e:
            print(f" NLP processing skipped: {e}")
            return []

    def _extract_context_based_terms(self, text):
        """
        Extract terms based on context indicators that suggest importance.

        Looks for phrases that appear in contexts that typically introduce
        important concepts (like definitions, explanations, etc.).

        Args:
            text (str): Input text to analyze

        Returns:
            list: Terms found in important contexts
        """
        context_terms = []
        
        # Context patterns that indicate important concepts (NOT hardcoded topics!)
        context_indicators = [
            r'(?:concept of|definition of|meaning of|understanding)\s+([A-Za-z\s]{3,30})',
            r'([A-Z][A-Za-z\s]{3,30})\s+(?:is|are|means|refers to)',
            r'(?:introducing|explaining|discussing)\s+([A-Za-z\s]{3,30})',
            r'([A-Z][A-Za-z\s]{3,30})\s+(?:involves|includes|contains)',
        ]
        
        # Search for each pattern in the text
        for pattern in context_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                # Clean up extra spaces
                cleaned_match = re.sub(r'\s+', ' ', match.strip())
                if self._is_meaningful_topic(cleaned_match):
                    context_terms.append(cleaned_match.title())
        
        return context_terms[:10]  # Return maximum 10 context-based terms

    def _extract_semantic_clusters(self, text):
        """
        Extract terms that appear in similar contexts (semantic clustering).

        Finds words that frequently appear together or in similar contexts,
        which suggests they are related to important topics.

        Args:
            text (str): Input text to analyze

        Returns:
            list: Terms that appear in rich semantic contexts
        """
        # Split text into sentences for context analysis
        sentences = re.split(r'[.!?]+', text)
        
        # Track what words appear near each other
        word_contexts = {}
        
        for sentence in sentences:
            # Find meaningful words in this sentence
            words = re.findall(r'\b[A-Za-z]{4,}\b', sentence.lower())
            words = [w for w in words if w not in self.stopwords and len(w) > 4]
            
            # Record context for each word (what words appear near it)
            for i, word in enumerate(words):
                if word not in word_contexts:
                    word_contexts[word] = []
                
                # Add surrounding words as context (2 words before and after)
                context_start = max(0, i-2)
                context_end = min(len(words), i+3)
                context = words[context_start:context_end]
                word_contexts[word].extend([w for w in context if w != word])
        
        # Find words that appear in diverse, rich contexts
        semantic_terms = []
        for word, contexts in word_contexts.items():
            if len(set(contexts)) >= 5:  # Appears with many different words
                context_freq = Counter(contexts)
                # If word has strong semantic associations
                if len(context_freq) >= 3:
                    semantic_terms.append(word.title())
        
        return semantic_terms[:10]  # Return maximum 10 semantic terms

    # ========== Helper Methods for Filtering and Validation ==========

    def _is_meaningful_topic(self, term):
        """
        Check if a term is meaningful as a topic (not junk).

        Applies various filters to determine if a term is worth keeping
        as a topic or should be discarded as noise.

        Args:
            term (str): Term to evaluate

        Returns:
            bool: True if term is meaningful, False if it's junk
        """
        if not term or not isinstance(term, str):
            return False
        
        term = term.strip()
        term_lower = term.lower()
        
        # Basic length filters
        if len(term) < 3 or len(term) > 60:
            return False
        
        # Check if it's a stopword
        if term_lower in self.stopwords:
            return False
        
        # Check if it's mostly symbols or numbers (at least 60% should be letters)
        if len(re.findall(r'[A-Za-z]', term)) < len(term) * 0.6:
            return False
        
        # Check if all words in the term are stopwords
        words = term_lower.split()
        if all(word in self.stopwords for word in words):
            return False
        
        # Avoid common junk patterns
        junk_patterns = [
            r'^\d+$',  # Just numbers like "123"
            r'^[^\w]+$',  # Just symbols like "!!!"
            r'page\s*\d+',  # Page references like "page 5"
            r'figure\s*\d+',  # Figure references like "figure 2"
        ]
        
        if any(re.match(pattern, term_lower) for pattern in junk_patterns):
            return False
        
        return True

    def _has_meaning_indicators(self, word, text):
        """
        Check if a word has semantic meaning in the text context.

        Determines if a word is actually meaningful by checking if it
        appears in definition-like contexts or has rich associations.

        Args:
            word (str): Word to check for meaning
            text (str): Full text for context analysis

        Returns:
            bool: True if word has semantic meaning, False otherwise
        """
        word_lower = word.lower()
        text_lower = text.lower()
        
        # Find sentences that contain this word
        sentences_with_word = [s for s in text_lower.split('.') if word_lower in s]
        
        # Word must appear in at least 2 different contexts
        if len(sentences_with_word) < 2:
            return False
        
        # Check if word appears in definition-like contexts
        definition_contexts = [
            f'{word_lower} is',
            f'{word_lower} are',
            f'{word_lower} means',
            f'{word_lower} refers',
            f'concept of {word_lower}',
            f'understanding {word_lower}',
        ]
        
        has_definition_context = any(context in text_lower for context in definition_contexts)
        
        # Check if word has rich semantic associations
        word_sentences = [s for s in sentences_with_word if len(s.split()) > 5]
        has_rich_context = len(word_sentences) >= 2
        
        return has_definition_context or has_rich_context

    def _clean_and_filter_topics(self, topics):
        """
        Clean and filter the list of topics to remove duplicates and normalize.

        Takes the raw list of topics from all extraction methods and
        cleans them up for final processing.

        Args:
            topics (list): Raw list of topics from extraction methods

        Returns:
            list: Cleaned and deduplicated list of topics
        """
        cleaned = []
        seen = set()
        
        for topic in topics:
            # Skip if not meaningful
            if not self._is_meaningful_topic(topic):
                continue
            
            # Normalize whitespace and capitalization
            topic = re.sub(r'\s+', ' ', topic).strip()
            topic = topic.title()
            topic_lower = topic.lower()
            
            # Skip duplicates
            if topic_lower in seen:
                continue
            
            seen.add(topic_lower)
            cleaned.append(topic)
        
        return cleaned

    # ========== Topic Ranking and Scoring ==========

    def _rank_by_importance(self, topics, text):
        """
        Rank topics by importance using multiple scoring factors.

        Calculates a comprehensive importance score for each topic based on
        frequency, position, context richness, and other factors.

        Args:
            topics (list): List of cleaned topics to rank
            text (str): Original text for scoring analysis

        Returns:
            list: Topics ranked by importance (most important first)
        """
        if not topics:
            return []
        
        text_lower = text.lower()
        scored_topics = []
        
        for topic in topics:
            topic_lower = topic.lower()
            
            # Factor 1: Frequency in text (how often topic appears)
            frequency = text_lower.count(topic_lower)
            
            # Factor 2: Position score (earlier appearance = more important)
            first_pos = text_lower.find(topic_lower)
            position_score = 1000 / (first_pos + 1) if first_pos >= 0 else 0
            
            # Factor 3: Context richness (how many sentences mention this topic)
            sentences_with_topic = [s for s in text_lower.split('.') if topic_lower in s]
            context_score = len(sentences_with_topic) * 10
            
            # Factor 4: Multi-word bonus (phrases are often more specific/important)
            word_count_bonus = len(topic.split()) * 50
            
            # Factor 5: Capitalization bonus (proper nouns are often important)
            capitalization_bonus = 100 if topic[0].isupper() else 0
            
            # Calculate total importance score
            total_score = (frequency * 100 + 
                          position_score + 
                          context_score + 
                          word_count_bonus + 
                          capitalization_bonus)
            
            if total_score > 0:
                scored_topics.append((topic, total_score))
        
        # Sort by score (highest first) and return just the topics
        scored_topics.sort(key=lambda x: x[1], reverse=True)
        return [topic for topic, score in scored_topics]

    # ========== Additional Utility Methods ==========

    def extract_keywords(self, text, top_n=20):
        """
        Extract keywords from text based on frequency.

        Simple keyword extraction that finds the most common meaningful words.

        Args:
            text (str): Text to analyze
            top_n (int): Number of top keywords to return

        Returns:
            list: List of (keyword, frequency) tuples
        """
        # Find all words of 4+ characters
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Filter out stopwords
        filtered = [w for w in words if w not in self.stopwords]
        # Count frequency and return top results
        freq = Counter(filtered)
        return freq.most_common(top_n)

    def split_into_sentences(self, text):
        """
        Split text into individual sentences using NLTK.

        Args:
            text (str): Text to split

        Returns:
            list: List of sentences
        """
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text)