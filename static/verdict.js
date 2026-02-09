/* verdict.js - Verdict display and audio handling */

async function loadVerdict(caseId) {
    const verdictLoading = document.getElementById('verdict-loading');
    const verdictError = document.getElementById('verdict-error');
    const verdictSection = document.getElementById('verdict-section');

    verdictLoading.style.display = 'block';

    try {
        // In a real implementation, we'd fetch the verdict data from the server
        // For now, we'll construct the paths to stored files
        // This is a simplified version - in production, you'd want a proper API endpoint

        // Simulate loading by just showing that we'd fetch it
        // The verdict data would be passed from the Flask response in production
        
        // For now, show a message that explains the limitation
        verdictError.innerHTML = `
            <strong>Note:</strong> The verdict display page would receive analysis results via AJAX.
            In a full implementation, you would see:
            <ul style="margin-top: 10px; margin-left: 20px;">
                <li>Verdict cards with guilty/not guilty status</li>
                <li>Confidence bars and scores</li>
                <li>Audio player for verdict narration (if available)</li>
                <li>LLM-generated defense arguments</li>
                <li>Case timeline and summary</li>
            </ul>
        `;
        verdictError.classList.remove('error');
        verdictError.classList.add('info');
        verdictError.style.display = 'block';

    } catch (error) {
        verdictError.textContent = 'Error loading verdict: ' + error.message;
        verdictError.style.display = 'block';
    } finally {
        verdictLoading.style.display = 'none';
    }
}

function createVerdictCard(verdict) {
    const card = document.createElement('div');
    card.className = `verdict-card ${verdict.verdict.toLowerCase().replace(' ', '-')}`;

    const verdictClass = verdict.verdict.toLowerCase() === 'guilty' ? 'guilty' : 'not-guilty';

    card.innerHTML = `
        <div class="verdict-charge">${verdict.charge}</div>
        <div class="verdict-text ${verdictClass}">${verdict.verdict}</div>
        <div>
            <strong>Recommendation:</strong> ${verdict.recommendation}
        </div>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${verdict.confidence}%"></div>
        </div>
        <div class="confidence-label">Confidence: ${verdict.confidence.toFixed(1)}%</div>
        <div style="margin-top: 15px; font-size: 0.9em; color: #666;">
            <div>Prosecution: ${verdict.prosecution_score.toFixed(3)}</div>
            <div>Defense: ${verdict.defense_score.toFixed(3)}</div>
        </div>
    `;

    return card;
}

function createScoreBreakdown(verdict) {
    const breakdown = document.createElement('div');
    breakdown.className = 'score-row';

    const verdictLabel = `${verdict.charge} - ${verdict.verdict}`;
    const difference = (verdict.prosecution_score - verdict.defense_score).toFixed(3);

    breakdown.innerHTML = `
        <span class="score-label">${verdictLabel}</span>
        <div>
            <span style="color: #666; margin-right: 15px;">Δ ${difference}</span>
            <span class="score-value">${verdict.confidence.toFixed(1)}%</span>
        </div>
    `;

    return breakdown;
}

function createDefenseArgumentCard(arg) {
    const card = document.createElement('div');
    card.className = 'defense-argument';

    card.innerHTML = `
        <div class="defense-arg-name">${arg.name}</div>
        <div class="defense-arg-strength">Strength: ${arg.strength}/10</div>
        <p class="defense-arg-desc">${arg.description}</p>
        ${arg.supporting_facts ? `<p style="margin-top: 10px; font-size: 0.85em; color: #666;"><strong>Supporting Facts:</strong> ${arg.supporting_facts.join(', ')}</p>` : ''}
    `;

    return card;
}

function formatCaseSummary(summary) {
    const container = document.createElement('div');
    container.className = 'summary-content';

    if (summary.events && summary.events.length > 0) {
        const eventsSection = document.createElement('div');
        eventsSection.className = 'summary-subsection';
        eventsSection.innerHTML = '<h4>Timeline of Events</h4>';
        
        const eventList = document.createElement('ul');
        eventList.className = 'summary-list';
        summary.events.forEach(event => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>[${event.time}]</strong> ${event.event}`;
            eventList.appendChild(li);
        });
        eventsSection.appendChild(eventList);
        container.appendChild(eventsSection);
    }

    if (summary.mitigating_factors && summary.mitigating_factors.length > 0) {
        const mitigatingSection = document.createElement('div');
        mitigatingSection.className = 'summary-subsection';
        mitigatingSection.innerHTML = '<h4>Mitigating Factors</h4>';
        
        const factorList = document.createElement('ul');
        factorList.className = 'summary-list';
        summary.mitigating_factors.forEach(factor => {
            const li = document.createElement('li');
            li.textContent = factor;
            factorList.appendChild(li);
        });
        mitigatingSection.appendChild(factorList);
        container.appendChild(mitigatingSection);
    }

    if (summary.aggravating_factors && summary.aggravating_factors.length > 0) {
        const aggravatingSection = document.createElement('div');
        aggravatingSection.className = 'summary-subsection';
        aggravatingSection.innerHTML = '<h4>Aggravating Factors</h4>';
        
        const factorList = document.createElement('ul');
        factorList.className = 'summary-list';
        summary.aggravating_factors.forEach(factor => {
            const li = document.createElement('li');
            li.textContent = factor;
            factorList.appendChild(li);
        });
        aggravatingSection.appendChild(factorList);
        container.appendChild(aggravatingSection);
    }

    return container;
}
