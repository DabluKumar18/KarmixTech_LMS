/**
 * KarmixTech LMS - Main JavaScript
 * Professional Learning Management System
 */

// ===========================
// DOM Ready
// ===========================
document.addEventListener('DOMContentLoaded', function() {
    initSidebar();
    initDropdowns();
    initForms();
    initModals();
    initAlerts();
    initSearch();
    initProgressBars();
    initTooltips();
});


// ===========================
// Sidebar Toggle
// ===========================
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const overlay = document.querySelector('.sidebar-overlay');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('show');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        });
    }

    // Close sidebar on mobile when clicking nav items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            if (window.innerWidth <= 1024) {
                sidebar.classList.remove('open');
                if (overlay) overlay.classList.remove('show');
            }
        });
    });
}


// ===========================
// Dropdown Menus
// ===========================
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(dropdown => {
        const trigger = dropdown.querySelector('.dropdown-trigger, .user-dropdown');

        if (trigger) {
            trigger.addEventListener('click', function(e) {
                e.stopPropagation();
                // Close all other dropdowns
                dropdowns.forEach(d => {
                    if (d !== dropdown) d.classList.remove('show');
                });
                dropdown.classList.toggle('show');
            });
        }
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        dropdowns.forEach(dropdown => dropdown.classList.remove('show'));
    });
}


// ===========================
// Form Validation
// ===========================
function initForms() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });

        // Real-time validation on inputs
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });

            input.addEventListener('input', function() {
                clearError(input);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');

    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });

    // Password confirmation check
    const password = form.querySelector('input[name="password"]');
    const confirmPassword = form.querySelector('input[name="confirm_password"]');

    if (password && confirmPassword && password.value !== confirmPassword.value) {
        showError(confirmPassword, 'Passwords do not match');
        isValid = false;
    }

    return isValid;
}

function validateField(input) {
    const value = input.value.trim();
    const type = input.type;
    const name = input.name;

    clearError(input);

    // Required check
    if (input.hasAttribute('required') && !value) {
        showError(input, 'This field is required');
        return false;
    }

    // Email validation
    if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showError(input, 'Please enter a valid email address');
            return false;
        }
    }

    // Password strength
    if (type === 'password' && value && input.hasAttribute('data-min-length')) {
        const minLength = parseInt(input.getAttribute('data-min-length')) || 8;
        if (value.length < minLength) {
            showError(input, `Password must be at least ${minLength} characters`);
            return false;
        }
        if (!/[A-Z]/.test(value)) {
            showError(input, 'Password must contain uppercase letter');
            return false;
        }
        if (!/[a-z]/.test(value)) {
            showError(input, 'Password must contain lowercase letter');
            return false;
        }
        if (!/[0-9]/.test(value)) {
            showError(input, 'Password must contain a number');
            return false;
        }
    }

    // Phone validation
    if (type === 'tel' && value) {
        const phoneRegex = /^[\d\s\-+()]{10,}$/;
        if (!phoneRegex.test(value)) {
            showError(input, 'Please enter a valid phone number');
            return false;
        }
    }

    // URL validation
    if (type === 'url' && value) {
        try {
            new URL(value);
        } catch {
            showError(input, 'Please enter a valid URL');
            return false;
        }
    }

    input.classList.add('is-valid');
    input.classList.remove('is-invalid');
    return true;
}

function showError(input, message) {
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');

    let errorEl = input.parentElement.querySelector('.form-error');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'form-error';
        input.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

function clearError(input) {
    input.classList.remove('is-invalid');
    const errorEl = input.parentElement.querySelector('.form-error');
    if (errorEl) errorEl.remove();
}


// ===========================
// Modal Management
// ===========================
function initModals() {
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const modalClose = document.querySelectorAll('.modal-close, [data-modal-close]');

    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            openModal(modalId);
        });
    });

    modalClose.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal-backdrop');
            if (modal) closeModal(modal.id);
        });
    });

    // Close on backdrop click
    const modalBackdrops = document.querySelectorAll('.modal-backdrop');
    modalBackdrops.forEach(backdrop => {
        backdrop.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal-backdrop.show');
            if (openModal) closeModal(openModal.id);
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}


// ===========================
// Flash Messages / Alerts
// ===========================
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'alert-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = 'background:none;border:none;font-size:1.25rem;cursor:pointer;margin-left:auto;color:inherit;';
        alert.style.display = 'flex';
        alert.appendChild(closeBtn);

        closeBtn.addEventListener('click', function() {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

function showAlert(type, message) {
    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    const alertHTML = `
        <div class="alert alert-${type}">
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
        </div>
    `;

    const container = document.querySelector('.alert-container') || document.querySelector('.page-content');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHTML);
        initAlerts();
    }
}


// ===========================
// Search Functionality
// ===========================
function initSearch() {
    const searchInputs = document.querySelectorAll('[data-search]');

    searchInputs.forEach(input => {
        const targetSelector = input.getAttribute('data-search');
        const targets = document.querySelectorAll(targetSelector);

        input.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();

            targets.forEach(item => {
                const text = item.textContent.toLowerCase();
                const match = text.includes(query);
                item.style.display = match ? '' : 'none';
            });
        });
    });
}


