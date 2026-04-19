async function loadData() {
    try {
        const response = await fetch('data/metadata.json');
        if (!response.ok) throw new Error('Failed to load data/metadata.json');
        const data = await response.json();
        if (!data.models || data.models.length === 0) throw new Error('No models in metadata.json');
        displayResults(data.models);
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('loading').innerHTML =
            '<div class="error">Error loading data. Please make sure data/metadata.json exists.</div>';
    }
}

function displayResults(models) {
    models.sort((a, b) => a.wer - b.wer);
    models.forEach((model, index) => { model.rank = index + 1; });

    document.getElementById('total-models').textContent = models.length;
    document.getElementById('best-wer').textContent = ((1 - models[0].wer) * 100).toFixed(1) + '%';

    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '';

    models.forEach(model => {
        const row = document.createElement('tr');
        row.className = model.rank === 1 ? 'best-model-row' : '';

        const accuracy = Math.max(0, (1 - model.wer) * 100).toFixed(1);
        const modelNameCell = model.url
            ? `<a href="${model.url}" target="_blank">${model.name}</a>`
            : model.name;
        const stressWer = model.stress_wer !== undefined ? model.stress_wer.toFixed(2) : 'N/A';

        row.innerHTML = `
            <td class="rank">${model.rank}</td>
            <td class="model-name">${modelNameCell}</td>
            <td class="metric">${accuracy}%</td>
            <td class="metric">${model.wer.toFixed(2)}</td>
            <td class="metric">${model.cer.toFixed(2)}</td>
            <td class="metric">${stressWer}</td>
            <td class="report-link"><a href="report.html?model=${model.id}">View Details</a></td>
        `;
        tableBody.appendChild(row);
    });

    displayScatterPlot(models);
}

function displayScatterPlot(models) {
    const trace = {
        x: models.map(m => m.wer),
        y: models.map(m => m.cer),
        text: models.map(m => m.name),
        mode: 'markers+text',
        type: 'scatter',
        marker: {
            color: models.map((m, i) => i === 0 ? '#22c55e' : '#3182ce'),
            size: models.map((m, i) => i === 0 ? 20 : 15),
            line: { color: models.map((m, i) => i === 0 ? '#16a34a' : '#2b6cb0'), width: 2 }
        },
        textposition: 'top center',
        textfont: { size: 12, color: '#2d3748' },
        hovertemplate: '<b>%{text}</b><br>WER: %{x:.2f}<br>CER: %{y:.2f}<br><extra></extra>'
    };

    const allWER = models.map(m => m.wer);
    const allCER = models.map(m => m.cer);
    const werRange = Math.max(...allWER) - Math.min(...allWER);
    const cerRange = Math.max(...allCER) - Math.min(...allCER);

    const layout = {
        title: { text: 'G2P Model Performance: WER vs CER', font: { size: 20, color: '#2d3748' } },
        xaxis: {
            title: 'Word Error Rate (WER)', titlefont: { size: 14 },
            range: [Math.max(0, Math.min(...allWER) - werRange * 0.3), Math.max(...allWER) + werRange * 0.3],
            gridcolor: '#e2e8f0', zerolinecolor: '#cbd5e0'
        },
        yaxis: {
            title: 'Character Error Rate (CER)', titlefont: { size: 14 },
            range: [Math.max(0, Math.min(...allCER) - cerRange * 0.3), Math.max(...allCER) + cerRange * 0.3],
            gridcolor: '#e2e8f0', zerolinecolor: '#cbd5e0'
        },
        plot_bgcolor: '#ffffff', paper_bgcolor: '#ffffff',
        font: { family: 'Arial, sans-serif' },
        hovermode: 'closest', margin: { t: 60, r: 40, b: 60, l: 60 }, showlegend: false
    };

    document.getElementById('loading').style.display = 'none';
    Plotly.newPlot('scatter-plot', [trace], layout, { responsive: true, displaylogo: false });
}

document.addEventListener('DOMContentLoaded', loadData);
