async function loadReport() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const modelId = urlParams.get('model');
        if (!modelId) throw new Error('No model specified in URL');

        const [metaResp, gtResp, predResp] = await Promise.all([
            fetch('data/metadata.json'),
            fetch('data/gt.tsv'),
            fetch(`data/${modelId}.tsv`),
        ]);

        if (!metaResp.ok) throw new Error('Failed to load metadata.json');
        if (!gtResp.ok) throw new Error('Failed to load gt.tsv');
        if (!predResp.ok) throw new Error(`Failed to load ${modelId}.tsv`);

        const meta = await metaResp.json();
        const model = meta.models.find(m => m.id === modelId);
        if (!model) throw new Error(`Model ${modelId} not found in metadata.json`);

        const gtRows = parseTsv(await gtResp.text());
        const predRows = parseTsv(await predResp.text());

        displayReport(model, gtRows, predRows);
    } catch (error) {
        console.error('Error loading report:', error);
        document.getElementById('loading').innerHTML =
            `<div class="error">Error loading report: ${error.message}</div>`;
    }
}

function charDiffHtml(gt, pred) {
    const dmp = new diff_match_patch();
    const diffs = dmp.diff_main(gt, pred);
    dmp.diff_cleanupSemantic(diffs);
    return diffs.map(([op, text]) => {
        if (op === 1)  return `<span class="diff-ins">${text}</span>`;
        if (op === -1) return `<span class="diff-del">${text}</span>`;
        return text;
    }).join('');
}

function parseTsv(text) {
    const lines = text.trim().split('\n');
    // skip header if present
    const start = lines[0].includes('Sentence') ? 1 : 0;
    return lines.slice(start).map(l => l.split('\t'));
}

function displayReport(model, gtRows, predRows) {
    document.getElementById('model-name').textContent = model.name + ' Report';

    const accuracy = Math.max(0, (1 - model.wer) * 100).toFixed(1);
    document.getElementById('accuracy-stat').textContent = accuracy + '%';
    document.getElementById('wer-stat').textContent = model.wer.toFixed(2);
    document.getElementById('cer-stat').textContent = model.cer.toFixed(2);
    document.getElementById('stress-wer-stat').textContent = model.stress_wer.toFixed(2);

    document.getElementById('loading').style.display = 'none';

    const container = document.getElementById('sentences-container');
    container.innerHTML = '';

    gtRows.forEach((row, index) => {
        const [sentence, gtPhonemes] = row;
        const predPhonemes = predRows[index]?.[1] ?? '';
        const wer = model.wers?.[index] ?? 0;
        const cer = model.cers?.[index] ?? 0;

        const sentenceAccuracy = Math.max(0, (1 - wer) * 100).toFixed(1);
        const accuracyClass = wer === 0 ? 'perfect' : (wer < 0.5 ? 'good' : 'poor');

        const card = document.createElement('div');
        card.className = 'sentence-card';
        card.innerHTML = `
            <div class="sentence-header">
                <div class="sentence-number">#${index + 1}</div>
                <div class="sentence-accuracy ${accuracyClass}">${sentenceAccuracy}% Accuracy</div>
            </div>
            <div class="sentence-text" dir="rtl">${sentence}</div>
            <div class="sentence-metrics">
                <span class="metric-badge">WER: ${wer.toFixed(2)}</span>
                <span class="metric-badge">CER: ${cer.toFixed(2)}</span>
            </div>
            <div class="phonemes-container">
                <div class="phoneme-row">
                    <div class="phoneme-label">Ground Truth:</div>
                    <div class="phoneme-value gt">${gtPhonemes}</div>
                </div>
                <div class="phoneme-row">
                    <div class="phoneme-label">Prediction:</div>
                    <div class="phoneme-value pred">${predPhonemes}</div>
                </div>
                <div class="phoneme-row">
                    <div class="phoneme-label">Diff:</div>
                    <div class="phoneme-value diff">${charDiffHtml(gtPhonemes, predPhonemes)}</div>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', loadReport);
