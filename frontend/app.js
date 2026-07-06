document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('triage-form');
    const inputSection = document.getElementById('input-section');
    const processingSection = document.getElementById('processing-section');
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');
    const resetBtn = document.getElementById('reset-btn');

    function switchSection(toShow) {
        // First fade out everything
        [inputSection, processingSection, resultSection].forEach(sec => {
            sec.classList.remove('active');
        });

        // After fade out transition (500ms), hide them and show the new one
        setTimeout(() => {
            [inputSection, processingSection, resultSection].forEach(sec => {
                if (sec !== toShow) sec.style.display = 'none';
            });
            
            toShow.style.display = 'flex';
            
            // Allow display block to render before triggering opacity transition
            requestAnimationFrame(() => {
                toShow.classList.add('active');
            });
        }, 500);
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const description = document.getElementById('situation').value.trim();
        if (!description) return;

        // Transition to Processing state
        switchSection(processingSection);

        try {
            const response = await fetch('/api/triage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description })
            });

            if (!response.ok) {
                throw new Error('Server error during processing');
            }

            const data = await response.json();
            
            // Render Result using marked.js to convert Markdown to HTML
            resultContent.innerHTML = marked.parse(data.result);
            switchSection(resultSection);

        } catch (error) {
            console.error('Error:', error);
            resultContent.textContent = 'An error occurred while analyzing your case. Please try again.';
            switchSection(resultSection);
        }
    });

    resetBtn.addEventListener('click', () => {
        document.getElementById('situation').value = '';
        switchSection(inputSection);
    });
});
