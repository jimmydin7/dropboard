particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: ['#00ff88', '#4ecdc4', '#ffe66d', '#a8e6cf', '#ff8b94', '#00d4ff'] },
                shape: { type: 'circle' },
                opacity: { value: 0.5, random: false },
                size: { value: 3, random: true },
                line_linked: { enable: true, distance: 150, color: '#ffffff', opacity: 0.1, width: 1 },
                move: { enable: true, speed: 2, direction: 'none', random: false, straight: false, out_mode: 'out', bounce: false }
            },
            interactivity: {
                detect_on: 'canvas',
                events: { onhover: { enable: true, mode: 'repulse' }, onclick: { enable: true, mode: 'push' }, resize: true },
                modes: { grab: { distance: 400, line_linked: { opacity: 1 } }, bubble: { distance: 400, size: 40, duration: 2, opacity: 8, speed: 3 }, repulse: { distance: 200, duration: 0.4 }, push: { particles_nb: 4 }, remove: { particles_nb: 2 } }
            },
            retina_detect: true
        });

document.addEventListener('DOMContentLoaded', function() {
    const pollToggle = document.getElementById('poll-toggle');
    const pollSection = document.getElementById('poll-section');
    const addOptionBtn = document.getElementById('add-option');
    const optionsContainer = document.getElementById('poll-options');
    
    if (pollToggle) {
        pollToggle.addEventListener('change', function() {
            if (this.checked) {
                pollSection.classList.remove('hidden');
            } else {
                pollSection.classList.add('hidden');
            }
        });
    }
    
    if (addOptionBtn) {
        addOptionBtn.addEventListener('click', function() {
            const optionCount = optionsContainer.children.length;
            if (optionCount >= 6) return;
            
            const optionDiv = document.createElement('div');
            optionDiv.className = 'flex items-center space-x-2 mb-2';
            optionDiv.innerHTML = `
                <input type="text" name="poll_options[]" placeholder="Option ${optionCount + 1}" 
                       class="flex-1 bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white" required>
                <button type="button" class="remove-option text-red-400 hover:text-red-300">×</button>
            `;
            
            optionsContainer.appendChild(optionDiv);
            
            optionDiv.querySelector('.remove-option').addEventListener('click', function() {
                optionDiv.remove();
            });
        });
    }
    
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-option')) {
            e.target.parentElement.remove();
        }
    });
});

