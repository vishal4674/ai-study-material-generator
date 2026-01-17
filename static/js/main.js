// ========== Global Utility Functions ==========
// Main JavaScript file that handles common functionality across all pages

/**
 * Initialize the application when the page loads.
 * 
 * This function sets up:
 * - Smooth scrolling for anchor links
 * - Loading animations for buttons
 * - Basic interaction effects
 * - Console logging for debugging
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Study Material Generator - Loaded');
    
    // ========== Smooth Scrolling Setup ==========
    // Add smooth scrolling to all anchor links that start with #
    
    /**
     * Enable smooth scrolling for internal page links.
     * 
     * When users click on links that point to sections within the same page
     * (like #section1), smoothly scroll to that section instead of jumping.
     */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();  // Prevent default jump behavior
            
            // Find the target element using the href attribute
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                // Smoothly scroll to the target element
                target.scrollIntoView({
                    behavior: 'smooth',    // Smooth animation instead of instant jump
                    block: 'start'        // Align to the top of the element
                });
            }
        });
    });
    
    // ========== Button Animation Setup ==========
    // Add visual feedback when buttons are clicked
    
    /**
     * Add loading animation to buttons when clicked.
     * 
     * Makes buttons slightly transparent when clicked to give users
     * visual feedback that their action was registered.
     */
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Don't animate delete buttons (they need immediate feedback)
            if (!this.classList.contains('btn-delete')) {
                // Make button slightly transparent
                this.style.opacity = '0.7';
                
                // Restore normal opacity after 300ms
                setTimeout(() => {
                    this.style.opacity = '1';
                }, 300);
            }
        });
    });
});

// ========== Notification System ==========

/**
 * Show notification messages to users.
 * 
 * Creates a popup notification in the top-right corner of the screen
 * with different colors based on the message type.
 * 
 * @param {string} message - Text to display in the notification
 * @param {string} type - Type of notification ('success', 'error', 'info')
 * 
 * Example:
 *   showNotification('File uploaded successfully!', 'success');
 *   showNotification('Something went wrong', 'error');
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Set styles for the notification popup
    notification.style.cssText = `
        position: fixed;                    /* Stay in place when scrolling */
        top: 20px;                         /* Distance from top of screen */
        right: 20px;                       /* Distance from right of screen */
        padding: 1rem 2rem;                /* Internal spacing */
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};  /* Color based on type */
        color: white;                      /* White text */
        border-radius: 8px;                /* Rounded corners */
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);  /* Drop shadow */
        z-index: 10000;                    /* Make sure it's on top of everything */
        animation: slideIn 0.3s ease;      /* Slide in animation */
    `;
    
    // Add notification to the page
    document.body.appendChild(notification);
    
    // Auto-remove notification after 3 seconds
    setTimeout(() => {
        // Start slide-out animation
        notification.style.animation = 'slideOut 0.3s ease';
        
        // Remove element after animation completes
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ========== CSS Animation Definitions ==========
// Create and inject CSS animations for notifications

/**
 * Add CSS keyframe animations for notification slide effects.
 * 
 * Creates smooth slide-in and slide-out animations that make
 * notifications appear from the right and disappear to the right.
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);    /* Start position: 400px to the right */
            opacity: 0;                      /* Start invisible */
        }
        to {
            transform: translateX(0);        /* End position: normal position */
            opacity: 1;                      /* End fully visible */
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);        /* Start position: normal position */
            opacity: 1;                      /* Start fully visible */
        }
        to {
            transform: translateX(400px);    /* End position: 400px to the right */
            opacity: 0;                      /* End invisible */
        }
    }
`;

// Add the animation styles to the page head
document.head.appendChild(style);