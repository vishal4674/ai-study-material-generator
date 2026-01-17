# ========== Imports ==========
from collections import defaultdict

class LearningPathGenerator:
    """
    Generate personalized learning paths for students.

    This class creates a structured study plan by:
    - Organizing topics in a logical order
    - Estimating time needed for each topic
    - Setting difficulty levels based on flashcard complexity
    - Creating prerequisites between topics
    """

    def __init__(self):
        # Difficulty weights for time estimation
        self.difficulty_weights = {
            'easy': 1,
            'medium': 2,
            'hard': 3
        }

    def generate(self, topics, flashcards):
        """
        Generate a complete learning path from topics and flashcards.

        Args:
            topics (list): List of key topics extracted from the material
            flashcards (list): List of flashcard dictionaries with questions/answers

        Returns:
            dict: Complete learning path with steps, time estimates, and progression
        """
        # Group flashcards by their topics for easier processing
        topic_cards = self._group_by_topic(flashcards)

        # Create individual learning steps for each topic
        steps = self._create_learning_steps(topics, topic_cards)

        # Calculate estimated study time for each step
        for step in steps:
            step['estimated_time'] = self._estimate_time(step)

        # Set up prerequisites (what needs to be learned first)
        for i, step in enumerate(steps):
            step['prerequisites'] = [steps[j]['topic'] for j in range(i) if j < i]

        # Build the complete learning path structure
        learning_path = {
            'total_steps': len(steps),
            'total_time': sum(step['estimated_time'] for step in steps),
            'steps': steps,
            'difficulty_progression': self._get_difficulty_progression(steps)
        }

        return learning_path

    def _group_by_topic(self, flashcards):
        """
        Group flashcards by their topics.

        This helps us see how many flashcards belong to each topic.

        Args:
            flashcards (list): List of flashcard dictionaries

        Returns:
            dict: Dictionary with topics as keys and lists of flashcards as values
        """
        topic_cards = defaultdict(list)

        for card in flashcards:
            # Get the topic of this flashcard (default to 'General' if not specified)
            topic = card.get('topic', 'General')
            topic_cards[topic].append(card)

        return dict(topic_cards)

    def _create_learning_steps(self, topics, topic_cards):
        """
        Create individual learning steps from topics.

        Each step represents one topic that the student needs to learn.

        Args:
            topics (list): List of topics to create steps for
            topic_cards (dict): Dictionary of flashcards grouped by topic

        Returns:
            list: List of learning step dictionaries
        """
        steps = []

        # Create a step for each topic (maximum 10 steps to keep it manageable)
        for i, topic in enumerate(topics[:10]):
            # Count how many flashcards are available for this topic
            num_cards = len(topic_cards.get(topic, []))

            # Determine how difficult this step will be
            difficulty = self._determine_step_difficulty(topic_cards.get(topic, []))

            # Create the step structure
            step = {
                'step_number': i + 1,
                'topic': topic,
                'description': f"Learn about {topic}",
                'num_flashcards': num_cards,
                'difficulty': difficulty,
                'status': 'locked' if i > 0 else 'available'  # Only first step is available initially
            }

            steps.append(step)

        return steps

    def _determine_step_difficulty(self, cards):
        """
        Determine the difficulty level of a learning step based on its flashcards.

        Looks at the difficulty of individual flashcards to decide overall step difficulty.

        Args:
            cards (list): List of flashcards for this topic

        Returns:
            str: Difficulty level ('easy', 'medium', or 'hard')
        """
        if not cards:
            return 'medium'  # Default difficulty if no cards available

        # Get difficulty levels of all flashcards
        difficulties = [card.get('difficulty', 'medium') for card in cards]

        # Count how many cards are at each difficulty level
        easy_count = difficulties.count('easy')
        medium_count = difficulties.count('medium')
        hard_count = difficulties.count('hard')

        # Determine overall difficulty based on card distribution
        if hard_count > len(cards) * 0.5:  # More than 50% hard cards
            return 'hard'
        elif easy_count > len(cards) * 0.5:  # More than 50% easy cards
            return 'easy'
        else:
            return 'medium'  # Mixed or mostly medium cards

    def _estimate_time(self, step):
        """
        Estimate how much time a student needs to complete a learning step.

        Considers the number of flashcards and difficulty level.

        Args:
            step (dict): Learning step dictionary

        Returns:
            int: Estimated time in minutes
        """
        base_time = 15  # Base time for any topic (15 minutes)

        # Add time based on number of flashcards (2 minutes per card)
        card_time = step['num_flashcards'] * 2

        # Multiply by difficulty (easy=1x, medium=2x, hard=3x)
        difficulty_multiplier = self.difficulty_weights.get(step['difficulty'], 1)

        # Calculate total time needed
        total_time = int((base_time + card_time) * difficulty_multiplier)

        return total_time

    def _get_difficulty_progression(self, steps):
        """
        Get the difficulty progression through all learning steps.

        Shows how difficulty changes as student progresses through the path.

        Args:
            steps (list): List of learning step dictionaries

        Returns:
            list: List of dictionaries showing step number and difficulty
        """
        progression = []

        for step in steps:
            progression.append({
                'step': step['step_number'],
                'difficulty': step['difficulty']
            })

        return progression