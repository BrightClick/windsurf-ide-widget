<?php
/** Main dashboard view: KPI cards, history chart, credit table. */
require_once __DIR__ . '/../includes/db.php';
require_once __DIR__ . '/../includes/helpers.php';

$latest  = wq_latest_quota();
$history = wq_quota_history(200);
$credits = wq_credit_history(50);

$dailyPct  = wq_parse_percent($latest['daily_quota']  ?? null);
$weeklyPct = wq_parse_percent($latest['weekly_quota'] ?? null);

include __DIR__ . '/../includes/header.php';
?>

<section class="kpis">
    <div class="card kpi <?= wq_e(wq_pct_class($dailyPct)) ?>">
        <div class="label">Daily quota</div>
        <div class="value"><?= $dailyPct !== null ? wq_e($dailyPct) . '%' : '—' ?></div>
        <div class="sub"><?= wq_e($latest['daily_quota'] ?? 'no data') ?></div>
    </div>
    <div class="card kpi <?= wq_e(wq_pct_class($weeklyPct)) ?>">
        <div class="label">Weekly quota</div>
        <div class="value"><?= $weeklyPct !== null ? wq_e($weeklyPct) . '%' : '—' ?></div>
        <div class="sub"><?= wq_e($latest['weekly_quota'] ?? 'no data') ?></div>
    </div>
    <div class="card kpi info">
        <div class="label">Extra balance</div>
        <div class="value"><?= wq_e($latest['extra_balance'] ?? '—') ?></div>
        <div class="sub">live balance</div>
    </div>
</section>

<section class="card chart-card">
    <h2>Quota history</h2>
    <canvas id="quotaChart" height="120"></canvas>
    <script id="quota-history-data" type="application/json"><?php
        $labels = [];
        $daily = [];
        $weekly = [];
        foreach ($history as $row) {
            $labels[] = $row['timestamp'];
            $daily[]  = wq_parse_percent($row['daily_quota']);
            $weekly[] = wq_parse_percent($row['weekly_quota']);
        }
        echo json_encode(['labels' => $labels, 'daily' => $daily, 'weekly' => $weekly]);
    ?></script>
</section>

<section class="card">
    <h2>Credit history</h2>
    <?php if (!$credits): ?>
        <p class="empty">No credit entries recorded yet.</p>
    <?php else: ?>
    <table class="data">
        <thead>
            <tr>
                <th>Description</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Last seen</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($credits as $c): ?>
            <tr>
                <td><?= wq_e($c['description']) ?></td>
                <td><?= wq_e($c['amount']) ?></td>
                <td><?= wq_e($c['date']) ?></td>
                <td><?= wq_e(wq_format_ts($c['fetched_at'])) ?></td>
            </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
    <?php endif; ?>
</section>

<?php include __DIR__ . '/../includes/footer.php'; ?>
