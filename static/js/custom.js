// Modern Invoice Generator SaaS - Teen-Friendly Interactions

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts with slide animation
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transform = 'translateX(100%)';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Add confirmation for delete actions with style
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('🚨 ' + this.dataset.confirm + ' This action cannot be undone!')) {
                e.preventDefault();
            }
        });
    });
    
    // Enhanced AJAX form handling with loading states
    const statusForms = document.querySelectorAll('.status-form');
    statusForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
            submitBtn.disabled = true;
            
            const formData = new FormData(form);
            const url = form.action;
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success animation
                    showNotification('success', '🎉 ' + data.message);
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showNotification('error', '❌ Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('error', '❌ Something went wrong! Please try again.');
            })
            .finally(() => {
                // Restore button state
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    });
    
    // Smooth scroll for anchor links
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
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Parallax effect for cards
    const cards = document.querySelectorAll('.card');
    const handleMouseMove = (e) => {
        const { clientX, clientY } = e;
        const { innerWidth, innerHeight } = window;
        const x = (clientX / innerWidth) * 100;
        const y = (clientY / innerHeight) * 100;
        
        cards.forEach((card, index) => {
            const speed = (index + 1) * 0.5;
            card.style.transform = `translate(${x * speed * 0.01}px, ${y * speed * 0.01}px)`;
        });
    };
    
    // Add subtle parallax only on larger screens
    if (window.innerWidth > 768) {
        document.addEventListener('mousemove', handleMouseMove);
    }
    
    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
    
    // Dynamic theme based on time of day
    const hour = new Date().getHours();
    if (hour >= 20 || hour <= 6) {
        document.body.classList.add('night-mode');
    }
    
    // Add loading states to navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.href && !this.href.includes('#')) {
                this.innerHTML += ' <i class="fas fa-spinner fa-spin ms-1"></i>';
            }
        });
    });
});

// Custom notification system
function showNotification(type, message) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show animate__animated animate__bounceInRight`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('animate__bounceOutRight');
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

// Field validation with visual feedback
function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    const isRequired = field.hasAttribute('required');
    
    let isValid = true;
    let errorMessage = '';
    
    if (isRequired && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    } else if (fieldType === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
    } else if (fieldType === 'password' && value && value.length < 8) {
        isValid = false;
        errorMessage = 'Password must be at least 8 characters long';
    }
    
    // Update field appearance
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        removeErrorMessage(field);
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showErrorMessage(field, errorMessage);
    }
    
    return isValid;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showErrorMessage(field, message) {
    removeErrorMessage(field);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback animate__animated animate__shakeX';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function removeErrorMessage(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: rippleEffect 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes rippleEffect {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .night-mode {
        filter: hue-rotate(180deg) invert(1);
    }
    
    .is-valid {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
    }
    
    .is-invalid {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
    }
`;
document.head.appendChild(style);