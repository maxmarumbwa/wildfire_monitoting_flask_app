document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggleButton');
    const bottomSection = document.getElementById('bottomSection');
    const toggleIcon = document.getElementById('toggleIcon');
    const toggleText = document.getElementById('toggleText');
    
    if (toggleButton && bottomSection) {
        toggleButton.addEventListener('click', function() {
            bottomSection.classList.toggle('collapsed');
            
            if (bottomSection.classList.contains('collapsed')) {
                toggleIcon.className = 'fas fa-chevron-down';
                toggleText.textContent = 'Expand Charts';
            } else {
                toggleIcon.className = 'fas fa-chevron-up';
                toggleText.textContent = 'Collapse Charts';
            }
        });
    }
});