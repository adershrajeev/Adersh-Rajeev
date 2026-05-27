/**
 * ============================================================
 *   MAIN JAVASCRIPT - Mobile Price Prediction System
 * ============================================================
 *   Handles:
 *     - Dark/Light theme toggle with persistence
 *     - Loading overlay for form submission
 *     - Prediction history modal
 *     - PDF export of results
 *     - Dashboard chart rendering (Chart.js)
 *     - CSV upload interaction
 *     - Smooth scroll & animations
 * ============================================================
 */

// =========================================================
//  1. THEME TOGGLE (Dark / Light Mode)
// =========================================================

/**
 * Initialize theme from localStorage or system preference.
 * Called immediately when the script loads.
 */
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
        // Check system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
    updateThemeIcon();
}

/**
 * Toggle between dark and light modes.
 */
function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon();
}

/**
 * Update the theme toggle button icon.
 */
function updateThemeIcon() {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    btn.innerHTML = isDark
        ? '<i class="fas fa-sun"></i> Light'
        : '<i class="fas fa-moon"></i> Dark';
}

// Initialize theme immediately
initTheme();


// =========================================================
//  2. LOADING OVERLAY
// =========================================================

/**
 * Show a full-screen loading overlay while the form submits.
 * Called when the prediction form is submitted.
 */
