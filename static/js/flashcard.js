// ========== Flashcard Management System ==========
// This file handles all flashcard functionality including navigation, filtering, and animations

/**
 * FlashcardManager Class - Manages flashcard display and interactions
 * 
 * This class handles all the flashcard functionality like:
 * - Displaying flashcards one by one
 * - Flipping cards to show answers
 * - Navigating between cards (next/previous)
 * - Filtering cards by topic
 * - Adding smooth animations
 */
class FlashcardManager {
    /**
     * Initialize the flashcard manager with a list of flashcards
     * 
     * @param {Array} flashcards - Array of flashcard objects with question, answer, topic, etc.
     */
    constructor(flashcards) {
        this.flashcards = flashcards;           // Store all original flashcards
        this.currentIndex = 0;                  // Which card we're currently showing (starts at first card)
        this.filteredCards = [...flashcards];   // Copy of cards that can be filtered by topic
        this.isFlipped = false;                 // Track if current card is showing answer side
    }

    // ========== Card Display and Update Methods ==========
    
    /**
     * Update the displayed flashcard with new content
     * 
     * This method refreshes the card display when user navigates to different card
     * or when filters are applied. It updates the question, answer, and counter.
     */
    updateCard() {
        // Get the current card from filtered list
        const card = this.filteredCards[this.currentIndex];
        const flashcardElement = document.getElementById('flashcard');
        
        // Update the text content on both sides of the card
        document.getElementById('questionContent').textContent = card.question;
        document.getElementById('answerContent').textContent = card.answer;
        
        // Update the card counter (e.g., "3 / 25")
        document.getElementById('currentCard').textContent = this.currentIndex + 1;
        document.getElementById('totalCards').textContent = this.filteredCards.length;
        
        // Always show question side when switching to new card
        flashcardElement.classList.remove('flipped');
        this.isFlipped = false;
        
        // Add a smooth slide-in animation when card changes
        flashcardElement.style.animation = 'cardSlide 0.3s ease';
        setTimeout(() => {
            // Remove animation after it completes so it can run again next time
            flashcardElement.style.animation = '';
        }, 300);
    }

    // ========== Card Interaction Methods ==========
    
    /**
     * Flip the flashcard to show question or answer side
     * 
     * This creates the 3D flip effect to reveal the answer when user clicks card
     * or presses spacebar. Can be called multiple times to flip back and forth.
     */
    flipCard() {
        const flashcardElement = document.getElementById('flashcard');
        
        // Toggle the 'flipped' CSS class which triggers the 3D rotation
        flashcardElement.classList.toggle('flipped');
        
        // Keep track of which side is currently showing
        this.isFlipped = !this.isFlipped;
    }

    // ========== Navigation Methods ==========
    
    /**
     * Navigate to the next flashcard in the sequence
     * 
     * Moves forward one card if there are more cards available.
     * Shows notification if already at the last card.
     */
    nextCard() {
        // Check if there's a next card available
        if (this.currentIndex < this.filteredCards.length - 1) {
            this.currentIndex++;        // Move to next card
            this.updateCard();          // Refresh display with new card
        } else {
            // User is already at last card - show friendly message
            showNotification('Last card reached!', 'info');
        }
    }
    
    /**
     * Navigate to the previous flashcard in the sequence
     * 
     * Moves backward one card if not already at the first card.
     * Shows notification if already at the first card.
     */
    previousCard() {
        // Check if there's a previous card available
        if (this.currentIndex > 0) {
            this.currentIndex--;        // Move to previous card
            this.updateCard();          // Refresh display with new card
        } else {
            // User is already at first card - show friendly message
            showNotification('First card reached!', 'info');
        }
    }

    // ========== Filtering Methods ==========
    
    /**
     * Filter flashcards by topic to show only cards from selected topic
     * 
     * @param {string} topic - Topic name to filter by, or 'all' to show all cards
     * 
     * This allows users to study specific topics by hiding cards from other topics.
     * Automatically resets to first card after filtering.
     */
    filterByTopic(topic) {
        if (topic === 'all') {
            // Show all cards - restore original full list
            this.filteredCards = [...this.flashcards];
        } else {
            // Filter to show only cards matching the selected topic
            this.filteredCards = this.flashcards.filter(card => card.topic === topic);
        }
        
        // Always go back to first card after applying filter
        this.currentIndex = 0;
        this.updateCard();
        
        // Show user how many cards are now available
        showNotification(`Filtered to ${this.filteredCards.length} cards`, 'success');
    }
}

// ========== CSS Animation Definitions ==========
// Create and inject CSS animations for smooth card transitions

/**
 * Add slide animation for flashcard transitions
 * 
 * This creates a smooth slide-in effect when switching between cards.
 * The animation makes cards appear to slide in from the left.
 */
const cardStyle = document.createElement('style');
cardStyle.textContent = `
    @keyframes cardSlide {
        from {
            transform: translateX(-50px);    /* Start position: 50px to the left */
            opacity: 0;                      /* Start invisible */
        }
        to {
            transform: translateX(0);        /* End position: normal position */
            opacity: 1;                      /* End fully visible */
        }
    }
`;

// Add the animation styles to the page
document.head.appendChild(cardStyle);