// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add floating animation to feature cards
    const featureCards = document.querySelectorAll('.feature-card, .step-card');
    featureCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.2}s`;
        card.classList.add('fade-in');
    });

 

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input[required]');
            let valid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    highlightInvalid(input);
                } else {
                    removeHighlight(input);
                }
            });

            if (!valid) {
                e.preventDefault();
                showToast('Please fill in all required fields.', 'error');
            }
        });
    });

    // Input field focus effects
    const formInputs = document.querySelectorAll('.form-control');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });

    // Dashboard functionality
    if (document.getElementById('detectionsTable')) {
        initializeDashboard();
    }

    // Hero carousel auto-rotation
    const heroCarousel = document.getElementById('heroCarousel');
    if (heroCarousel) {
        const carousel = new bootstrap.Carousel(heroCarousel, {
            interval: 4000,
            ride: 'carousel'
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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

    // Parallax effect for floating elements
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const floaters = document.querySelectorAll('.floater');
        
        floaters.forEach((floater, index) => {
            const speed = 0.5 + (index * 0.1);
            const yPos = -(scrolled * speed);
            floater.style.transform = `translateY(${yPos}px) rotate(${scrolled * 0.1}deg)`;
        });
    });

    // Real-time form validation
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const feedback = this.nextElementSibling;
            if (this.value.length < 6) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    }
});

// Dashboard specific functions
function initializeDashboard() {
    // View details functionality
    const viewButtons = document.querySelectorAll('.view-details');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const detectionId = this.getAttribute('data-id');
            loadDetectionDetails(detectionId);
        });
    });

    // Sort table functionality
    const table = document.getElementById('detectionsTable');
    if (table) {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (index !== headers.length - 1) { // Exclude actions column
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    sortTable(index);
                });
            }
        });
    }
}

function loadDetectionDetails(detectionId) {
    // In a real application, you would fetch this data from the server
    // For now, we'll show a placeholder message
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading detection details...</p>
        </div>
    `;
    
    // Simulate API call
    setTimeout(() => {
        modalBody.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                Detailed view functionality would be implemented here with actual data from the server.
            </div>
            <p><strong>Detection ID:</strong> ${detectionId}</p>
            <p>This would show comprehensive details including:</p>
            <ul>
                <li>Complete patient information</li>
                <li>All vital signs and measurements</li>
                <li>Detailed risk analysis</li>
                <li>Historical trends</li>
                <li>Recommendations and next steps</li>
            </ul>
        `;
    }, 1000);
    
    const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
    modal.show();
}

function sortTable(columnIndex) {
    const table = document.getElementById('detectionsTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isNumeric = columnIndex === 1 || columnIndex === 4 || columnIndex === 5 || columnIndex === 6; // Age, ECG, Heart Rate, Temperature columns
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        if (isNumeric) {
            return parseFloat(aValue) - parseFloat(bValue);
        } else {
            return aValue.localeCompare(bValue);
        }
    });
    
    // Reverse if already sorted
    if (table.getAttribute('data-sort-column') === columnIndex.toString()) {
        rows.reverse();
        table.setAttribute('data-sort-direction', table.getAttribute('data-sort-direction') === 'asc' ? 'desc' : 'asc');
    } else {
        table.setAttribute('data-sort-direction', 'asc');
    }
    
    table.setAttribute('data-sort-column', columnIndex.toString());
    
    // Clear and re-append sorted rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    rows.forEach(row => tbody.appendChild(row));
    
    // Update row numbers
    updateRowNumbers();
}

function updateRowNumbers() {
    const rows = document.querySelectorAll('#detectionsTable tbody tr');
    rows.forEach((row, index) => {
        row.cells[0].textContent = index + 1;
    });
}

// Utility functions
function highlightInvalid(input) {
    input.classList.add('is-invalid');
    input.focus();
}

function removeHighlight(input) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'primary'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after hide
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Export functions for global access (if needed)
window.CardiacApp = {
    showToast,
    highlightInvalid,
    removeHighlight
};