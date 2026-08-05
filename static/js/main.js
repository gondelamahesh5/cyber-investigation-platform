$(document).ready(function() {
    // Sidebar toggle
    $("#menu-toggle").click(function(e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
    });

    // Password strength meter
    $('#passwordField').on('input', function() {
        const password = $(this).val();
        const strength = calculatePasswordStrength(password);
        updatePasswordStrength(strength);
    });

    // Password confirmation match
    $('#confirmPasswordField').on('input', function() {
        const password = $('#passwordField').val();
        const confirmPassword = $(this).val();
        
        if (confirmPassword) {
            if (password === confirmPassword) {
                $('#passwordMatch').html('<i class="fas fa-check-circle text-success"></i> Passwords match').removeClass('text-muted').addClass('text-success');
            } else {
                $('#passwordMatch').html('<i class="fas fa-times-circle text-danger"></i> Passwords do not match').removeClass('text-muted').addClass('text-danger');
            }
        } else {
            $('#passwordMatch').html('').removeClass('text-success text-danger');
        }
    });

    // Toggle password visibility
    $('#togglePassword').click(function() {
        const passwordField = $('#passwordField');
        const icon = $(this).find('i');
        
        if (passwordField.attr('type') === 'password') {
            passwordField.attr('type', 'text');
            icon.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            passwordField.attr('type', 'password');
            icon.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });

    // Initialize DataTables
    $('.data-table').DataTable({
        pageLength: 25,
        order: [[0, 'desc']],
        language: {
            search: "",
            searchPlaceholder: "Search..."
        }
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);

    // Confirm delete actions
    $('.btn-delete').click(function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });

    // File size validation
    $('input[type="file"]').change(function() {
        const file = this.files[0];
        if (file && file.size > 50 * 1024 * 1024) {
            alert('File size exceeds 50MB limit');
            this.value = '';
        }
    });

    // Copy to clipboard functionality
    $('.copy-btn').click(function() {
        const text = $(this).data('copy');
        navigator.clipboard.writeText(text).then(function() {
            const btn = $(this);
            const originalHtml = btn.html();
            btn.html('<i class="fas fa-check"></i>');
            setTimeout(function() {
                btn.html(originalHtml);
            }, 2000);
        });
    });

    // Search functionality
    let searchTimer;
    $('#global-search').on('input', function() {
        clearTimeout(searchTimer);
        const query = $(this).val();
        if (query.length < 2) {
            $('#search-results').hide();
            return;
        }
        searchTimer = setTimeout(function() {
            $.get('/api/search', { q: query }, function(data) {
                const results = data.results;
                const container = $('#search-results');
                container.empty();
                if (results.length > 0) {
                    results.forEach(function(r) {
                        container.append(`
                            <a href="#" class="list-group-item list-group-item-action">
                                <small class="text-muted">${r.type}</small>
                                <div><strong>${r.title}</strong></div>
                                <small class="text-muted">${r.subtitle}</small>
                            </a>
                        `);
                    });
                    container.show();
                } else {
                    container.html('<div class="list-group-item text-muted">No results found</div>');
                    container.show();
                }
            });
        }, 300);
    });

    // IOC lookup
    $('#ioc-check-btn').click(function() {
        const value = $('#ioc-check-value').val();
        if (!value) return;
        $.post('/iocs/check', { value: value }, function(data) {
            if (data.found) {
                alert('IOC found: ' + data.ioc.ioc_type + ' - ' + data.ioc.threat_level);
            } else {
                alert('IOC not found in database');
            }
        });
    });

    // Tooltip initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Password strength calculator
function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    
    if (strength <= 2) return 'weak';
    if (strength === 3) return 'fair';
    if (strength === 4) return 'good';
    return 'strong';
}

function updatePasswordStrength(strength) {
    const fill = $('#strengthFill');
    const text = $('#strengthText');
    
    fill.removeClass('weak fair good strong');
    fill.addClass(strength);
    
    const messages = {
        'weak': 'Weak - Add more characters',
        'fair': 'Fair - Add uppercase letters and numbers',
        'good': 'Good - Add special characters',
        'strong': 'Strong - Excellent password!'
    };
    
    text.text(messages[strength]);
}
