/* Main page script.js for case upload and analysis */

document.addEventListener('DOMContentLoaded', function() {
    const caseForm = document.getElementById('case-form');
    const analyzeBtn = document.getElementById('analyze-btn');
    const thetaInput = document.getElementById('theta');
    const thetaValue = document.getElementById('theta-value');
    const llmWeightInput = document.getElementById('llm-weight');
    const llmValue = document.getElementById('llm-value');
    const errorMessage = document.getElementById('error-message');
    const loadingMessage = document.getElementById('loading-message');
    const btnSpinner = document.getElementById('btn-spinner');
    const btnText = document.querySelector('.btn-text');

    // Update theta display
    if (thetaInput) {
        thetaInput.addEventListener('input', function() {
            thetaValue.textContent = parseFloat(this.value).toFixed(2);
        });
    }

    // Update LLM weight display
    if (llmWeightInput) {
        llmWeightInput.addEventListener('input', function() {
            llmValue.textContent = this.value + '%';
        });
    }

    // Form submission
    if (caseForm) {
        caseForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Hide previous messages
            errorMessage.style.display = 'none';
            loadingMessage.style.display = 'flex';
            analyzeBtn.disabled = true;
            btnSpinner.style.display = 'inline-block';
            btnText.textContent = 'Analyzing...';

            try {
                const formData = new FormData(caseForm);
                
                // Add weights in correct format
                const theta = parseFloat(thetaInput.value);
                const llmWeight = parseInt(llmWeightInput.value) / 100;
                
                formData.set('theta', theta.toString());
                formData.set('llm_weight', llmWeight.toString());

                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    // Redirect to verdict page
                    window.location.href = `/verdict/${result.case_id}`;
                } else {
                    showError(result.error || 'Analysis failed');
                }
            } catch (error) {
                showError('Error: ' + error.message);
            } finally {
                analyzeBtn.disabled = false;
                btnSpinner.style.display = 'none';
                btnText.textContent = 'Analyze Case';
                loadingMessage.style.display = 'none';
            }
        });
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        window.scrollTo(0, 0);
    }

    // File input handler
    const caseFileInput = document.getElementById('case-file');
    const caseTextInput = document.getElementById('case-text');
    
    if (caseFileInput) {
        caseFileInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                const file = this.files[0];
                const reader = new FileReader();
                reader.onload = function(event) {
                    caseTextInput.value = event.target.result;
                };
                reader.readAsText(file);
            }
        });
    }
});