function showLoader() {
    const overlay = document.getElementById('loaderOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
    // Allow form to submit (return true)
    return true;
}

/**
 * Hide the loading overlay.
 */
function hideLoader() {
    const overlay = document.getElementById('loaderOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}


// =========================================================
//  3. PREDICTION HISTORY
// =========================================================

/**
 * Fetch prediction history from the backend and display in modal.
 */
async function loadHistory() {
    const container = document.getElementById('historyContainer');
    if (!container) return;

    container.innerHTML = '<div class="text-center py-3"><div class="loader-spinner mx-auto" style="width:30px;height:30px;border-width:3px;"></div></div>';

    try {
        const response = await fetch('/api/history');
        const history = await response.json();

        if (history.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-history" style="font-size:2rem;color:var(--text-muted);"></i>
                    <p class="text-muted-custom mt-2">No predictions yet. Try making a prediction first!</p>
                </div>`;
            return;
        }

        let html = '';
        history.forEach((item, index) => {
            // Pick CSS class based on category
            const catClass = getCategoryClass(item.category);
            html += `
                <div class="history-item fade-in-up" style="animation-delay:${index * 0.05}s">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="history-category ${catClass}">${item.category}</span>
                            <br>
                            <span class="history-time">${item.timestamp}</span>
                        </div>
                        <div class="text-end">
                            <span class="history-confidence">${item.confidence}%</span>
                            <br>
                            <small class="text-muted-custom">${item.price_range}</small>
                        </div>
                    </div>
                </div>`;
        });
        container.innerHTML = html;

    } catch (err) {
        container.innerHTML = '<p class="text-danger text-center">Failed to load history.</p>';
        console.error('History load error:', err);
    }
}

/**
 * Map category name to CSS class for coloring.
 */
function getCategoryClass(category) {
    const map = {
        'Budget Phone': 'cat-budget',
        'Mid-Range Phone': 'cat-midrange',
        'Premium Phone': 'cat-premium',
        'Flagship Phone': 'cat-flagship'
    };
    return map[category] || '';
}


// =========================================================
//  4. PDF EXPORT (Result Page)
// =========================================================

/**
 * Export the prediction result card as a PDF.
 * Uses html2pdf.js library (loaded from CDN).
 */
function exportPDF() {
    const element = document.getElementById('resultExportArea');
    if (!element) {
        alert('Nothing to export.');
        return;
    }

    // Options for html2pdf
    const opt = {
        margin:       0.5,
        filename:     'mobile_price_prediction.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'in', format: 'a4', orientation: 'portrait' }
    };

    // Check if html2pdf is loaded
    if (typeof html2pdf === 'undefined') {
        alert('PDF library is loading. Please try again in a moment.');
        return;
    }

    html2pdf().set(opt).from(element).save();
}


// =========================================================
//  5. CONFIDENCE RING ANIMATION (Result Page)
// =========================================================

/**
 * Animate the confidence ring SVG on the result page.
 * Called after the result page loads.
 */
function animateConfidenceRing(confidence) {
    const circle = document.getElementById('progressCircle');
    if (!circle) return;

    // Calculate the stroke offset
    // Circle circumference = 2 * π * r = 2 * 3.14159 * 70 ≈ 440
    const circumference = 440;
    const offset = circumference - (confidence / 100) * circumference;

    // Trigger animation after a small delay
    setTimeout(() => {
        circle.style.strokeDashoffset = offset;
    }, 300);
}


// =========================================================
//  6. DASHBOARD CHARTS (Chart.js)
// =========================================================

/**
 * Fetch analysis data from backend and render all charts.
 * Called when dashboard.html loads.
 */
async function loadDashboardCharts() {
    try {
        const response = await fetch('/api/analysis');
        const data = await response.json();

        if (data.error) {
            console.error('Analysis error:', data.error);
            return;
        }

        renderPieChart(data.category_distribution);
        renderBarChart(data.avg_by_category);
        renderCorrelationChart(data.correlation);
        renderFeatureComparison(data.avg_by_category);
        updateSummaryStats(data.summary);

    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

/**
 * Render a pie/doughnut chart of price category distribution.
 */
function renderPieChart(catDist) {
    const ctx = document.getElementById('pieChart');
    if (!ctx) return;

    const labels = Object.keys(catDist);
    const values = Object.values(catDist);
    const colors = ['#10b981', '#3b82f6', '#a855f7', '#f59e0b'];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 0,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        pointStyleWidth: 10,
                        font: { size: 12, family: 'Inter' },
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
                    }
                }
            }
        }
    });
}

/**
 * Render a grouped bar chart of average feature values per category.
 */
function renderBarChart(avgByCat) {
    const ctx = document.getElementById('barChart');
    if (!ctx) return;

    const categories = Object.keys(avgByCat);
    const features = ['ram', 'rear_camera_mp', 'front_camera_mp', 'processor_speed'];
    const featureLabels = ['RAM (GB)', 'Rear Camera (MP)', 'Front Camera (MP)', 'Processor (GHz)'];
    const colors = ['#6c63ff', '#10b981', '#a855f7', '#3b82f6'];

    const datasets = features.map((feat, i) => ({
        label: featureLabels[i],
        data: categories.map(cat => avgByCat[cat][feat]),
        backgroundColor: colors[i],
        borderRadius: 6,
        barPercentage: 0.7
    }));

    new Chart(ctx, {
        type: 'bar',
        data: { labels: categories, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                        font: { size: 11, family: 'Inter' },
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { size: 10 },
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim()
                    }
                },
                y: {
                    grid: { color: 'rgba(128,128,128,0.1)' },
                    ticks: {
                        font: { size: 10 },
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim()
                    }
                }
            }
        }
    });
}

/**
 * Render a heatmap-style chart for the correlation matrix.
 * Since Chart.js doesn't have a native heatmap, we use a custom canvas approach.
 */
function renderCorrelationChart(corrData) {
    const canvas = document.getElementById('heatmapChart');
    if (!canvas) return;

    const features = Object.keys(corrData);
    const n = features.length;
    const ctx = canvas.getContext('2d');

    // Set canvas size
    const cellSize = Math.min(40, (canvas.parentElement.clientWidth - 120) / n);
    const offsetX = 100;
    const offsetY = 20;
    canvas.width = offsetX + n * cellSize + 20;
    canvas.height = offsetY + n * cellSize + 100;

    // Draw cells
    features.forEach((feat1, i) => {
        features.forEach((feat2, j) => {
            const val = corrData[feat1][feat2];
            ctx.fillStyle = getCorrelationColor(val);
            ctx.fillRect(offsetX + j * cellSize, offsetY + i * cellSize, cellSize - 1, cellSize - 1);

            // Draw value text
            if (cellSize > 25) {
                ctx.fillStyle = Math.abs(val) > 0.5 ? '#fff' : getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim();
                ctx.font = `${Math.max(8, cellSize * 0.25)}px Inter`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(val.toFixed(1), offsetX + j * cellSize + cellSize / 2, offsetY + i * cellSize + cellSize / 2);
            }
        });

        // Row labels
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim();
        ctx.font = '9px Inter';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        const shortLabel = features[i].replace('_', '\n').substring(0, 12);
        ctx.fillText(shortLabel, offsetX - 5, offsetY + i * cellSize + cellSize / 2);
    });

    // Column labels (rotated)
    ctx.save();
    features.forEach((feat, j) => {
        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim();
        ctx.font = '9px Inter';
        ctx.save();
        ctx.translate(offsetX + j * cellSize + cellSize / 2, offsetY + n * cellSize + 8);
        ctx.rotate(Math.PI / 4);
        ctx.textAlign = 'left';
        ctx.fillText(feat.substring(0, 12), 0, 0);
        ctx.restore();
    });
    ctx.restore();
}

/**
 * Map correlation value (-1 to 1) to a color.
 */
function getCorrelationColor(val) {
    if (val >= 0.7) return '#6c63ff';
    if (val >= 0.4) return '#8b7cff';
    if (val >= 0.2) return '#b0a8ff';
    if (val >= 0) return '#d8d4ff';
    if (val >= -0.2) return '#ffd4d4';
    if (val >= -0.4) return '#ffb0b0';
    return '#ff8080';
}

/**
 * Render a radar-style comparison chart showing feature comparison.
 */
function renderFeatureComparison(avgByCat) {
    const ctx = document.getElementById('radarChart');
    if (!ctx) return;

    const categories = Object.keys(avgByCat);
    const features = ['ram', 'battery_power', 'storage', 'rear_camera_mp', 'front_camera_mp', 'processor_speed', 'refresh_rate'];
    const featureLabels = ['RAM', 'Battery', 'Storage', 'Rear Camera', 'Front Camera', 'Processor', 'Refresh Rate'];
    const colors = [
        { bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981' },
        { bg: 'rgba(59, 130, 246, 0.15)', border: '#3b82f6' },
        { bg: 'rgba(168, 85, 247, 0.15)', border: '#a855f7' },
        { bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b' }
    ];

    // Normalize values (0-100 scale)
    const maxVals = {};
    features.forEach(f => {
        maxVals[f] = Math.max(...categories.map(c => avgByCat[c][f]));
    });

    const datasets = categories.map((cat, i) => ({
        label: cat,
        data: features.map(f => ((avgByCat[cat][f] / maxVals[f]) * 100).toFixed(1)),
        backgroundColor: colors[i].bg,
        borderColor: colors[i].border,
        borderWidth: 2,
        pointBackgroundColor: colors[i].border,
        pointRadius: 3
    }));

    new Chart(ctx, {
        type: 'radar',
        data: { labels: featureLabels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                        font: { size: 10, family: 'Inter' },
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
                    }
                }
            },
            scales: {
                r: {
                    grid: { color: 'rgba(128,128,128,0.15)' },
                    angleLines: { color: 'rgba(128,128,128,0.1)' },
                    ticks: { display: false },
                    pointLabels: {
                        font: { size: 10, family: 'Inter' },
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
                    }
                }
            }
        }
    });
}

/**
 * Update the summary statistics cards on the dashboard.
 */
function updateSummaryStats(summary) {
    const el = (id) => document.getElementById(id);
    if (el('statTotal')) el('statTotal').textContent = summary.total_records.toLocaleString();
    if (el('statFeatures')) el('statFeatures').textContent = summary.num_features;
    if (el('statCategories')) el('statCategories').textContent = summary.categories.length;
}


// =========================================================
//  7. CSV UPLOAD INTERACTION
// =========================================================

/**
 * Handle drag & drop and click-to-upload for the CSV upload area.
 */
function initUploadArea() {
    const area = document.getElementById('uploadArea');
    const input = document.getElementById('csvFileInput');
    if (!area || !input) return;

    // Click to upload
    area.addEventListener('click', () => input.click());

    // Drag and drop
    area.addEventListener('dragover', (e) => {
        e.preventDefault();
        area.style.borderColor = 'var(--accent-1)';
        area.style.background = 'rgba(108, 99, 255, 0.08)';
    });

    area.addEventListener('dragleave', () => {
        area.style.borderColor = 'var(--border-color)';
        area.style.background = '';
    });

    area.addEventListener('drop', (e) => {
        e.preventDefault();
        area.style.borderColor = 'var(--border-color)';
        area.style.background = '';
        if (e.dataTransfer.files.length > 0) {
            input.files = e.dataTransfer.files;
            document.getElementById('uploadForm').submit();
        }
    });

    // File selection
    input.addEventListener('change', () => {
        if (input.files.length > 0) {
            document.getElementById('uploadForm').submit();
        }
    });
}


// =========================================================
//  8. TOOLTIP INITIALIZATION
// =========================================================

/**
 * Initialize Bootstrap tooltips on all elements with data-bs-toggle="tooltip".
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
}


// =========================================================
//  9. AUTO-DISMISS FLASH ALERTS
// =========================================================

function initAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000); // Auto-dismiss after 5 seconds
    });
}


// =========================================================
//  10. DOM READY - Initialize everything
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
    initTooltips();
    initAlerts();
    initUploadArea();

    // If on result page, animate confidence ring
    const confEl = document.getElementById('confidenceValue');
    if (confEl) {
        const confidence = parseFloat(confEl.dataset.confidence || 0);
        animateConfidenceRing(confidence);
    }

    // If on dashboard page, load charts
    if (document.getElementById('pieChart')) {
        loadDashboardCharts();
    }
});
