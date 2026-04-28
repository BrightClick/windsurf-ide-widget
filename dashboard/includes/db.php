<?php
/**
 * SQLite connection and query helpers for the Windsurf quota dashboard.
 */

/**
 * Returns a PDO connection to the project SQLite database.
 */
function wq_db(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        $dbPath = realpath(__DIR__ . '/../../windsurf_quota.db');
        if ($dbPath === false) {
            throw new RuntimeException('windsurf_quota.db not found at project root');
        }
        $pdo = new PDO('sqlite:' . $dbPath);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ATTR_ERRMODE);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    }
    return $pdo;
}

/**
 * Latest quota row (most recent sync).
 */
function wq_latest_quota(): ?array {
    $stmt = wq_db()->query(
        'SELECT timestamp, daily_quota, weekly_quota, extra_balance
         FROM quota_history
         ORDER BY id DESC LIMIT 1'
    );
    $row = $stmt->fetch();
    return $row ?: null;
}

/**
 * Quota history rows for charting (oldest -> newest), capped.
 */
function wq_quota_history(int $limit = 200): array {
    $stmt = wq_db()->prepare(
        'SELECT timestamp, daily_quota, weekly_quota, extra_balance
         FROM (SELECT * FROM quota_history ORDER BY id DESC LIMIT :lim)
         ORDER BY id ASC'
    );
    $stmt->bindValue(':lim', $limit, PDO::PARAM_INT);
    $stmt->execute();
    return $stmt->fetchAll();
}

/**
 * Latest credit history entries (deduped by description+amount+date).
 */
function wq_credit_history(int $limit = 50): array {
    $stmt = wq_db()->prepare(
        'SELECT description, amount, date, MAX(fetched_at) AS fetched_at
         FROM credit_history
         GROUP BY description, amount, date
         ORDER BY MAX(id) DESC
         LIMIT :lim'
    );
    $stmt->bindValue(':lim', $limit, PDO::PARAM_INT);
    $stmt->execute();
    return $stmt->fetchAll();
}
