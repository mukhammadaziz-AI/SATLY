document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initDAUChart();
    initTestsChart();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize sidebar toggle for mobile
    initMobileMenu();
    
    // Add active class to current nav item
    setActiveNavItem();
    
    // Initialize any other interactive elements
    initInteractiveElements();
});

// Initialize Daily Active Users Chart
function initDAUChart() {
    const ctx = document.getElementById('dauCanvas').getContext('2d');
    
    // Sample data - in a real app, this would come from your API
    const data = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Daily Active Users',
            data: [2700, 2900, 3000, 3200, 3600, 3300, 3000],
            backgroundColor: 'rgba(78, 115, 223, 0.05)',
            borderColor: 'rgba(78, 115, 223, 1)',
            pointBackgroundColor: 'rgba(78, 115, 223, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(78, 115, 223, 1)',
            pointRadius: 4,
            pointHoverRadius: 6,
            pointHitRadius: 10,
            pointBorderWidth: 2,
            borderWidth: 2,
            tension: 0.3,
            fill: true
        }]
    };
    
    const config = {
        type: 'line',
        data: data,
        options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: '600',
                        family: "'Poppins', sans-serif"
                    },
                    bodyFont: {
                        size: 13,
                        family: "'Poppins', sans-serif"
                    },
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return 'Users: ' + context.raw.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "'Poppins', sans-serif"
                        },
                        color: '#858796'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "'Poppins', sans-serif"
                        },
                        color: '#858796',
                        callback: function(value) {
                            return value === 0 ? '0' : value / 1000 + 'k';
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };
    
    new Chart(ctx, config);
}

// Initialize Tests Completed Chart
function initTestsChart() {
    const ctx = document.getElementById('testsCanvas').getContext('2d');
    
    // Sample data - in a real app, this would come from your API
    const data = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Tests Completed',
            data: [700, 850, 750, 900, 1000, 850, 950],
            backgroundColor: 'rgba(28, 200, 138, 0.1)',
            borderColor: 'rgba(28, 200, 138, 1)',
            pointBackgroundColor: 'rgba(28, 200, 138, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(28, 200, 138, 1)',
            pointRadius: 4,
            pointHoverRadius: 6,
            pointHitRadius: 10,
            pointBorderWidth: 2,
            borderWidth: 2,
            barPercentage: 0.7,
            categoryPercentage: 0.7
        }]
    };
    
    const config = {
        type: 'bar',
        data: data,
        options: {
            maintainAspectRatio: false,
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: '600',
                        family: "'Poppins', sans-serif"
                    },
                    bodyFont: {
                        size: 13,
                        family: "'Poppins', sans-serif"
                    },
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return 'Tests: ' + context.raw.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "'Poppins', sans-serif"
                        },
                        color: '#858796'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "'Poppins', sans-serif"
                        },
                        color: '#858796',
                        stepSize: 300
                    }
                }
            }
        }
    };
    
    new Chart(ctx, config);
}

// Initialize tooltips
function initTooltips() {
    // This would be implemented with a tooltip library in a real app
    // For now, we'll just log a message
    console.log('Tooltips initialized');
}

// Initialize mobile menu toggle
function initMobileMenu() {
    // This would be implemented to toggle the sidebar on mobile
    // For now, we'll just log a message
    console.log('Mobile menu initialized');
}

// Set active navigation item based on current URL
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.parentElement.classList.add('active');
        } else {
            link.parentElement.classList.remove('active');
        }
    });
}

// Initialize interactive elements
function initInteractiveElements() {
    // Add click event listeners to table rows for expansion
    const tableRows = document.querySelectorAll('.data-table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking on a button or link
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A') {
                return;
            }
            
            // Toggle active class for the row
            this.classList.toggle('active');
            
            // In a real app, you might fetch and display more details here
            console.log('Row clicked:', this);
        });
    });
    
    // Add event listeners for filter buttons
    const filterButtons = document.querySelectorAll('.chart-filter');
    
    filterButtons.forEach(button => {
        button.addEventListener('change', function() {
            // In a real app, this would update the chart data
            console.log('Filter changed to:', this.value);
        });
    });
}

// Helper function to format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Export functions for use in other modules if needed
window.SATLYAdmin = {
    initDAUChart,
    initTestsChart,
    formatNumber
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize navigation
    setupNavigation();
    
    // Set default active page
    showPage('dashboard-content');
    
    // Initialize charts
    initDAUChart();
    initTestsChart();
    
    // Initialize other interactive elements
    initInteractiveElements();
});

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(navLink => {
                navLink.parentElement.classList.remove('active');
            });
            
            // Add active class to clicked link
            this.parentElement.classList.add('active');
            
            // Show the corresponding page
            const pageId = this.getAttribute('data-page') || 'dashboard-content';
            showPage(pageId);
        });
    });
}

function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.content').forEach(page => {
        page.style.display = 'none';
    });
    
    // Show the selected page
    const activePage = document.getElementById(pageId);
    if (activePage) {
        activePage.style.display = 'block';
    }
}

function initDAUChart() {
    const ctx = document.getElementById('dauChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Daily Active Users',
                data: [2700, 2900, 3000, 3200, 3600, 3300, 3000],
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                tension: 0.3,
                fill: true
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
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function initTestsChart() {
    const ctx = document.getElementById('testsChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Tests Completed',
                data: [700, 850, 750, 900, 1000, 850, 950],
                backgroundColor: '#1cc88a',
                borderRadius: 4
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
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function initInteractiveElements() {
    // Add click event to filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // Add your filter logic here
        });
    });
    
    // Add click event to test cards
    document.querySelectorAll('.test-card').forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.test-actions')) {
                // Navigate to test details or open a modal
                console.log('View test:', this.querySelector('h3').textContent);
            }
        });
    });
}