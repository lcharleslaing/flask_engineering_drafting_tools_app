// Engineering/Drafting Tools - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Add fade-in animation to cards
    addFadeInAnimation();

    // Initialize tooltips
    initializeTooltips();

    // Setup navigation
    setupNavigation();

    // Setup status indicators
    setupStatusIndicators();

    // Setup form handlers
    setupFormHandlers();

    console.log('Engineering/Drafting Tools initialized');
}

function addFadeInAnimation() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.classList.add('fade-in');
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function initializeTooltips() {
    // Simple tooltip implementation
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const tooltipText = event.target.getAttribute('data-tooltip');
    if (!tooltipText) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip tooltip-open tooltip-top';
    tooltip.textContent = tooltipText;
    tooltip.style.position = 'absolute';
    tooltip.style.zIndex = '1000';

    document.body.appendChild(tooltip);

    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';

    event.target._tooltip = tooltip;
}

function hideTooltip(event) {
    if (event.target._tooltip) {
        event.target._tooltip.remove();
        event.target._tooltip = null;
    }
}

function setupNavigation() {
    // Handle active navigation states
    const navLinks = document.querySelectorAll('.navbar a');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Handle mobile menu toggle
    const mobileMenuButton = document.querySelector('.btn-ghost.lg\\:hidden');
    const mobileMenu = document.querySelector('.dropdown-content');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

function setupStatusIndicators() {
    // Check Flask server status
    checkServerStatus();

    // Update status every 30 seconds
    setInterval(checkServerStatus, 30000);
}

async function checkServerStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        updateStatusIndicator('flask-status', data.status === 'running' ? 'online' : 'offline');
        updateStatusIndicator('electron-status', 'online');

    } catch (error) {
        updateStatusIndicator('flask-status', 'offline');
        updateStatusIndicator('electron-status', 'online');
    }
}

function updateStatusIndicator(elementId, status) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = `status-indicator status-${status}`;
    }
}

function setupFormHandlers() {
    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

    // Handle input validation
    const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
    });
}

function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        const originalText = submitButton.textContent;
        submitButton.innerHTML = '<span class="loading"></span> Processing...';
        submitButton.disabled = true;

        // Simulate processing
        setTimeout(() => {
            submitButton.textContent = originalText;
            submitButton.disabled = false;
            showNotification('Form submitted successfully!', 'success');
        }, 2000);
    }
}

function validateInput(event) {
    const input = event.target;
    const value = input.value.trim();

    if (input.hasAttribute('required') && !value) {
        input.classList.add('input-error');
        showFieldError(input, 'This field is required');
    } else {
        input.classList.remove('input-error');
        hideFieldError(input);
    }
}

function showFieldError(input, message) {
    hideFieldError(input);

    const errorDiv = document.createElement('div');
    errorDiv.className = 'label-text-alt text-error mt-1';
    errorDiv.textContent = message;
    errorDiv.setAttribute('data-field-error', 'true');

    input.parentNode.appendChild(errorDiv);
}

function hideFieldError(input) {
    const existingError = input.parentNode.querySelector('[data-field-error="true"]');
    if (existingError) {
        existingError.remove();
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-sm`;
    notification.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>${message}</span>
        <button class="btn btn-sm btn-ghost" onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Utility functions
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

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

// Export functions for use in other scripts
window.EngineeringTools = {
    showNotification,
    formatNumber,
    debounce
};
