<?php
/**
 * JSON API endpoint: returns latest quota + recent history.
 * GET /dashboard/api.php
 */
header('Content-Type: application/json');
header('Cache-Control: no-store');

require_once __DIR__ . '/includes/db.php';
require_once __DIR__ . '/includes/helpers.php';

try {
    $latest  = wq_latest_quota();
    $history = wq_quota_history(200);
    $credits = wq_credit_history(50);

    echo json_encode([
        'ok'      => true,
        'latest'  => $latest,
        'history' => $history,
        'credits' => $credits,
    ]);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => $e->getMessage()]);
}
