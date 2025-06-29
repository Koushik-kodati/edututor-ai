// Main JavaScript for EduTutor AI

// Global variables
let currentUser = null;
let notifications = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkNotifications();
});

function initializeApp() {
    // Add loading states to buttons
    addLoadingStates();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup theme toggle
    setupThemeToggle();
    
    // Add smooth scrolling
    addSmoothScrolling();
}

function setupEventListeners() {
    // Global click handlers
    document.addEventListener('click', function(e) {
        // Handle dropdown toggles
        if (e.target.matches('[data-bs-toggle="dropdown"]')) {
            handleDropdownToggle(e);
        }
        
        // Handle modal triggers
        if (e.target.matches('[data-bs-toggle="modal"]')) {
            handleModalTrigger(e);
        }
    });
    
    // Form validation
    document.addEventListener('submit', function(e) {
        if (e.target.matches('form[data-validate="true"]')) {
            handleFormValidation(e);
        }
    });
    
    // Auto-save functionality
    document.addEventListener('input', function(e) {
        if (e.target.matches('[data-autosave="true"]')) {
            debounce(autoSave, 1000)(e.target);
        }
    });
}

function addLoadingStates() {
    // Add loading states to all buttons with data-loading attribute
    document.querySelectorAll('button[data-loading]').forEach(button => {
        button.addEventListener('click', function() {
            showButtonLoading(this);
        });
    });
}

function showButtonLoading(button) {
    const originalText = button.innerHTML;
    const loadingText = button.dataset.loading || 'Loading...';
    
    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>${loadingText}`;
    button.disabled = true;
    
    // Store original text for restoration
    button.dataset.originalText = originalText;
}

function hideButtonLoading(button) {
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupThemeToggle() {
    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        });
    }
}

function addSmoothScrolling() {
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function handleDropdownToggle(e) {
    // Custom dropdown handling if needed
    console.log('Dropdown toggled:', e.target);
}

function handleModalTrigger(e) {
    // Custom modal handling if needed
    console.log('Modal triggered:', e.target);
}

function handleFormValidation(e) {
    const form = e.target;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    
    if (!isValid) {
        e.preventDefault();
        showNotification('Please fill in all required fields correctly.', 'error');
    }
}

function validateInput(input) {
    const value = input.value.trim();
    const type = input.type;
    let isValid = true;
    
    // Remove existing error classes
    input.classList.remove('is-invalid');
    
    // Check if required field is empty
    if (input.hasAttribute('required') && !value) {
        isValid = false;
    }
    
    // Type-specific validation
    switch (type) {
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (value && !emailRegex.test(value)) {
                isValid = false;
            }
            break;
        case 'password':
            if (value && value.length < 6) {
                isValid = false;
            }
            break;
        case 'number':
            if (value && isNaN(value)) {
                isValid = false;
            }
            break;
    }
    
    // Add error class if invalid
    if (!isValid) {
        input.classList.add('is-invalid');
    }
    
    return isValid;
}

function autoSave(input) {
    const data = {
        field: input.name,
        value: input.value,
        timestamp: new Date().toISOString()
    };
    
    // Save to localStorage
    localStorage.setItem(`autosave_${input.name}`, JSON.stringify(data));
    
    // Show auto-save indicator
    showAutoSaveIndicator(input);
}

function showAutoSaveIndicator(input) {
    // Create or update auto-save indicator
    let indicator = input.parentNode.querySelector('.autosave-indicator');
    if (!indicator) {
        indicator = document.createElement('small');
        indicator.className = 'autosave-indicator text-muted';
        input.parentNode.appendChild(indicator);
    }
    
    indicator.textContent = 'Saved';
    indicator.style.opacity = '1';
    
    // Fade out after 2 seconds
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to notifications container or create one
    let container = document.getElementById('notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notifications-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

function checkNotifications() {
    // Check for any pending notifications or updates
    // This could be expanded to check server-side notifications
    const savedNotifications = localStorage.getItem('pending_notifications');
    if (savedNotifications) {
        const notifications = JSON.parse(savedNotifications);
        notifications.forEach(notification => {
            showNotification(notification.message, notification.type);
        });
        localStorage.removeItem('pending_notifications');
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success', 2000);
    }).catch(() => {
        showNotification('Failed to copy to clipboard', 'error', 2000);
    });
}

function downloadFile(data, filename, type = 'text/plain') {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// API helper functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showNotification('Request failed. Please try again.', 'error');
        throw error;
    }
}

// Export functions for use in other scripts
window.EduTutorAI = {
    showNotification,
    showButtonLoading,
    hideButtonLoading,
    validateInput,
    formatDate,
    formatTime,
    copyToClipboard,
    downloadFile,
    apiRequest,
    debounce,
    throttle
};

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        }, 0);
    });
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Could send error reports to server here
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    // Could send error reports to server here
});