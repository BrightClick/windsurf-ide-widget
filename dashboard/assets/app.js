/* Renders the quota history chart from inline JSON, then auto-refreshes via api.php. */
(function () {
    const dataEl = document.getElementById('quota-history-data');
    if (!dataEl) return;

    const initial = JSON.parse(dataEl.textContent || '{}');
    const ctx = document.getElementById('quotaChart');
    if (!ctx) return;

    // Format timestamp labels for chart x-axis.
    const fmt = (iso) => {
        if (!iso) return '';
        const d = new Date(iso);
        return isNaN(d) ? iso : d.toLocaleString();
    };

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: (initial.labels || []).map(fmt),
            datasets: [
                {
                    label: 'Daily %',
                    data: initial.daily || [],
                    borderColor: '#4f8cff',
                    backgroundColor: 'rgba(79,140,255,0.15)',
                    tension: 0.25,
                    spanGaps: true,
                },
                {
                    label: 'Weekly %',
                    data: initial.weekly || [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46,204,113,0.15)',
                    tension: 0.25,
                    spanGaps: true,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 0, max: 100, ticks: { color: '#8b95a7' }, grid: { color: '#262c38' } },
                x: { ticks: { color: '#8b95a7', maxTicksLimit: 8 }, grid: { color: '#262c38' } },
            },
            plugins: {
                legend: { labels: { color: '#e6e9ef' } },
            },
        },
    });

    // Periodic refresh from JSON API every 60s.
    async function refresh() {
        try {
            const res = await fetch('/dashboard/api.php', { cache: 'no-store' });
            const json = await res.json();
            if (!json.ok) return;
            const labels = (json.history || []).map((r) => fmt(r.timestamp));
            const parse = (s) => {
                if (!s) return null;
                const m = String(s).match(/([\d.]+)\s*%/);
                return m ? parseFloat(m[1]) : null;
            };
            chart.data.labels = labels;
            chart.data.datasets[0].data = json.history.map((r) => parse(r.daily_quota));
            chart.data.datasets[1].data = json.history.map((r) => parse(r.weekly_quota));
            chart.update();
            const ts = document.getElementById('last-updated');
            if (ts && json.latest && json.latest.timestamp) {
                ts.textContent = new Date(json.latest.timestamp).toLocaleString();
            }
        } catch (e) {
            // silent fail; chart stays as-is
        }
    }

    setInterval(refresh, 60_000);
})();
