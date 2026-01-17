# ========== Imports ==========
import re
from nltk.tokenize import sent_tokenize
import random

class FlashcardGenerator:
    """
    Generate flashcards from text content using dynamic methods.

    This class creates question-answer pairs from study material by:
    - Finding definition sentences in the text
    - Creating concept questions based on topics
    - Making comparison questions between related topics
    - Generating feature and process questions
    """

    def __init__(self):
        # Pre-defined question patterns to look for in text
        self.question_patterns = [
            r'what is (.*?)\?',
            r'define (.*?)[\.\?]',
            r'explain (.*?)[\.\?]',
            r'(.*?) is defined as (.*?)[\.\?]',
            r'(.*?) refers to (.*?)[\.\?]'
        ]

    def generate(self, text, topics, num_cards=20):
        """
        Generate flashcards from text using multiple methods.

        Args:
            text (str): The source text to create flashcards from
            topics (list): List of key topics found in the text
            num_cards (int): Maximum number of flashcards to generate

        Returns:
            list: List of flashcard dictionaries with questions and answers
        """
        flashcards = []
        sentences = sent_tokenize(text)

        print(f"Generating flashcards from {len(sentences)} sentences")
        print(f"Topics available: {topics[:5]}")

        # Method 1: Extract definition-like sentences
        definition_cards = self._extract_definition_cards(sentences, topics, text)
        flashcards.extend(definition_cards)

        # Method 2: Generate concept questions from content
        concept_cards = self._generate_concept_questions(text, topics, sentences)
        flashcards.extend(concept_cards)

        # Method 3: Generate comparison questions
        comparison_cards = self._generate_comparison_questions(text, topics, sentences)
        flashcards.extend(comparison_cards)

        # Method 4: Generate feature/characteristic questions
        feature_cards = self._generate_feature_questions(text, topics, sentences)
        flashcards.extend(feature_cards)

        # Method 5: Generate process/how questions
        process_cards = self._generate_process_questions(text, topics, sentences)
        flashcards.extend(process_cards)

        # Remove duplicates and limit to requested number
        flashcards = self._remove_duplicates(flashcards)
        flashcards = flashcards[:num_cards]

        # Add metadata to each flashcard
        for i, card in enumerate(flashcards):
            card['id'] = i + 1
            card['difficulty'] = self._assign_difficulty(card)

        print(f" Generated {len(flashcards)} flashcards")
        return flashcards

    def _extract_definition_cards(self, sentences, topics, full_text):
        """
        Extract definition-like sentences and turn them into Q&A pairs.

        Looks for sentences that define or explain topics using words like
        "is", "means", "refers to", etc.

        Args:
            sentences (list): List of sentences from the text
            topics (list): List of key topics
            full_text (str): Complete text for context

        Returns:
            list: List of definition-based flashcards
        """
        cards = []

        # Words that usually indicate definitions
        definition_indicators = [
            'is', 'are', 'refers to', 'defined as', 'means', 'represents',
            'consists of', 'includes', 'involves', 'characterized by'
        ]

        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Check if sentence contains definition indicators
            if any(indicator in sentence_lower for indicator in definition_indicators):
                # Find which topic this sentence is about
                for topic in topics[:10]:
                    if topic.lower() in sentence_lower and len(sentence.split()) > 5:
                        # Create definition question
                        question = f"What is {topic}?"
                        answer = sentence.strip()

                        # Make sure answer is long enough to be meaningful
                        if len(answer.split()) >= 8:
                            cards.append({
                                'question': question,
                                'answer': answer,
                                'topic': topic,
                                'type': 'definition'
                            })
                        break

        return cards[:8]  # Return maximum 8 definition cards

    def _generate_concept_questions(self, text, topics, sentences):
        """
        Generate concept-based questions from content.

        Creates various types of questions about each topic using templates.

        Args:
            text (str): Source text
            topics (list): List of key topics
            sentences (list): List of sentences

        Returns:
            list: List of concept-based flashcards
        """
        cards = []

        # Different question templates we can use
        concept_templates = [
            ("What is {}?", "definition"),
            ("Explain the concept of {}.", "explanation"),
            ("Define {}.", "definition"),
            ("What are the key features of {}?", "features"),
            ("How does {} work?", "mechanism"),
            ("What is the purpose of {}?", "purpose"),
            ("Why is {} important?", "importance")
        ]

        for topic in topics[:15]:
            # Find sentences that talk about this topic
            related_sentences = []
            for sentence in sentences:
                if topic.lower() in sentence.lower() and len(sentence.split()) > 6:
                    related_sentences.append(sentence.strip())

            if related_sentences:
                # Pick a random question template
                template, card_type = random.choice(concept_templates)
                question = template.format(topic)

                # Use 1-2 most relevant sentences as the answer
                answer = ". ".join(related_sentences[:2])

                # Keep answer length reasonable
                if len(answer.split()) > 50:
                    answer = ". ".join(answer.split('.')[:2]) + "."

                cards.append({
                    'question': question,
                    'answer': answer,
                    'topic': topic,
                    'type': card_type
                })

        return cards[:10]  # Return maximum 10 concept cards

    def _generate_comparison_questions(self, text, topics, sentences):
        """
        Generate comparison questions between different concepts.

        Looks for sentences that compare or contrast topics.

        Args:
            text (str): Source text
            topics (list): List of key topics
            sentences (list): List of sentences

        Returns:
            list: List of comparison flashcards
        """
        cards = []

        # Words that indicate comparisons
        comparison_words = ['difference', 'compare', 'versus', 'vs', 'unlike', 'similar', 'contrast']

        for sentence in sentences:
            sentence_lower = sentence.lower()

            if any(word in sentence_lower for word in comparison_words):
                # Find topics mentioned in this sentence
                mentioned_topics = [topic for topic in topics if topic.lower() in sentence_lower]

                if len(mentioned_topics) >= 2:
                    topic1, topic2 = mentioned_topics[:2]
                    question = f"What is the difference between {topic1} and {topic2}?"
                    answer = sentence.strip()

                    cards.append({
                        'question': question,
                        'answer': answer,
                        'topic': f"{topic1} vs {topic2}",
                        'type': 'comparison'
                    })

        return cards[:3]  # Return maximum 3 comparison cards

    def _generate_feature_questions(self, text, topics, sentences):
        """
        Generate questions about features and characteristics of topics.

        Looks for sentences that describe properties or features.

        Args:
            text (str): Source text
            topics (list): List of key topics
            sentences (list): List of sentences

        Returns:
            list: List of feature-based flashcards
        """
        cards = []

        # Words that indicate features or characteristics
        feature_words = ['characteristics', 'features', 'properties', 'advantages', 'benefits', 'types']

        for sentence in sentences:
            sentence_lower = sentence.lower()

            if any(word in sentence_lower for word in feature_words):
                for topic in topics[:10]:
                    if topic.lower() in sentence_lower and len(sentence.split()) > 8:
                        question = f"What are the key characteristics of {topic}?"
                        answer = sentence.strip()

                        cards.append({
                            'question': question,
                            'answer': answer,
                            'topic': topic,
                            'type': 'features'
                        })
                        break

        return cards[:5]  # Return maximum 5 feature cards

    def _generate_process_questions(self, text, topics, sentences):
        """
        Generate process/how-to questions about topics.

        Looks for sentences that describe processes, methods, or procedures.

        Args:
            text (str): Source text
            topics (list): List of key topics
            sentences (list): List of sentences

        Returns:
            list: List of process-based flashcards
        """
        cards = []

        # Words that indicate processes or methods
        process_words = ['process', 'steps', 'procedure', 'method', 'approach', 'technique']

        for sentence in sentences:
            sentence_lower = sentence.lower()

            if any(word in sentence_lower for word in process_words):
                for topic in topics[:8]:
                    if topic.lower() in sentence_lower and len(sentence.split()) > 6:
                        question = f"How does {topic} work?"
                        answer = sentence.strip()

                        cards.append({
                            'question': question,
                            'answer': answer,
                            'topic': topic,
                            'type': 'process'
                        })
                        break

        return cards[:4]  # Return maximum 4 process cards

    def _remove_duplicates(self, flashcards):
        """
        Remove duplicate flashcards based on similar questions.

        Args:
            flashcards (list): List of flashcard dictionaries

        Returns:
            list: List of unique flashcards
        """
        seen_questions = set()
        unique_cards = []

        for card in flashcards:
            # Normalize question text for comparison
            question_normalized = card['question'].lower().strip()

            if question_normalized not in seen_questions:
                seen_questions.add(question_normalized)
                unique_cards.append(card)

        return unique_cards

    def _assign_difficulty(self, card):
        """
        Assign difficulty level based on answer complexity.

        Considers answer length and presence of complex terms.

        Args:
            card (dict): Flashcard dictionary

        Returns:
            str: Difficulty level ('easy', 'medium', or 'hard')
        """
        answer = card['answer']
        answer_length = len(answer.split())

        # Words that indicate complex concepts
        complex_terms = ['implementation', 'architecture', 'methodology', 'paradigm', 'algorithm']
        has_complex_terms = any(term in answer.lower() for term in complex_terms)

        # Determine difficulty based on length and complexity
        if answer_length < 15 and not has_complex_terms:
            return 'easy'
        elif answer_length < 30 and not has_complex_terms:
            return 'medium'
        else:
            return 'hard'