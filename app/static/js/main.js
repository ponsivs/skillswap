// SkillSwap Global JavaScript Utilities

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons if available
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });

    // Password visibility toggle helpers
    const passwordToggles = document.querySelectorAll('.password-toggle-btn');
    passwordToggles.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input) {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                const icon = btn.querySelector('i');
                if (icon) {
                    icon.setAttribute('data-lucide', type === 'password' ? 'eye' : 'eye-off');
                    if (window.lucide) window.lucide.createIcons();
                }
            }
        });
    });
});
