async function loadReport() {
    try {
        // Get report name from URL query parameters
        const urlParams = new URLSearchParams(window.location.search);
        const reportName = urlParams.get('report');
        
        if (!reportName) {
            throw new Error('No report name specified in URL');
        }

        // Load data.json to get model information
        const dataResponse = await fetch('data.json');
        if (!dataResponse.ok) {
            throw new Error('Failed to load data.json');
        }
        const data = await dataResponse.json();
        
        // Find the model with matching report
        const model = data.models.find(m => m.report === `reports/${reportName}.json`);
        
        // Load the report
        const reportResponse = await fetch(`reports/${reportName}.json`);
        if (!reportResponse.ok) {
            throw new Error(`Failed to load report: ${reportName}.json`);
        }
        const report = await reportResponse.json();
        
        // Display the report
        displayReport(report, model ? model.name : reportName);
        
    } catch (error) {
        console.error('Error loading report:', error);
        document.getElementById('loading').innerHTML = 
            `<div class="error">Error loading report: ${error.message}</div>`;
    }
}

function displayReport(report, modelName) {
    // Update header
    document.getElementById('model-name').textContent = modelName + ' Report';
    
    // Update stats
    const accuracy = ((1 - report.summary.mean_wer) * 100).toFixed(1);
    document.getElementById('accuracy-stat').textContent = accuracy + '%';
    document.getElementById('wer-stat').textContent = report.summary.mean_wer.toFixed(2);
    document.getElementById('cer-stat').textContent = report.summary.mean_cer.toFixed(2);
    document.getElementById('stress-wer-stat').textContent = report.summary.mean_stress_wer.toFixed(2);
    
    // Hide loading
    document.getElementById('loading').style.display = 'none';
    
    // Display individual sentences
    const container = document.getElementById('sentences-container');
    container.innerHTML = '';
    
    report.individual.forEach((item, index) => {
        const sentenceCard = document.createElement('div');
        sentenceCard.className = 'sentence-card';
        
        // Calculate accuracy for this sentence
        const sentenceAccuracy = ((1 - item.wer) * 100).toFixed(1);
        const accuracyClass = item.wer === 0 ? 'perfect' : (item.wer < 0.5 ? 'good' : 'poor');
        
        // Use sentence field directly
        const sentenceText = item.sentence;
        // Truncate sentence for ID badge display if too long
        const displayId = sentenceText.length > 50 ? sentenceText.substring(0, 47) + '...' : sentenceText;
        
        sentenceCard.innerHTML = `
            <div class="sentence-header">
                <div class="sentence-number">#${index + 1}</div>
                <div class="sentence-id" title="${sentenceText}">${displayId}</div>
                <div class="sentence-accuracy ${accuracyClass}">${sentenceAccuracy}% Accuracy</div>
            </div>
            <div class="sentence-text" dir="rtl">${sentenceText}</div>
            <div class="sentence-metrics">
                <span class="metric-badge">WER: ${item.wer.toFixed(2)}</span>
                <span class="metric-badge">CER: ${item.cer.toFixed(2)}</span>
                <span class="metric-badge">Stress WER: ${item.stress_wer.toFixed(2)}</span>
            </div>
            <div class="phonemes-container">
                <div class="phoneme-row">
                    <div class="phoneme-label">Ground Truth:</div>
                    <div class="phoneme-value gt">${item.gt_phonemes}</div>
                </div>
                <div class="phoneme-row">
                    <div class="phoneme-label">Prediction:</div>
                    <div class="phoneme-value pred">${item.pred_phonemes}</div>
                </div>
            </div>
        `;
        
        container.appendChild(sentenceCard);
    });
}

// Load report when page loads
document.addEventListener('DOMContentLoaded', loadReport);