// ===========================
// Progress Bars Animation
// ===========================
function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.getAttribute('data-progress') || bar.style.width;
                bar.style.width = '0';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
                observer.unobserve(bar);
            }
        });
    }, { threshold: 0.5 });

    progressBars.forEach(bar => {
        observer.observe(bar);
    });
}


// ===========================
// Tooltips
// ===========================
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');

    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', function() {
            const text = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = text;
            tooltip.style.cssText = `
                position: absolute;
                background: var(--gray-800);
                color: white;
                padding: 0.5rem 0.75rem;
                border-radius: 4px;
                font-size: 0.75rem;
                z-index: 1000;
                white-space: nowrap;
            `;

            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + window.scrollY + 'px';

            this._tooltip = tooltip;
        });

        trigger.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
}


// ===========================
// API Calls
// ===========================
const API = {
    async request(endpoint, options = {}) {
        const defaults = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        };

        if (options.body && typeof options.body === 'object') {
            options.body = JSON.stringify(options.body);
        }

        const response = await fetch(endpoint, { ...defaults, ...options });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    },

    get(endpoint) {
        return this.request(endpoint);
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: data
        });
    },

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: data
        });
    },

    delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
};


// ===========================
// Course Enrollment
// ===========================
async function enrollCourse(courseId) {
    try {
        const response = await API.post(`/api/enrollments/`, { course_id: courseId });
        showAlert('success', response.message || 'Successfully enrolled!');
        location.reload();
    } catch (error) {
        showAlert('danger', error.message || 'Failed to enroll');
    }
}


// ===========================
// Mark Lesson Complete
// ===========================
async function markLessonComplete(courseId, lessonId) {
    try {
        const response = await API.post(`/api/progress/${courseId}/lesson/${lessonId}`);
        showAlert('success', 'Lesson completed!');

        // Update UI
        const element = document.querySelector(`[data-lesson-id="${lessonId}"]`);
        if (element) {
            element.classList.add('completed');
        }

        // Update progress bar
        updateCourseProgress(response.course_progress);
    } catch (error) {
        showAlert('danger', error.message || 'Failed to mark lesson complete');
    }
}

function updateCourseProgress(percentage) {
    const progressBar = document.querySelector('.course-progress-bar');
    const progressText = document.querySelector('.course-progress-text');

    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
        progressBar.setAttribute('data-progress', percentage);
    }

    if (progressText) {
        progressText.textContent = `${Math.round(percentage)}% Complete`;
    }
}


// ===========================
// Notifications
// ===========================
async function markNotificationRead(notificationId) {
    try {
        await API.post(`/student/notifications/mark-read/${notificationId}`);

        const element = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (element) {
            element.classList.remove('unread');
        }

        updateNotificationBadge();
    } catch (error) {
        console.error('Failed to mark notification as read:', error);
    }
}

async function markAllNotificationsRead() {
    try {
        await API.post('/student/notifications/mark-all-read');
        document.querySelectorAll('.notification-item').forEach(item => {
            item.classList.remove('unread');
        });
        updateNotificationBadge(0);
        showAlert('success', 'All notifications marked as read');
    } catch (error) {
        showAlert('danger', 'Failed to update notifications');
    }
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        if (count === 0) {
            badge.style.display = 'none';
        } else {
            badge.textContent = count;
            badge.style.display = 'block';
        }
    }
}


// ===========================
// Charts (if using Chart.js)
// ===========================
function initCharts() {
    const enrollmentChart = document.getElementById('enrollmentChart');
    if (enrollmentChart && typeof Chart !== 'undefined') {
        new Chart(enrollmentChart, {
            type: 'line',
            data: {
                labels: window.chartLabels || [],
                datasets: [{
                    label: 'Enrollments',
                    data: window.chartData || [],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    const categoryChart = document.getElementById('categoryChart');
    if (categoryChart && typeof Chart !== 'undefined') {
        new Chart(categoryChart, {
            type: 'doughnut',
            data: {
                labels: window.categoryLabels || [],
                datasets: [{
                    data: window.categoryData || [],
                    backgroundColor: [
                        '#2563eb', '#0891b2', '#059669', '#d97706', '#dc2626'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}


// ===========================
// Table Sorting
// ===========================
function sortTable(table, column, asc = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    const sortedRows = rows.sort((a, b) => {
        const aValue = a.cells[column].textContent.trim();
        const bValue = b.cells[column].textContent.trim();

        // Try numeric comparison
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return asc ? aNum - bNum : bNum - aNum;
        }

        // String comparison
        return asc ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
    });

    // Re-append sorted rows
    sortedRows.forEach(row => tbody.appendChild(row));
}


// ===========================
// Utility Functions
// ===========================
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

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(date, options = {}) {
    const defaults = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-US', { ...defaults, ...options });
}

function timeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);

    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };

    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }

    return 'Just now';
}


// Export functions for global use
window.openModal = openModal;
window.closeModal = closeModal;
window.showAlert = showAlert;
window.enrollCourse = enrollCourse;
window.markLessonComplete = markLessonComplete;
window.markNotificationRead = markNotificationRead;
window.markAllNotificationsRead = markAllNotificationsRead;
window.API = API;
