async function loadData() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error('Failed to load data.json');
        }
        const data = await response.json();
        
        // Fetch report data for each model
        const modelsWithMetrics = await Promise.all(
            data.models.map(async (model) => {
                try {
                    const reportResponse = await fetch(model.report);
                    if (!reportResponse.ok) {
                        throw new Error(`Failed to load report for ${model.name}`);
                    }
                    const report = await reportResponse.json();
                    
                    // Extract report name from path (e.g., "reports/goruut.json" -> "goruut")
                    const reportName = model.report.replace('reports/', '').replace('.json', '');
                    
                    // Extract metrics from report summary
                    return {
                        name: model.name,
                        url: model.url,
                        reportName: reportName,
                        reportAvailable: true,
                        wer: report.summary.mean_wer,
                        cer: report.summary.mean_cer,
                        stress_wer: report.summary.mean_stress_wer,
                        num_samples: report.summary.num_samples
                    };
                } catch (error) {
                    console.error(`Error loading report for ${model.name}:`, error);
                    const reportName = model.report.replace('reports/', '').replace('.json', '');
                    return {
                        name: model.name,
                        url: model.url,
                        reportName: reportName,
                        reportAvailable: false,
                        wer: null,
                        cer: null,
                        stress_wer: null,
                        num_samples: null
                    };
                }
            })
        );

        if (modelsWithMetrics.length === 0) {
            throw new Error('No models loaded');
        }

        displayResults({ models: modelsWithMetrics });
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('loading').innerHTML =
            '<div class="error">Error loading data. Please make sure data.json exists.</div>';
    }
}

function displayResults(data) {
    const models = data.models;

    // Sort models by WER (ascending). Models without metrics go last.
    models.sort((a, b) => {
        const aHasWer = typeof a.wer === 'number';
        const bHasWer = typeof b.wer === 'number';
        if (aHasWer && bHasWer) return a.wer - b.wer;
        if (aHasWer) return -1;
        if (bHasWer) return 1;
        return a.name.localeCompare(b.name);
    });

    // Add rank to each model
    models.forEach((model, index) => {
        model.rank = index + 1;
    });

    // Update stats
    document.getElementById('total-models').textContent = models.length;
    const scoredModels = models.filter(m => typeof m.wer === 'number');
    document.getElementById('best-wer').textContent = scoredModels.length > 0
        ? ((1 - scoredModels[0].wer) * 100).toFixed(1) + '%'
        : 'N/A';

    // Populate the table
    const tableBody = document.getElementById('table-body');
    tableBody.innerHTML = '';

    models.forEach(model => {
        const row = document.createElement('tr');
        row.className = model.rank === 1 ? 'best-model-row' : '';

        // Calculate accuracy as percentage (1 - WER)
        const hasMetrics = typeof model.wer === 'number' && typeof model.cer === 'number';
        const accuracy = hasMetrics ? ((1 - model.wer) * 100).toFixed(1) : 'N/A';

        const modelNameCell = model.url
            ? `<a href="${model.url}" target="_blank">${model.name}</a>`
            : model.name;

        const stressWer = typeof model.stress_wer === 'number' ? model.stress_wer.toFixed(2) : 'N/A';
        const reportCell = model.reportAvailable
            ? `<a href="report.html?report=${model.reportName}">View Details</a>`
            : 'Pending';

        row.innerHTML = `
            <td class="rank">${model.rank}</td>
            <td class="model-name">${modelNameCell}</td>
            <td class="metric">${hasMetrics ? `${accuracy}%` : 'N/A'}</td>
            <td class="metric">${hasMetrics ? model.wer.toFixed(2) : 'N/A'}</td>
            <td class="metric">${hasMetrics ? model.cer.toFixed(2) : 'N/A'}</td>
            <td class="metric">${stressWer}</td>
            <td class="report-link">${reportCell}</td>
        `;

        tableBody.appendChild(row);
    });

    // Display scatter plot with models that have metrics
    displayScatterPlot(scoredModels);
}

function displayScatterPlot(models) {
    if (models.length === 0) {
        document.getElementById('loading').style.display = 'none';
        return;
    }
    // Create trace
    const trace = {
        x: models.map(m => m.wer),
        y: models.map(m => m.cer),
        text: models.map(m => m.name),
        mode: 'markers+text',
        type: 'scatter',
        marker: {
            color: models.map((m, i) => i === 0 ? '#22c55e' : '#3182ce'),
            size: models.map((m, i) => i === 0 ? 20 : 15),
            line: {
                color: models.map((m, i) => i === 0 ? '#16a34a' : '#2b6cb0'),
                width: 2
            }
        },
        textposition: 'top center',
        textfont: {
            size: 12,
            color: '#2d3748'
        },
        hovertemplate: '<b>%{text}</b><br>' +
                      'WER: %{x:.2f}<br>' +
                      'CER: %{y:.2f}<br>' +
                      '<extra></extra>'
    };

    // Calculate axis ranges with padding
    const allWER = models.map(m => m.wer);
    const allCER = models.map(m => m.cer);
    const werRange = Math.max(...allWER) - Math.min(...allWER);
    const cerRange = Math.max(...allCER) - Math.min(...allCER);

    const layout = {
        title: {
            text: 'G2P Model Performance: WER vs CER',
            font: { size: 20, color: '#2d3748' }
        },
        xaxis: {
            title: 'Word Error Rate (WER)',
            titlefont: { size: 14 },
            range: [
                Math.max(0, Math.min(...allWER) - werRange * 0.3),
                Math.max(...allWER) + werRange * 0.3
            ],
            gridcolor: '#e2e8f0',
            zerolinecolor: '#cbd5e0'
        },
        yaxis: {
            title: 'Character Error Rate (CER)',
            titlefont: { size: 14 },
            range: [
                Math.max(0, Math.min(...allCER) - cerRange * 0.3),
                Math.max(...allCER) + cerRange * 0.3
            ],
            gridcolor: '#e2e8f0',
            zerolinecolor: '#cbd5e0'
        },
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#ffffff',
        font: { family: 'Arial, sans-serif' },
        hovermode: 'closest',
        margin: { t: 60, r: 40, b: 60, l: 60 },
        showlegend: false
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false
    };

    // Hide loading message
    document.getElementById('loading').style.display = 'none';

    // Create the plot
    Plotly.newPlot('scatter-plot', [trace], layout, config);
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', loadData);
